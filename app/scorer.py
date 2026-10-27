import json
import re
from typing import Any

from app.config import FITMENT_THRESHOLD
from app.llm import complete_json, has_llm
from app.logging_config import get_logger

logger = get_logger("scorer")

SCORE_SYSTEM = """You are an executive-search screening agent.
Score a candidate against a job description from 0 to 100.
Consider:
1) domain relevance and career trajectory
2) skill recency (hands-on in last 24 months vs historical)
3) stability index (average tenure per company; job-hopping lowers score)
Return ONLY JSON:
{
  "fitment_score": 0-100 number,
  "domain_relevance": 0-100,
  "skill_recency": 0-100,
  "stability_index": 0-100,
  "summary_bullets": ["...", "...", "..."]
}
Be calibrated: 85+ is a strong submit, 70-84 is a maybe, below 70 is a no-submit."""


def score_candidate(candidate: dict[str, Any], job: dict[str, Any], threshold: float | None = None) -> dict[str, Any]:
    cutoff = FITMENT_THRESHOLD if threshold is None else threshold
    if has_llm():
        try:
            payload = {
                "candidate": {k: candidate.get(k) for k in [
                    "full_name", "current_location", "total_experience_years",
                    "relevant_experience_years", "current_ctc", "expected_ctc",
                    "notice_period_days", "current_company", "previous_employers",
                    "skills", "certifications", "education",
                ]},
                "job": {"title": job.get("title"), "jd_text": job.get("jd_text")},
            }
            data, engine = complete_json(SCORE_SYSTEM, json.dumps(payload, ensure_ascii=False)[:14000])
            result = _normalize_score(data, cutoff)
            result["engine"] = engine
            _log_score(candidate, job, result)
            return result
        except Exception as exc:
            logger.warning(f"LLM scoring failed for candidate #{candidate.get('id')}: {exc}; using heuristic scoring")
            result = heuristic_score(candidate, job, cutoff)
            result["engine"] = "heuristic-fallback"
            _log_score(candidate, job, result)
            return result
    result = heuristic_score(candidate, job, cutoff)
    result["engine"] = "heuristic"
    _log_score(candidate, job, result)
    return result


def _log_score(candidate: dict[str, Any], job: dict[str, Any], result: dict[str, Any]) -> None:
    logger.info(
        f"Scored candidate #{candidate.get('id')} ('{candidate.get('full_name')}') vs job '{job.get('title')}': "
        f"score={result['fitment_score']}, status='{result['status']}', engine='{result['engine']}'",
        extra={
            "extra_data": {
                "candidate_id": candidate.get("id"),
                "job_id": job.get("id"),
                "fitment_score": result["fitment_score"],
                "status": result["status"],
                "engine": result["engine"],
            }
        },
    )


def heuristic_score(candidate: dict[str, Any], job: dict[str, Any], threshold: float) -> dict[str, Any]:
    jd = (job.get("jd_text") or "").lower()
    skills = str(candidate.get("skills") or "").lower()
    tokens = {t for t in re.findall(r"[a-z0-9+#.]{3,}", jd) if t not in STOP}
    skill_tokens = set(re.findall(r"[a-z0-9+#.]{2,}", skills))
    overlap = len(tokens & skill_tokens)
    domain = min(95.0, 35 + overlap * 6)
    recency = 70.0
    recent_keywords = ["fastapi", "python", "claude", "llm", "naukri", "ceipal", "react", "docker"]
    if any(k in skills for k in recent_keywords):
        recency = 82.0
    years = candidate.get("total_experience_years") or 0
    recency = recency if years >= 3 else recency - 8
    prev = candidate.get("previous_employers") or ""
    employers = [p for p in re.split(r"[,;/]", prev) if p.strip()]
    n_emp = max(len(employers), 1)
    avg_tenure = (years / n_emp) if years else 1.5
    stability = 85.0 if avg_tenure >= 1.8 else 60.0 if avg_tenure >= 1.0 else 45.0
    loc_bonus = 0.0
    cand_loc = (candidate.get("current_location") or "").lower()
    if cand_loc and cand_loc in jd:
        loc_bonus = 5.0
    gap_penalty = 0.0
    if candidate.get("career_gap_months") and candidate.get("career_gap_months", 0) > 6:
        gap_penalty = min(8.0, (candidate.get("career_gap_months") - 6) * 0.8)
    cert_bonus = 0.0
    certs = str(candidate.get("certifications") or "").lower()
    if any(c in certs for c in ["aws", "azure", "gcp", "pmp", "scrum", "kubernetes", "ckad"]):
        cert_bonus = 3.5
    score = round(0.45 * domain + 0.35 * recency + 0.20 * stability + loc_bonus - gap_penalty + cert_bonus, 1)
    bullets = [
        f"Skill overlap with the JD is {'strong' if overlap >= 6 else 'moderate' if overlap >= 3 else 'thin'} ({overlap} matching terms).",
        f"Experience of {years or 'unspecified'} years; recency signal is {'good' if recency >= 75 else 'mixed'}.",
        f"Stability index {stability:.0f} based on ~{avg_tenure:.1f} years average tenure across {n_emp} employer(s).",
    ]
    return _normalize_score(
        {
            "fitment_score": score,
            "domain_relevance": domain,
            "skill_recency": recency,
            "stability_index": stability,
            "summary_bullets": bullets,
        },
        threshold,
    )


def _normalize_score(data: dict[str, Any], threshold: float) -> dict[str, Any]:
    score = float(data.get("fitment_score") or 0)
    score = max(0.0, min(100.0, score))
    bullets = data.get("summary_bullets") or []
    if isinstance(bullets, str):
        text = bullets
    else:
        text = "\n".join(f"• {b}" for b in bullets[:3])
    status = "Screened - AI Fit" if score >= threshold else "Sourced - Below Threshold"
    return {
        "fitment_score": round(score, 1),
        "summary_bullets": text,
        "status": status,
        "domain_relevance": _opt_float(data.get("domain_relevance")),
        "skill_recency": _opt_float(data.get("skill_recency")),
        "stability_index": _opt_float(data.get("stability_index")),
    }


def _opt_float(val: Any) -> float | None:
    try:
        return float(val) if val is not None else None
    except (TypeError, ValueError):
        return None


STOP = {
    "the", "and", "for", "with", "you", "will", "this", "that", "from", "have",
    "must", "years", "year", "experience", "client", "location", "hybrid",
    "office", "role", "team", "work", "plus", "nice", "have", " mand",
}
