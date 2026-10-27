"""Local client-submission dossier (BRD stage 3). Not emailed; no client ATS push."""
from typing import Any, Optional

from app import db


def build_dossier(candidate_id: int, job_id: Optional[int] = None) -> dict[str, Any]:
    cand = db.get_candidate(candidate_id)
    if not cand:
        raise ValueError("Candidate not found")
    scores = db.fetchall(
        "SELECT * FROM scores WHERE candidate_id = ? ORDER BY id DESC",
        (candidate_id,),
    )
    score = None
    if job_id:
        score = next((s for s in scores if s["job_id"] == job_id), scores[0] if scores else None)
    elif scores:
        score = scores[0]
    job = db.get_job(job_id) if job_id else (db.get_job(score["job_id"]) if score else None)
    session = db.get_session(candidate_id)
    lines = [
        f"# Candidate submission dossier — {cand.get('full_name') or 'Unnamed'}",
        "",
        f"**Client / mandate:** {(job or {}).get('client_name') or '—'} / {(job or {}).get('title') or 'unscored'}",
        f"**Source:** {cand.get('source_channel') or '—'}",
        f"**Location:** {cand.get('current_location') or '—'} (prefers {cand.get('preferred_location') or '—'})",
        f"**Experience:** {cand.get('total_experience_years') or '—'} yrs | **Notice:** {cand.get('notice_period_days') or '—'} days",
        f"**CTC:** current {cand.get('current_ctc') or '—'} L · expected {cand.get('expected_ctc') or '—'} L",
        f"**Skills:** {cand.get('skills') or '—'}",
        "",
        "## Fitment",
        f"- Score: {(score or {}).get('fitment_score') if score else 'not scored'}",
        f"- Status: {(score or {}).get('status') if score else 'Sourced - Unscored'}",
        (score or {}).get("summary_bullets") or "- No summary yet.",
        "",
        "## Screening desk (captured)",
        f"- Employment: {session.get('employment_status') or 'pending'}",
        f"- Notice (actual): {session.get('notice_actual') or 'pending'}",
        f"- Compensation: {session.get('compensation_notes') or 'pending'}",
        f"- Relocation / hybrid: {session.get('relocation') or 'pending'}",
        "",
        "_This file would be emailed to the client panel. No CEIPAL/Workday injection in this demo._",
    ]
    markdown = "\n".join(lines)
    return {
        "candidate_id": candidate_id,
        "job_id": (job or {}).get("id"),
        "markdown": markdown,
        "delivery": "local-preview",
    }