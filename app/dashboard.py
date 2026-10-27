import json
import time
from typing import Any

from app import db
from app.config import MOCK_RECRUITERS
from app.logging_config import get_logger

logger = get_logger("dashboard")


def _reminder_counts() -> dict[str, int]:
    rows = db.list_reminders()
    return {
        "queued": sum(1 for r in rows if r.get("status") == "queued"),
        "sent": sum(1 for r in rows if r.get("status") == "sent"),
    }


def summary() -> dict[str, Any]:
    t0 = time.perf_counter()
    candidates = db.list_candidates()
    scores = db.fetchall("SELECT * FROM scores")
    interviews = db.list_interviews()
    jobs = db.list_jobs()

    sourced = len(candidates)
    qualified = sum(1 for c in candidates if (c.get("latest_status") or "") == "Screened - AI Fit")
    below = sourced - qualified
    avg_score = round(
        sum(s["fitment_score"] for s in scores) / len(scores), 1
    ) if scores else 0.0

    by_status: dict[str, int] = {}
    for c in candidates:
        key = c.get("latest_status") or "Sourced - Unscored"
        by_status[key] = by_status.get(key, 0) + 1

    by_channel: dict[str, int] = {}
    for c in candidates:
        ch = c.get("source_channel") or "Unknown"
        by_channel[ch] = by_channel.get(ch, 0) + 1

    iv_status: dict[str, int] = {}
    for i in interviews:
        st = i.get("confirmation_status") or "Unknown"
        iv_status[st] = iv_status.get(st, 0) + 1

    recruiters = json.loads(MOCK_RECRUITERS.read_text(encoding="utf-8"))
    activity_to_output = []
    for r in recruiters:
        flags = []
        if r["productive_hours"] > 6 and r["profiles_added"] < 2:
            flags.append("high screen time, low sourcing")
        if r["submissions"] >= 3 and r["first_rounds"] / max(r["submissions"], 1) < 0.25:
            flags.append("high submission-to-interview rejection")
        activity_to_output.append(
            {
                "recruiter_id": r["recruiter_name"].lower().replace(" ", "_"),
                "recruiter_name": r["recruiter_name"],
                "login_hours": r["login_hours"],
                "active_hours": r["productive_hours"],
                "sourced": r["profiles_added"],
                "submitted": r["submissions"],
                "interviewed": r["first_rounds"],
                "closed": r["closures"],
                "flags": flags,
            }
        )

    elapsed_ms = round((time.perf_counter() - t0) * 1000, 2)
    logger.info(
        f"Dashboard summary aggregated in {elapsed_ms}ms ({sourced} candidates, {len(interviews)} interviews, {len(jobs)} jobs)",
        extra={
            "extra_data": {
                "elapsed_ms": elapsed_ms,
                "sourced": sourced,
                "interviews": len(interviews),
                "jobs": len(jobs),
            }
        },
    )

    return {
        "sourced": sourced,
        "qualified": qualified,
        "below_threshold": below,
        "qualified_ratio": round(qualified / sourced, 3) if sourced else 0,
        "average_fitment_score": avg_score,
        "jobs": len(jobs),
        "interviews": len(interviews),
        "by_status": by_status,
        "by_channel": by_channel,
        "interview_pipeline": iv_status,
        "recruiters": recruiters,
        "activity_to_output": activity_to_output,
        # Mocked conversion metrics so the executive view matches BRD-F-501
        "cv_select_ratio": 0.42,
        "interview_to_offer": 0.28,
        "offer_to_join": 0.81,
        "avg_time_to_fill_days": 34,
        "reminders": _reminder_counts(),
    }


def channel_roi() -> dict[str, Any]:
    cands = db.list_candidates()
    spend_map = {"Naukri": 45000, "LinkedIn": 62000, "Shine": 18000, "Direct upload": 0, "Inbound email": 0}
    by_channel: dict[str, dict] = {}
    for c in cands:
        ch = c.get("source_channel") or "Unknown"
        stats = by_channel.setdefault(ch, {"sourced": 0, "qualified": 0, "scores": []})
        stats["sourced"] += 1
        if (c.get("latest_status") or "") == "Screened - AI Fit":
            stats["qualified"] += 1
        if c.get("latest_score"):
            stats["scores"].append(float(c["latest_score"]))
    results = []
    for ch, d in by_channel.items():
        spend = spend_map.get(ch, 12000)
        avg_score = round(sum(d["scores"]) / len(d["scores"]), 1) if d["scores"] else 0.0
        results.append({
            "channel": ch,
            "spend": spend,
            "sourced": d["sourced"],
            "qualified": d["qualified"],
            "avg_score": avg_score,
            "cpa": round(spend / d["qualified"], 2) if d["qualified"] else None,
        })
    return {"channels": results}
