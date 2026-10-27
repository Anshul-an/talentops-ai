from fastapi.testclient import TestClient

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
