from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from app import config, db, llm
from app.main import app
from app.seed import seed_if_empty


@pytest.fixture(autouse=True)
def tmp_db(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setattr(config, "DATABASE_PATH", tmp_path / "test.db")
    monkeypatch.setattr(llm, "_ollama_up", lambda: False)
    db.init_db()
    seed_if_empty()
    yield


@pytest.fixture
def client():
    with TestClient(app) as c:
        yield c
