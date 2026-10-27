from app import db


def test_duplicate_email_merges():
    id1, action1 = db.upsert_candidate({"full_name": "Old Name", "email": "merge@example.com", "skills": "Java"})
    id2, action2 = db.upsert_candidate({"full_name": "New Name", "email": "merge@example.com", "skills": "Python"})
    assert action1 == "inserted"
    assert action2 == "merged"
    assert id1 == id2
    row = db.get_candidate(id1)
    assert row["full_name"] == "New Name"
    assert "Python" in row["skills"]
