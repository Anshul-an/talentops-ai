from typing import Any

from app import db
from app import scheduler
from app.llm import complete_json, has_llm
from app.logging_config import get_logger

logger = get_logger("chat_agent")

QUESTIONS = [
    ("employment", "Are you currently employed, serving notice, or immediately available?"),
    ("notice", "What is your actual last working day / notice period, and is a buyout negotiable vs what is printed on paper?"),
    ("compensation", "Please share current fixed + variable CTC and your expected CTC (annual, INR)."),
    ("relocation", "Are you open to relocating, and is hybrid / in-office attendance feasible for this mandate?"),
]

CHAT_SYSTEM = """You are Virtuous' candidate pre-screening agent (demo).
You must collect four facts, one at a time if missing:
employment_status, notice_actual, compensation_notes, relocation.
Be concise, professional, and warm. Do not ask for Aadhaar/PAN or other sensitive IDs.
After all four are captured, set qualified=true if the candidate is employed or serving notice
(or immediately available), has a usable notice story, shared CTC, and answered relocation.
Then propose they pick an interview slot.
Return ONLY JSON:
{
  "reply": "message to candidate",
  "employment_status": string or null,
  "notice_actual": string or null,
  "compensation_notes": string or null,
  "relocation": string or null,
  "qualified": boolean
}"""


def _detect_hinglish_or_hindi(msg: str) -> bool:
    hindi_keywords = ["haan", "nahi", "accha", "kya", "theek", "bhai", "namaste", "dhanyawad"]
    return any(w in msg.lower().split() for w in hindi_keywords)


def start_or_continue(candidate_id: int, user_message: str) -> dict[str, Any]:
    cand = db.get_candidate(candidate_id)
    if not cand:
        raise ValueError("Candidate not found")
    session = db.get_session(candidate_id)
    logger.debug(f"Chat turn starting for candidate #{candidate_id} ('{cand.get('full_name')}'): '{user_message[:50]}'")
    db.add_chat(candidate_id, "user", user_message)

    if has_llm():
        try:
            result = _llm_turn(cand, session, user_message)
            result["engine"] = result.get("engine") or "llm"
            return _finalize(candidate_id, session, result)
        except Exception as exc:
            logger.warning(f"LLM turn failed for candidate #{candidate_id}: {exc}; falling back to scripted dialog")
            result = _scripted_turn(cand, session, user_message)
            result["engine"] = "scripted-fallback"
            return _finalize(candidate_id, session, result)

    result = _scripted_turn(cand, session, user_message)
    result["engine"] = "scripted"
    return _finalize(candidate_id, session, result)


def _llm_turn(cand: dict, session: dict, user_message: str) -> dict[str, Any]:
    history = db.chat_history(cand["id"])
    transcript = "\n".join(f"{h['role']}: {h['message']}" for h in history[-12:])
    payload = (
        f"Candidate: {cand.get('full_name')} | notice_on_cv={cand.get('notice_period_days')} "
        f"| current_ctc={cand.get('current_ctc')} expected={cand.get('expected_ctc')}\n"
        f"Already captured: { {k: session.get(k) for k in ['employment_status','notice_actual','compensation_notes','relocation']} }\n"
        f"Transcript:\n{transcript}\nLatest user message: {user_message}"
    )
    data, engine = complete_json(CHAT_SYSTEM, payload, max_tokens=800)
    data["engine"] = engine
    return data


def _scripted_turn(cand: dict, session: dict, user_message: str) -> dict[str, Any]:
    asked = list(session.get("asked") or [])
    last = asked[-1] if asked else None
    if last and not session.get(_field(last)):
        session[_field(last)] = user_message.strip()

    missing = [q for q, _ in QUESTIONS if not session.get(_field(q))]
    if not asked and user_message.lower() in {"hi", "hello", "hey", "start"}:
        missing = [q for q, _ in QUESTIONS if not session.get(_field(q))]

    if missing:
        nxt = missing[0]
        if nxt not in asked:
            asked.append(nxt)
        session["asked"] = asked
        qtext = dict(QUESTIONS)[nxt]
        name = cand.get("full_name") or "there"
        if len(asked) == 1:
            reply = (
                f"Hi {name.split()[0]}, this is the TalentOps screening desk. "
                f"I'll confirm four points, then we can lock an interview slot. {qtext}"
            )
        else:
            reply = f"Thanks — noted. {qtext}"
        return {
            "reply": reply,
            "employment_status": session.get("employment_status"),
            "notice_actual": session.get("notice_actual"),
            "compensation_notes": session.get("compensation_notes"),
            "relocation": session.get("relocation"),
            "qualified": False,
        }

    session["asked"] = asked
    return {
        "reply": (
            "All four qualification points are captured. If this looks aligned, "
            "reply with the slot id you'd like (e.g. slot-mon-1000) from the list I'll show, "
            "or type BOOK <slot-id>."
        ),
        "employment_status": session.get("employment_status"),
        "notice_actual": session.get("notice_actual"),
        "compensation_notes": session.get("compensation_notes"),
        "relocation": session.get("relocation"),
        "qualified": True,
    }


def _field(key: str) -> str:
    return {
        "employment": "employment_status",
        "notice": "notice_actual",
        "compensation": "compensation_notes",
        "relocation": "relocation",
    }[key]


def _finalize(candidate_id: int, session: dict, result: dict[str, Any]) -> dict[str, Any]:
    prev_qualified = bool(session.get("qualified"))
    for key in ("employment_status", "notice_actual", "compensation_notes", "relocation"):
        if result.get(key):
            session[key] = result[key]
    qualified = bool(result.get("qualified")) and all(
        session.get(k) for k in ("employment_status", "notice_actual", "compensation_notes", "relocation")
    )
    session["qualified"] = qualified
    session["candidate_id"] = candidate_id
    db.save_session(session)

    if not prev_qualified and qualified:
        logger.info(f"Candidate #{candidate_id} state transition -> QUALIFIED for interview scheduling")
    else:
        logger.debug(f"Candidate #{candidate_id} session updated (qualified={qualified})")

    slots: list[dict[str, Any]] = []
    reply = str(result.get("reply") or "")
    if qualified:
        slots = scheduler.propose(3)
        if slots:
            listing = "\n".join(f"- {s['id']}: {s['label']} ({s['channel']})" for s in slots)
            reply = reply.rstrip() + "\n\nOpen slots:\n" + listing

    history = db.chat_history(candidate_id)
    user_last = history[-1]["message"] if history else ""
    chosen = _extract_slot(user_last)
    booked = None
    if qualified and chosen:
        try:
            booked = scheduler.book(candidate_id, chosen)
            logger.info(f"Candidate #{candidate_id} successfully booked slot '{chosen}'")
            reply += f"\n\nBooked {booked['label']}. Status: Scheduled. Calendar invite would be sent via Google/M365 here."
            slots = []
        except ValueError as exc:
            logger.warning(f"Candidate #{candidate_id} failed to book slot '{chosen}': {exc}")
            reply += f"\n\nCould not book that slot: {exc}"

    db.add_chat(candidate_id, "assistant", reply)
    return {
        "reply": reply,
        "qualified": qualified,
        "captured": {
            "employment_status": session.get("employment_status"),
            "notice_actual": session.get("notice_actual"),
            "compensation_notes": session.get("compensation_notes"),
            "relocation": session.get("relocation"),
        },
        "proposed_slots": slots,
        "booked": booked,
        "engine": result.get("engine"),
    }


def _extract_slot(text: str) -> str | None:
    import re

    m = re.search(r"slot-[a-z0-9-]+", text.lower())
    return m.group(0) if m else None


def reset_session(candidate_id: int) -> bool:
    with db.connect() as conn:
        conn.execute("DELETE FROM screening_sessions WHERE candidate_id = ?", (candidate_id,))
        conn.execute("DELETE FROM chat_log WHERE candidate_id = ?", (candidate_id,))
    logger.info(f"Screening session reset for candidate #{candidate_id}")
    return True
