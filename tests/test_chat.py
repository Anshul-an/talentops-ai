from app import chat_agent, db


def test_scripted_chat_asks_all_four_then_proposes_slots():
    cid, _ = db.upsert_candidate({"full_name": "Ananya Rao", "email": "chat@example.com"})
    first = chat_agent.start_or_continue(cid, "hi")
    assert "employed" in first["reply"].lower() or "currently employed" in first["reply"].lower()
    assert first["qualified"] is False

    r2 = chat_agent.start_or_continue(cid, "Employed, not serving notice yet")
    assert "notice" in r2["reply"].lower()

    r3 = chat_agent.start_or_continue(cid, "30 days on paper, buyout possible")
    assert "ctc" in r3["reply"].lower() or "compensation" in r3["reply"].lower()

    r4 = chat_agent.start_or_continue(cid, "Current 24 LPA, expected 32 LPA")
    assert "relocat" in r4["reply"].lower() or "hybrid" in r4["reply"].lower()

    r5 = chat_agent.start_or_continue(cid, "Hybrid Bengaluru is fine")
    assert r5["qualified"] is True
    assert r5["captured"]["employment_status"]
    assert r5["captured"]["notice_actual"]
    assert r5["captured"]["compensation_notes"]
    assert r5["captured"]["relocation"]
    assert r5["proposed_slots"]
    assert any("slot-" in s["id"] for s in r5["proposed_slots"])


def test_chat_reset_session():
    from app import chat_agent, db
    cid, _ = db.upsert_candidate({"full_name": "Reset Test", "email": "reset@test.com"})
    chat_agent.start_or_continue(cid, "Hello")
    assert len(db.chat_history(cid)) > 0
    chat_agent.reset_session(cid)
    assert len(db.chat_history(cid)) == 0
