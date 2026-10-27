from pathlib import Path

from app import db
from app.config import SAMPLE_JDS


def seed_if_empty() -> None:
    db.init_db()
    if db.fetchone("SELECT id FROM jobs LIMIT 1"):
        return
    for path in sorted(SAMPLE_JDS.glob("*.md")):
        title, client = _title_client(path)
        db.insert_job(title, client, path.read_text(encoding="utf-8"))


def _title_client(path: Path) -> tuple[str, str]:
    lines = path.read_text(encoding="utf-8").splitlines()
    title = path.stem.replace("_", " ").title()
    client = "Demo Client"
    for ln in lines:
        if ln.startswith("# "):
            title = ln[2:].strip()
        if ln.lower().startswith("**client:**"):
            client = ln.split(":", 1)[1].replace("*", "").strip()
    return title, client
