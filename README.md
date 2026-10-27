# TalentOps AI

Scoped prototype of the **Next-Gen AI Recruitment** platform described in Virtuous Advisors’ BRD. Built as a verifiable internship demo: the AI funnel is real; paid enterprise connectors are mocked and documented.

## What this is

Virtuous’ BRD is a 16-week enterprise build across CEIPAL, Naukri/LinkedIn, WhatsApp, Google/M365, Kredily, TeamLogger, TallyPrime, and CredFlow. This repo implements the part an intern can actually run without those admin accounts:

1. Resume ingest + structured parse (BRD-F-201)
2. Semantic fitment 0–100% + 3-bullet summary (BRD-F-202) and auto-tag **Screened – AI Fit** (BRD-F-203)
3. Screening chat + mock 3-way calendar (BRD-F-301/302/303)
4. Executive dashboard and a 3-sheet Excel MIS (BRD-F-501/502)

Modules 4 and 6 (productivity correlation and finance) are specified in [docs/MODULE_4_6_NOTES.md](docs/MODULE_4_6_NOTES.md), not live-integrated.

## What’s real vs mocked

| Piece | Status |
| --- | --- |
| PDF/DOCX/TXT text extract + field mapping | **Real** |
| LLM parse / score / chat | **Real** via Anthropic, or free Gemini / Groq / Ollama, else heuristic |
| Heuristic fallback so the demo runs without a key | **Real** |
| SQLite candidate store + email/phone/LinkedIn de-dupe | **Real** (stand-in for CEIPAL) |
| Fitment threshold tagging | **Real** |
| Screening conversation + slot booking | **Real UI**, mocked WhatsApp |
| Interview calendar | **Mock** JSON (`data/mock_calendar.json`) |
| Recruiter KPI hours | **Mock** Kredily / TeamLogger |
| CEIPAL, TallyPrime, CredFlow, Meta WhatsApp, Graph/Google Calendar | **Not called** — see integration notes |

## Keys (read this)

- **Required to run:** none (`LLM_PROVIDER=auto` falls through to heuristic).
- **Preferred LLM:** Anthropic — [console.anthropic.com/settings/keys](https://console.anthropic.com/settings/keys) → `ANTHROPIC_API_KEY`.
- **Free workarounds:** Gemini ([aistudio.google.com/apikey](https://aistudio.google.com/apikey) → `GEMINI_API_KEY`), Groq ([console.groq.com/keys](https://console.groq.com/keys) → `GROQ_API_KEY`), or local Ollama ([ollama.com](https://ollama.com), no key).
- **No free workaround:** CEIPAL, Naukri/Shine, LinkedIn Recruiter, WhatsApp Business, Google/M365 calendars, Kredily, TeamLogger, TallyPrime, CredFlow.

Exact steps: **[docs/KEYS_AND_SETUP.md](docs/KEYS_AND_SETUP.md)**.

## Quick start

```powershell
cd "C:\Users\lenovo\Desktop\Virtuous automation\talentops-ai"
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python scripts\generate_samples.py
copy .env.example .env
# optional free LLM: GEMINI_API_KEY or GROQ_API_KEY, or run Ollama
# optional preferred: ANTHROPIC_API_KEY
uvicorn app.main:app --reload --port 8000
```

Open [http://127.0.0.1:8000](http://127.0.0.1:8000).

1. Ingest sample resumes  
2. Score against a job description  
3. Screen a candidate in chat and book `slot-mon-1500`  
4. Download `TalentOps_MIS.xlsx`

```powershell
pytest
```

## API (also in the UI)

| Method | Path | Purpose |
| --- | --- | --- |
| POST | `/api/resumes/upload` | Upload PDF/DOCX |
| POST | `/api/resumes/ingest-samples` | Parse `data/sample_resumes/` |
| GET | `/api/candidates` | List, `?status=` `?source=` |
| GET | `/api/candidates/{id}` | Full record + chat + scores |
| GET/POST | `/api/jobs` | List / create JDs |
| POST | `/api/score` | `{ "job_id": 1 }` |
| POST | `/api/chat/{candidate_id}` | `{ "message": "..." }` |
| POST | `/api/interviews/propose/{id}` | Mock free slots |
| POST | `/api/interviews/confirm/{id}` | confirm / reschedule / noshow |
| GET | `/api/dashboard/summary` | KPI JSON |
| GET | `/api/export/excel` | Three-sheet workbook |

Spec paths from the build plan (`/candidates`, `/score`, `/chat/{id}`, …) are registered as aliases without the `/api` prefix.

## Stack

Python 3.11, FastAPI, SQLite, Anthropic Claude, pandas/openpyxl, vanilla HTML UI.

## Docs

- [Architecture](docs/ARCHITECTURE.md)
- [Modules 4 & 6 API map](docs/MODULE_4_6_NOTES.md)
- [Demo script](docs/DEMO_SCRIPT.md)
- [Keys and setup](docs/KEYS_AND_SETUP.md)


## Enhanced Capabilities
- **Candidate Search**: Fast substring search across name, skills, company, email.
- **Recruiter Notes & Tags**: Attach collaboration notes and skill tags directly to candidate profiles.
- **Pipeline Velocity & Channel ROI**: Live metrics tracking recruitment cycle times and spend per hire.
- **CSV & Excel Export**: Dual export formats for CRM synchronization and offline analysis.
