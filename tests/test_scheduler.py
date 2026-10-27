import pytest

from app import db, scheduler


def test_no_double_booking():
    db.upsert_candidate({"full_name": "A", "email": "a@example.com"})
    db.upsert_candidate({"full_name": "B", "email": "b@example.com"})
    first = scheduler.book(1, "slot-mon-1000")
    assert first["confirmation_status"] == "Scheduled"
    assert first["interview_id"] >= 1
    with pytest.raises(ValueError, match="already booked"):
        scheduler.book(2, "slot-mon-1000")
    open_ids = {s["id"] for s in scheduler.available_slots()}
    assert "slot-mon-1000" not in open_ids


def test_confirm_and_reschedule():
    db.upsert_candidate({"full_name": "C", "email": "c@example.com"})
    booked = scheduler.book(1, "slot-tue-1130")
    confirmed = scheduler.confirm(booked["interview_id"], "confirm")
    assert confirmed["confirmation_status"] == "Confirmed"
    moved = scheduler.confirm(booked["interview_id"], "reschedule", new_slot_id="slot-wed-0930")
    assert moved["confirmation_status"] == "Rescheduled"
    assert moved["slot_id"] == "slot-wed-0930"
