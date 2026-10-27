from pathlib import Path
import os

from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parent.parent
load_dotenv(ROOT / ".env")

DATABASE_PATH = Path(os.getenv("DATABASE_PATH", ROOT / "talentops.db"))
if not DATABASE_PATH.is_absolute():
    DATABASE_PATH = ROOT / DATABASE_PATH

UPLOAD_DIR = Path(os.getenv("UPLOAD_DIR", ROOT / "uploads"))
if not UPLOAD_DIR.is_absolute():
    UPLOAD_DIR = ROOT / UPLOAD_DIR
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

DATA_DIR = ROOT / "data"
SAMPLE_RESUMES = DATA_DIR / "sample_resumes"
SAMPLE_JDS = DATA_DIR / "sample_jds"
MOCK_CALENDAR = DATA_DIR / "mock_calendar.json"
MOCK_RECRUITERS = DATA_DIR / "mock_recruiters.json"

# auto = first configured provider (anthropic, gemini, groq, ollama), else heuristic
LLM_PROVIDER = os.getenv("LLM_PROVIDER", "auto").strip().lower() or "auto"

ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "").strip()
CLAUDE_MODEL = os.getenv("CLAUDE_MODEL", "claude-sonnet-4-5")

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "").strip()
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.0-flash")

GROQ_API_KEY = os.getenv("GROQ_API_KEY", "").strip()
GROQ_MODEL = os.getenv("GROQ_MODEL", "llama-3.1-8b-instant")

OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://127.0.0.1:11434").rstrip("/")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3.2")

FITMENT_THRESHOLD = float(os.getenv("FITMENT_THRESHOLD", "70"))
FRONTEND_DIR = ROOT / "frontend"

SCORER_LOCATION_BONUS = float(os.getenv("SCORER_LOCATION_BONUS", "5.0"))
SCORER_GAP_PENALTY = float(os.getenv("SCORER_GAP_PENALTY", "8.0"))

LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()

MAX_UPLOAD_SIZE_MB = int(os.getenv("MAX_UPLOAD_SIZE_MB", "15"))
