import json
from typing import Any

from app import db
from app.config import MOCK_RECRUITERS


def _reminder_counts() -> dict[str, int]:
    rows = db.list_reminders()
    return {
        "queued": sum(1 for r in rows if r.get("status") == "queued"),
        "sent": sum(1 for r in rows if r.get("status") == "sent"),
    }


def summary() -> dict[str, Any]:
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
