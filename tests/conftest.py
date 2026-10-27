from pathlib import Path

import pytest

from app import config, db, llm


@pytest.fixture(autouse=True)
def tmp_db(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setattr(config, "DATABASE_PATH", tmp_path / "test.db")
    monkeypatch.setattr(llm, "_ollama_up", lambda: False)
    db.init_db()
    yield
