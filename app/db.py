import json
import sqlite3
from contextlib import contextmanager
from datetime import datetime, timezone
from typing import Any, Iterator, Optional

from app import config
from app.logging_config import get_logger

logger = get_logger("db")

SCHEMA = """
CREATE TABLE IF NOT EXISTS candidates (
  id INTEGER PRIMARY KEY,
  full_name TEXT,
  current_location TEXT,
  preferred_location TEXT,
  email TEXT,
  phone TEXT,
  linkedin_url TEXT,
  total_experience_years REAL,
  relevant_experience_years REAL,
  current_ctc REAL,
  expected_ctc REAL,
  notice_period_days INTEGER,
  current_company TEXT,
  previous_employers TEXT,
  skills TEXT,
  certifications TEXT,
  education TEXT,
  source_channel TEXT,
  resume_path TEXT,
  parser_engine TEXT,
  created_at TEXT
);

CREATE TABLE IF NOT EXISTS jobs (
  id INTEGER PRIMARY KEY,
  title TEXT,
  client_name TEXT,
  jd_text TEXT,
  created_at TEXT
);

CREATE TABLE IF NOT EXISTS scores (
  id INTEGER PRIMARY KEY,
  candidate_id INTEGER REFERENCES candidates(id),
  job_id INTEGER REFERENCES jobs(id),
  fitment_score REAL,
  summary_bullets TEXT,
  status TEXT,
  domain_relevance REAL,
  skill_recency REAL,
  stability_index REAL,
  engine TEXT,
  created_at TEXT
);

CREATE TABLE IF NOT EXISTS interviews (
  id INTEGER PRIMARY KEY,
  candidate_id INTEGER REFERENCES candidates(id),
  job_id INTEGER,
  stage TEXT,
  slot_id TEXT,
  slot_time TEXT,
  confirmation_status TEXT,
  created_at TEXT
);

CREATE TABLE IF NOT EXISTS chat_log (
  id INTEGER PRIMARY KEY,
  candidate_id INTEGER REFERENCES candidates(id),
  role TEXT,
  message TEXT,
  created_at TEXT
);

CREATE TABLE IF NOT EXISTS screening_sessions (
  candidate_id INTEGER PRIMARY KEY,
  employment_status TEXT,
  notice_actual TEXT,
  compensation_notes TEXT,
  relocation TEXT,
  qualified INTEGER DEFAULT 0,
  asked_json TEXT,
  updated_at TEXT
);


CREATE TABLE IF NOT EXISTS notes (
  id INTEGER PRIMARY KEY,
  candidate_id INTEGER REFERENCES candidates(id),
  note TEXT,
  author TEXT,
  created_at TEXT
);

CREATE TABLE IF NOT EXISTS tags (
  id INTEGER PRIMARY KEY,
  candidate_id INTEGER REFERENCES candidates(id),
  tag TEXT,
  created_at TEXT
);

CREATE TABLE IF NOT EXISTS timeline (
  id INTEGER PRIMARY KEY,
  candidate_id INTEGER REFERENCES candidates(id),
  status TEXT,
  note TEXT,
  created_at TEXT
);

CREATE TABLE IF NOT EXISTS reminders (
  id INTEGER PRIMARY KEY,
  interview_id INTEGER REFERENCES interviews(id),
  milestone TEXT,
  channel TEXT,
  body TEXT,
  status TEXT,
  created_at TEXT,
  sent_at TEXT
);
"""


def utcnow() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


@contextmanager
def connect() -> Iterator[sqlite3.Connection]:
    config.DATABASE_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(config.DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()


def init_db() -> None:
    with connect() as conn:
        conn.executescript(SCHEMA + '''
CREATE INDEX IF NOT EXISTS idx_candidates_email ON candidates(email);
CREATE INDEX IF NOT EXISTS idx_scores_candidate ON scores(candidate_id);
CREATE INDEX IF NOT EXISTS idx_scores_job ON scores(job_id);
CREATE INDEX IF NOT EXISTS idx_interviews_slot ON interviews(slot_id);
''')


def row_to_dict(row: Optional[sqlite3.Row]) -> Optional[dict[str, Any]]:
    if row is None:
        return None
    return dict(row)


def fetchall(query: str, params: tuple = ()) -> list[dict[str, Any]]:
    with connect() as conn:
        rows = conn.execute(query, params).fetchall()
    return [dict(r) for r in rows]


def fetchone(query: str, params: tuple = ()) -> Optional[dict[str, Any]]:
    with connect() as conn:
        row = conn.execute(query, params).fetchone()
    return row_to_dict(row)


def execute(query: str, params: tuple = ()) -> int:
    with connect() as conn:
        cur = conn.execute(query, params)
        return cur.lastrowid


def find_duplicate(email: Optional[str], phone: Optional[str], linkedin_url: Optional[str]) -> Optional[dict[str, Any]]:
    clauses, params = [], []
    if email:
        clauses.append("lower(email) = lower(?)")
        params.append(email.strip())
    if phone:
        digits = "".join(ch for ch in phone if ch.isdigit())[-10:]
        if digits:
            clauses.append("replace(replace(replace(phone, ' ', ''), '-', ''), '+', '') LIKE ?")
            params.append(f"%{digits}")
    if linkedin_url:
        clauses.append("lower(linkedin_url) = lower(?)")
        params.append(linkedin_url.strip())
    if not clauses:
        return None
    sql = f"SELECT * FROM candidates WHERE {' OR '.join(clauses)} ORDER BY id DESC LIMIT 1"
    match = fetchone(sql, tuple(params))
    if match:
        logger.info(f"Dedup match found: candidate matches existing #{match['id']} (email={match.get('email')})")
    return match


def upsert_candidate(payload: dict[str, Any]) -> tuple[int, str]:
    """Insert or merge on email/phone/linkedin. Returns (id, inserted|merged)."""
    existing = find_duplicate(payload.get("email"), payload.get("phone"), payload.get("linkedin_url"))
    payload = {**payload, "created_at": payload.get("created_at") or utcnow()}
    fields = [
        "full_name",
        "current_location",
        "preferred_location",
        "email",
        "phone",
        "linkedin_url",
        "total_experience_years",
        "relevant_experience_years",
        "current_ctc",
        "expected_ctc",
        "notice_period_days",
        "current_company",
        "previous_employers",
        "skills",
        "certifications",
        "education",
        "source_channel",
        "resume_path",
        "parser_engine",
        "created_at",
    ]
    if existing:
        sets = []
        params: list[Any] = []
        for f in fields:
            if f == "created_at":
                continue
            val = payload.get(f)
            if val not in (None, "", []):
                sets.append(f"{f} = ?")
                params.append(_serialize(val))
        if sets:
            params.append(existing["id"])
            execute(f"UPDATE candidates SET {', '.join(sets)} WHERE id = ?", tuple(params))
        logger.info(f"Upsert candidate: merged fields into existing candidate #{existing['id']}")
        return existing["id"], "merged"
    cols = ", ".join(fields)
    placeholders = ", ".join("?" for _ in fields)
    values = tuple(_serialize(payload.get(f)) for f in fields)
    cid = execute(f"INSERT INTO candidates ({cols}) VALUES ({placeholders})", values)
    logger.info(f"Upsert candidate: inserted new candidate #{cid} ('{payload.get('full_name')}')")
    return cid, "inserted"


def _serialize(val: Any) -> Any:
    if isinstance(val, (list, dict)):
        return json.dumps(val, ensure_ascii=False)
    return val


def list_candidates(status: Optional[str] = None, source: Optional[str] = None) -> list[dict[str, Any]]:
    sql = """
    SELECT c.*,
           s.fitment_score AS latest_score,
           s.status AS latest_status,
           s.summary_bullets AS latest_summary
    FROM candidates c
    LEFT JOIN scores s ON s.id = (
        SELECT id FROM scores WHERE candidate_id = c.id ORDER BY id DESC LIMIT 1
    )
    WHERE 1=1
    """
    params: list[Any] = []
    if status:
        sql += " AND s.status = ?"
        params.append(status)
    if source:
        sql += " AND c.source_channel = ?"
        params.append(source)
    sql += " ORDER BY c.id DESC"
    return fetchall(sql, tuple(params))


def get_candidate(cid: int) -> Optional[dict[str, Any]]:
    return fetchone("SELECT * FROM candidates WHERE id = ?", (cid,))


def list_jobs() -> list[dict[str, Any]]:
    return fetchall("SELECT * FROM jobs ORDER BY id ASC")


def get_job(jid: int) -> Optional[dict[str, Any]]:
    return fetchone("SELECT * FROM jobs WHERE id = ?", (jid,))


def insert_job(title: str, client_name: str, jd_text: str) -> int:
    return execute(
        "INSERT INTO jobs (title, client_name, jd_text, created_at) VALUES (?, ?, ?, ?)",
        (title, client_name, jd_text, utcnow()),
    )


def insert_score(row: dict[str, Any]) -> int:
    return execute(
        """
        INSERT INTO scores (
          candidate_id, job_id, fitment_score, summary_bullets, status,
          domain_relevance, skill_recency, stability_index, engine, created_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            row["candidate_id"],
            row["job_id"],
            row["fitment_score"],
            row["summary_bullets"],
            row["status"],
            row.get("domain_relevance"),
            row.get("skill_recency"),
            row.get("stability_index"),
            row.get("engine"),
            utcnow(),
        ),
    )


def add_chat(candidate_id: int, role: str, message: str) -> None:
    execute(
        "INSERT INTO chat_log (candidate_id, role, message, created_at) VALUES (?, ?, ?, ?)",
        (candidate_id, role, message, utcnow()),
    )


def chat_history(candidate_id: int) -> list[dict[str, Any]]:
    return fetchall(
        "SELECT * FROM chat_log WHERE candidate_id = ? ORDER BY id ASC",
        (candidate_id,),
    )


def get_session(candidate_id: int) -> dict[str, Any]:
    row = fetchone("SELECT * FROM screening_sessions WHERE candidate_id = ?", (candidate_id,))
    if row:
        asked = json.loads(row["asked_json"] or "[]")
        return {**row, "asked": asked}
    execute(
        "INSERT INTO screening_sessions (candidate_id, asked_json, qualified, updated_at) VALUES (?, ?, 0, ?)",
        (candidate_id, "[]", utcnow()),
    )
    return {
        "candidate_id": candidate_id,
        "employment_status": None,
        "notice_actual": None,
        "compensation_notes": None,
        "relocation": None,
        "qualified": 0,
        "asked": [],
    }


def save_session(session: dict[str, Any]) -> None:
    execute(
        """
        INSERT INTO screening_sessions (
          candidate_id, employment_status, notice_actual, compensation_notes,
          relocation, qualified, asked_json, updated_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ON CONFLICT(candidate_id) DO UPDATE SET
          employment_status = excluded.employment_status,
          notice_actual = excluded.notice_actual,
          compensation_notes = excluded.compensation_notes,
          relocation = excluded.relocation,
          qualified = excluded.qualified,
          asked_json = excluded.asked_json,
          updated_at = excluded.updated_at
        """,
        (
            session["candidate_id"],
            session.get("employment_status"),
            session.get("notice_actual"),
            session.get("compensation_notes"),
            session.get("relocation"),
            1 if session.get("qualified") else 0,
            json.dumps(session.get("asked") or []),
            utcnow(),
        ),
    )


def insert_interview(row: dict[str, Any]) -> int:
    return execute(
        """
        INSERT INTO interviews (
          candidate_id, job_id, stage, slot_id, slot_time, confirmation_status, created_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        (
            row["candidate_id"],
            row.get("job_id"),
            row.get("stage") or "L1",
            row.get("slot_id"),
            row.get("slot_time"),
            row.get("confirmation_status") or "Scheduled",
            utcnow(),
        ),
    )


def update_interview(iid: int, status: str, slot_id: Optional[str] = None, slot_time: Optional[str] = None) -> None:
    if slot_id:
        execute(
            "UPDATE interviews SET confirmation_status = ?, slot_id = ?, slot_time = ? WHERE id = ?",
            (status, slot_id, slot_time, iid),
        )
    else:
        execute("UPDATE interviews SET confirmation_status = ? WHERE id = ?", (status, iid))


def booked_slot_ids() -> set[str]:
    rows = fetchall(
        "SELECT slot_id FROM interviews WHERE confirmation_status IN ('Scheduled', 'Confirmed', 'Rescheduled') AND slot_id IS NOT NULL"
    )
    return {r["slot_id"] for r in rows if r["slot_id"]}


def list_interviews() -> list[dict[str, Any]]:
    return fetchall(
        """
        SELECT i.*, c.full_name
        FROM interviews i
        LEFT JOIN candidates c ON c.id = i.candidate_id
        ORDER BY i.id DESC
        """
    )


def insert_reminder(row: dict[str, Any]) -> int:
    return execute(
        """
        INSERT INTO reminders (interview_id, milestone, channel, body, status, created_at, sent_at)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        (
            row["interview_id"],
            row["milestone"],
            row.get("channel") or "mock-whatsapp",
            row["body"],
            row.get("status") or "queued",
            utcnow(),
            row.get("sent_at"),
        ),
    )


def list_reminders(interview_id: Optional[int] = None) -> list[dict[str, Any]]:
    if interview_id:
        return fetchall("SELECT * FROM reminders WHERE interview_id = ? ORDER BY id ASC", (interview_id,))
    return fetchall("SELECT * FROM reminders ORDER BY id DESC")


def mark_reminders_sent(interview_id: Optional[int] = None) -> int:
    now = utcnow()
    if interview_id:
        with connect() as conn:
            cur = conn.execute(
                "UPDATE reminders SET status = 'sent', sent_at = ? WHERE interview_id = ? AND status = 'queued'",
                (now, interview_id),
            )
            return cur.rowcount
    with connect() as conn:
        cur = conn.execute(
            "UPDATE reminders SET status = 'sent', sent_at = ? WHERE status = 'queued'",
            (now,),
        )
        return cur.rowcount


def search_candidates(query: str) -> list[dict[str, Any]]:
    q = f"%{query.strip()}%"
    sql = """
    SELECT c.*, s.fitment_score AS latest_score, s.status AS latest_status
    FROM candidates c
    LEFT JOIN scores s ON s.id = (
        SELECT id FROM scores WHERE candidate_id = c.id ORDER BY id DESC LIMIT 1
    )
    WHERE c.full_name LIKE ? OR c.skills LIKE ? OR c.current_company LIKE ? OR c.email LIKE ?
    ORDER BY c.id DESC
    """
    return fetchall(sql, (q, q, q, q))


def add_candidate_note(candidate_id: int, note: str, author: str = "Recruiter") -> int:
    nid = execute(
        "INSERT INTO notes (candidate_id, note, author, created_at) VALUES (?, ?, ?, ?)",
        (candidate_id, note.strip(), author.strip(), utcnow()),
    )
    logger.info(f"Added note #{nid} for candidate #{candidate_id} by {author}")
    return nid


def get_candidate_notes(candidate_id: int) -> list[dict[str, Any]]:
    return fetchall("SELECT * FROM notes WHERE candidate_id = ? ORDER BY id DESC", (candidate_id,))


def update_candidate_status(candidate_id: int, status: str, note: Optional[str] = None) -> None:
    execute("INSERT INTO timeline (candidate_id, status, note, created_at) VALUES (?, ?, ?, ?)",
            (candidate_id, status, note or "Manual status update", utcnow()))
    logger.info(f"Updated candidate #{candidate_id} status to '{status}'")


def soft_delete_candidate(candidate_id: int) -> bool:
    with connect() as conn:
        cur = conn.execute("UPDATE candidates SET parser_engine = 'deleted' WHERE id = ?", (candidate_id,))
        return cur.rowcount > 0


def update_job(jid: int, title: Optional[str] = None, client_name: Optional[str] = None, jd_text: Optional[str] = None) -> bool:
    sets, params = [], []
    if title:
        sets.append("title = ?")
        params.append(title)
    if client_name:
        sets.append("client_name = ?")
        params.append(client_name)
    if jd_text:
        sets.append("jd_text = ?")
        params.append(jd_text)
    if not sets:
        return False
    params.append(jid)
    execute(f"UPDATE jobs SET {', '.join(sets)} WHERE id = ?", tuple(params))
    return True


def get_interview(iid: int) -> Optional[dict[str, Any]]:
    return fetchone(
        "SELECT i.*, c.full_name, c.email FROM interviews i LEFT JOIN candidates c ON c.id = i.candidate_id WHERE i.id = ?",
        (iid,),
    )


def cancel_interview(iid: int) -> bool:
    with connect() as conn:
        cur = conn.execute("UPDATE interviews SET confirmation_status = 'Cancelled' WHERE id = ?", (iid,))
        return cur.rowcount > 0


def get_candidate_timeline(candidate_id: int) -> list[dict[str, Any]]:
    return fetchall("SELECT * FROM timeline WHERE candidate_id = ? ORDER BY id ASC", (candidate_id,))


def add_candidate_tag(candidate_id: int, tag: str) -> int:
    tid = execute("INSERT INTO tags (candidate_id, tag, created_at) VALUES (?, ?, ?)", (candidate_id, tag.strip(), utcnow()))
    logger.info(f"Added tag '{tag}' to candidate #{candidate_id}")
    return tid

def get_candidate_tags(candidate_id: int) -> list[str]:
    rows = fetchall("SELECT tag FROM tags WHERE candidate_id = ?", (candidate_id,))
    return [r["tag"] for r in rows]


def archive_job(jid: int) -> bool:
    with connect() as conn:
        cur = conn.execute("UPDATE jobs SET client_name = client_name || ' [ARCHIVED]' WHERE id = ?", (jid,))
        return cur.rowcount > 0


def search_candidates_advanced(terms: list[str]) -> list[dict[str, Any]]:
    """Search candidates matching all or any terms across full name, skills, and current company."""
    if not terms:
        return list_candidates()
    clauses = []
    params = []
    for term in terms:
        t = f"%{term.strip()}%"
        clauses.append("(c.full_name LIKE ? OR c.skills LIKE ? OR c.current_company LIKE ?)")
        params.extend([t, t, t])
    sql = f"""
    SELECT c.*, s.fitment_score AS latest_score, s.status AS latest_status
    FROM candidates c
    LEFT JOIN scores s ON s.id = (
        SELECT id FROM scores WHERE candidate_id = c.id ORDER BY id DESC LIMIT 1
    )
    WHERE {' AND '.join(clauses)}
    ORDER BY c.id DESC
    """
    return fetchall(sql, tuple(params))


def delete_candidate_note(note_id: int) -> bool:
    with connect() as conn:
        cur = conn.execute("DELETE FROM notes WHERE id = ?", (note_id,))
        return cur.rowcount > 0


def delete_candidate_tag(candidate_id: int, tag: str) -> bool:
    with connect() as conn:
        cur = conn.execute("DELETE FROM tags WHERE candidate_id = ? AND tag = ?", (candidate_id, tag.strip()))
        return cur.rowcount > 0


def record_timeline_event(candidate_id: int, status: str, note: Optional[str] = None) -> int:
    return execute(
        "INSERT INTO timeline (candidate_id, status, note, created_at) VALUES (?, ?, ?, ?)",
        (candidate_id, status, note or "System update", utcnow()),
    )


def restore_candidate(candidate_id: int) -> bool:
    with connect() as conn:
        cur = conn.execute("UPDATE candidates SET parser_engine = 'restored' WHERE id = ?", (candidate_id,))
        return cur.rowcount > 0


def get_job_with_stats(jid: int) -> Optional[dict[str, Any]]:
    job = get_job(jid)
    if not job:
        return None
    scores = fetchall("SELECT fitment_score FROM scores WHERE job_id = ?", (jid,))
    avg_score = round(sum(s["fitment_score"] for s in scores) / len(scores), 1) if scores else None
    return {**job, "scored_candidates_count": len(scores), "avg_fitment_score": avg_score}


def update_job_status(jid: int, is_active: bool) -> bool:
    marker = "[INACTIVE]" if not is_active else ""
    with connect() as conn:
        cur = conn.execute("UPDATE jobs SET client_name = replace(client_name, ' [INACTIVE]', '') || ? WHERE id = ?", (f" {marker}".strip(), jid))
        return cur.rowcount > 0


def unarchive_job(jid: int) -> bool:
    with connect() as conn:
        cur = conn.execute("UPDATE jobs SET client_name = replace(client_name, ' [ARCHIVED]', '') WHERE id = ?", (jid,))
        return cur.rowcount > 0


def get_interviews_for_candidate(candidate_id: int) -> list[dict[str, Any]]:
    return fetchall("SELECT * FROM interviews WHERE candidate_id = ? ORDER BY id DESC", (candidate_id,))
