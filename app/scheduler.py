import json
from typing import Any, Optional

from app import db
from app.config import MOCK_CALENDAR
from app.logging_config import get_logger

logger = get_logger("scheduler")

# Real Google Workspace / Microsoft Graph calendar sync would replace load_calendar()
# and booked_slot_ids() with free/busy queries. See docs/MODULE_4_6_NOTES.md.


def load_calendar() -> dict[str, Any]:
    return json.loads(MOCK_CALENDAR.read_text(encoding="utf-8"))


def available_slots() -> list[dict[str, Any]]:
    recruiters = ["Aisha Khan", "Vikram Malhotra", "Sneha Roy", "Rohan Joshi"]
    booked = db.booked_slot_ids()
    cal = load_calendar()
    open_slots = []
    for i, s in enumerate(cal["slots"]):
        if s["id"] not in booked:
            slot_copy = dict(s)
            slot_copy["interviewer"] = recruiters[i % len(recruiters)]
            open_slots.append(slot_copy)
    return open_slots


def propose(n: int = 3) -> list[dict[str, Any]]:
    return available_slots()[:n]


def book(candidate_id: int, slot_id: str, job_id: Optional[int] = None, stage: str = "L1") -> dict[str, Any]:
    if slot_id in db.booked_slot_ids():
        logger.warning(f"Booking attempt rejected: slot '{slot_id}' already booked")
        raise ValueError("That interview slot is already booked (no double-booking).")
    slot = next((s for s in load_calendar()["slots"] if s["id"] == slot_id), None)
    if not slot:
        logger.warning(f"Booking attempt rejected: unknown slot_id '{slot_id}'")
        raise ValueError(f"Unknown slot_id: {slot_id}")
    iid = db.insert_interview(
        {
            "candidate_id": candidate_id,
            "job_id": job_id,
            "stage": stage,
            "slot_id": slot_id,
            "slot_time": slot["start"],
            "confirmation_status": "Scheduled",
        }
    )
    logger.info(
        f"Booked interview #{iid} for candidate #{candidate_id} on slot '{slot_id}' ({slot.get('start')}), stage={stage}"
    )
    reminders = queue_reminders(iid, slot)
    return {
        "interview_id": iid,
        "id": iid,
        **slot,
        "confirmation_status": "Scheduled",
        "reminders_queued": len(reminders),
    }


# BRD-F-303: T-24h / T-2h / T-15m. These are local log rows only — no WhatsApp/SMS send.
REMINDER_COPY = [
    ("T-24h", "Confirming your interview {label}. Panel: {panel}. Join: {link}. Prep dossier attached (mock)."),
    ("T-2h", "Confirming attendance: reply 1 to Confirm, 2 to Request Immediate Reschedule. {label} via {channel}."),
    ("T-15m", "Starting soon — quick link: {link}"),
]


def queue_reminders(interview_id: int, slot: dict[str, Any]) -> list[dict[str, Any]]:
    existing = db.list_reminders(interview_id)
    if existing:
        logger.debug(f"Reminders already queued for interview #{interview_id}; skipping duplicate queue")
        return existing
    created = []
    for milestone, template in REMINDER_COPY:
        body = template.format(
            label=slot.get("label") or slot.get("start"),
            panel=slot.get("panel") or "hiring panel",
            channel=slot.get("channel") or "video",
            link=load_calendar().get("meeting_link", "https://meet.google.com/talentops-demo"),
        )
        rid = db.insert_reminder(
            {
                "interview_id": interview_id,
                "milestone": milestone,
                "channel": "mock-whatsapp",
                "body": body,
                "status": "queued",
            }
        )
        created.append({"id": rid, "milestone": milestone, "status": "queued", "body": body})
    logger.info(f"Queued {len(created)} reminders for interview #{interview_id} ({', '.join(r['milestone'] for r in created)})")
    return created


def dispatch_reminders(interview_id: Optional[int] = None) -> dict[str, Any]:
    """Mark queued reminders as sent. REAL CALL WOULD GO HERE: Meta WhatsApp Cloud API."""
    count = db.mark_reminders_sent(interview_id)
    target = f"interview #{interview_id}" if interview_id else "all queued interviews"
    logger.info(f"Dispatched {count} reminders for {target}")
    return {"sent": count, "reminders": db.list_reminders(interview_id)}


def confirm(interview_id: int, action: str, new_slot_id: Optional[str] = None) -> dict[str, Any]:
    row = db.fetchone("SELECT * FROM interviews WHERE id = ?", (interview_id,))
    if not row:
        logger.warning(f"Confirmation failed: interview #{interview_id} not found")
        raise ValueError("Interview not found")
    action = action.lower()
    if action == "confirm":
        db.update_interview(interview_id, "Confirmed")
        logger.info(f"Interview #{interview_id} status updated -> Confirmed")
        return {**row, "confirmation_status": "Confirmed"}
    if action == "noshow":
        db.update_interview(interview_id, "No-Show")
        logger.info(f"Interview #{interview_id} status updated -> No-Show")
        return {**row, "confirmation_status": "No-Show"}
    if action == "reschedule":
        if not new_slot_id:
            raise ValueError("new_slot_id is required to reschedule")
        if new_slot_id in db.booked_slot_ids() and new_slot_id != row.get("slot_id"):
            logger.warning(f"Reschedule failed: slot '{new_slot_id}' already booked")
            raise ValueError("That interview slot is already booked")
        slot = next((s for s in load_calendar()["slots"] if s["id"] == new_slot_id), None)
        if not slot:
            raise ValueError("Unknown slot")
        db.update_interview(interview_id, "Rescheduled", new_slot_id, slot["start"])
        logger.info(f"Interview #{interview_id} rescheduled to slot '{new_slot_id}' ({slot['start']})")
        return {**row, "slot_id": new_slot_id, "slot_time": slot["start"], "confirmation_status": "Rescheduled"}
    raise ValueError("action must be confirm, reschedule, or noshow")


def format_slot_label(start_iso: str) -> str:
    from datetime import datetime
    try:
        dt = datetime.fromisoformat(start_iso.replace("Z", "+00:00"))
        return dt.strftime("%A, %b %d at %I:%M %p")
    except Exception:
        return start_iso
