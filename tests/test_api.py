from fastapi.testclient import TestClient

from app import db
from app.main import app


def test_health_and_jobs_seeded():
    with TestClient(app) as client:
        r = client.get("/api/health")
        assert r.status_code == 200
        body = r.json()
        assert body["ok"] is True
        assert body["provider"] in {"heuristic", "anthropic", "gemini", "groq", "ollama"}
        jobs = client.get("/jobs").json()["jobs"]
        assert len(jobs) >= 2


def test_ingest_score_dashboard_excel_flow():
    with TestClient(app) as client:
        ingest = client.post("/api/resumes/ingest-samples")
        assert ingest.status_code == 200
        assert ingest.json()["ingested"] >= 8

        people = client.get("/candidates").json()["candidates"]
        assert people
        job_id = client.get("/jobs").json()["jobs"][0]["id"]
        scored = client.post("/score", json={"job_id": job_id})
        assert scored.status_code == 200
        assert scored.json()["scores"]

        dash = client.get("/dashboard/summary").json()
        assert dash["sourced"] == len(people)
        assert "average_fitment_score" in dash
        assert dash["activity_to_output"]
        assert "queued" in dash["reminders"]

        xls = client.get("/export/excel")
        assert xls.status_code == 200
        assert "spreadsheetml" in xls.headers["content-type"]


def test_spec_paths_match_build_plan():
    with TestClient(app) as client:
        assert client.get("/candidates").status_code == 200
        assert client.get("/dashboard/summary").status_code == 200


def test_search_candidate_by_name(client):
    db.upsert_candidate({"full_name": "Ananya Rao", "email": "ananya@example.com"})
    res = client.get("/api/candidates/search?q=Ananya")
    assert res.status_code == 200
    assert "candidates" in res.json()
    assert len(res.json()["candidates"]) >= 1


def test_search_candidate_by_skill(client):
    db.upsert_candidate({"full_name": "Python Dev", "email": "py@example.com", "skills": "Python, Django"})
    res = client.get("/api/candidates/search?q=Python")
    assert res.status_code == 200
    assert "count" in res.json()
    assert res.json()["count"] >= 1


def test_candidate_notes_crud(client):
    cid, _ = db.upsert_candidate({"full_name": "Notes Candidate", "email": "notes@example.com"})
    res = client.post(f"/api/candidates/{cid}/notes", json={"note": "Strong communication skills", "author": "Recruiter A"})
    assert res.status_code == 200
    res_list = client.get(f"/api/candidates/{cid}/notes")
    assert res_list.status_code == 200
    assert len(res_list.json()["notes"]) >= 1


def test_candidate_status_update(client):
    cid, _ = db.upsert_candidate({"full_name": "Status Candidate", "email": "status@example.com"})
    res = client.patch(f"/api/candidates/{cid}/status", json={"status": "Screened - AI Fit", "note": "Verified manually"})
    assert res.status_code == 200
    assert res.json()["updated"] is True


def test_candidate_soft_delete(client):
    cid, _ = db.upsert_candidate({"full_name": "Delete Candidate", "email": "del@example.com"})
    res = client.delete(f"/api/candidates/{cid}")
    assert res.status_code == 200


def test_bulk_score_api(client):
    cid, _ = db.upsert_candidate({"full_name": "Bulk Candidate", "email": "bulk@example.com", "skills": "Python, FastAPI"})
    job = db.list_jobs()[0]
    res = client.post("/api/score/bulk", json={"job_id": job["id"], "candidate_ids": [cid]})
    assert res.status_code == 200
    assert "scores" in res.json()


def test_csv_export_endpoint(client):
    res = client.get("/api/export/csv")
    assert res.status_code == 200
    assert "text/csv" in res.headers["content-type"]
    assert "ID,Name" in res.text


def test_version_info_endpoint(client):
    res = client.get("/api/version")
    assert res.status_code == 200
    assert res.json()["name"] == "TalentOps AI"


def test_detailed_health_endpoint(client):
    res = client.get("/api/health/detailed")
    assert res.status_code == 200
    assert "database" in res.json()


def test_interview_cancel_endpoint(client):
    res = client.delete("/api/interviews/99999")
    assert res.status_code in (404, 200)
