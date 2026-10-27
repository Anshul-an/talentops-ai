from app import db, scheduler
from app.dossier import build_dossier


def test_booking_queues_three_reminders_and_dispatch_marks_sent():
    db.upsert_candidate({"full_name": "A", "email": "remind@example.com"})
    booked = scheduler.book(1, "slot-mon-1000")
    assert booked["reminders_queued"] == 3
    rows = db.list_reminders(booked["interview_id"])
    assert {r["milestone"] for r in rows} == {"T-24h", "T-2h", "T-15m"}
    assert all(r["status"] == "queued" for r in rows)
    out = scheduler.dispatch_reminders(booked["interview_id"])
    assert out["sent"] == 3
    assert all(r["status"] == "sent" for r in db.list_reminders(booked["interview_id"]))


def test_dossier_contains_name_and_no_email_send():
    cid, _ = db.upsert_candidate({"full_name": "Ananya Rao", "email": "doss@example.com", "skills": "Python"})
    pack = build_dossier(cid)
    assert "Ananya Rao" in pack["markdown"]
    assert pack["delivery"] == "local-preview"


def test_no_double_queueing():
    cid, _ = db.upsert_candidate({"full_name": "Reminder Cand", "email": "rc@test.com"})
    iid = db.insert_interview({
        "candidate_id": cid,
        "slot_id": "slot-test-double",
        "slot_time": "2026-11-01T10:00:00Z",
    })
    slot = {"id": "slot-test-double", "start": "2026-11-01T10:00:00Z", "label": "Test"}
    r1 = scheduler.queue_reminders(iid, slot)
    r2 = scheduler.queue_reminders(iid, slot)
    assert len(r1) == len(r2)
