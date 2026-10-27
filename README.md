<div align="center">

<img src="https://readme-typing-svg.demolab.com?font=Fira+Code&size=32&duration=2800&pause=2000&color=6366F1&center=true&vCenter=true&width=940&lines=TalentOps+AI+%F0%9F%A4%96;Next-Gen+AI+Recruitment+Automation;Autonomous+Talent+Intelligence+%F0%9F%9A%80" alt="Typing SVG" />

<br/>

<img src="https://capsule-render.vercel.app/api?type=waving&color=gradient&customColorList=6,11,20&height=180&section=header&text=TalentOps%20AI&fontSize=42&fontColor=fff&animation=twinkling&fontAlignY=32&desc=Resume%20→%20Parse%20→%20Score%20→%20Screen%20→%20Schedule&descAlignY=55&descAlign=50" width="100%"/>

<br/>

<!-- Badges Row 1 -->
<p>
  <img src="https://img.shields.io/badge/Python-3.10%2B-3776AB?style=for-the-badge&logo=python&logoColor=white"/>
  <img src="https://img.shields.io/badge/FastAPI-0.111+-009688?style=for-the-badge&logo=fastapi&logoColor=white"/>
  <img src="https://img.shields.io/badge/SQLite-003B57?style=for-the-badge&logo=sqlite&logoColor=white"/>
  <img src="https://img.shields.io/badge/Gemini-Free%20Tier-4285F4?style=for-the-badge&logo=google&logoColor=white"/>
</p>

<!-- Badges Row 2 -->
<p>
  <img src="https://img.shields.io/badge/Tests-40%20passing-22c55e?style=for-the-badge&logo=pytest&logoColor=white"/>
  <img src="https://img.shields.io/badge/Commits-167%2B-f59e0b?style=for-the-badge&logo=git&logoColor=white"/>
  <img src="https://img.shields.io/badge/LLM%20Providers-4%20%2B%20heuristic-8b5cf6?style=for-the-badge&logo=openai&logoColor=white"/>
  <img src="https://img.shields.io/badge/License-MIT-red?style=for-the-badge"/>
</p>

<!-- Badges Row 3 -->
<p>
  <img src="https://img.shields.io/badge/No%20API%20Key%20Required-Heuristic%20Fallback-10b981?style=for-the-badge&logo=checkmarx&logoColor=white"/>
  <img src="https://img.shields.io/badge/BRD%20Coverage-F101%20→%20F502-6366f1?style=for-the-badge"/>
</p>

<br/>

> **🎯 Autonomous AI Recruitment & Candidate Pipeline Automation Platform.**
> The AI funnel is **real and running**. Enterprise connectors are mocked and fully specced.

<br/>

</div>

---

## 🎬 See It In Action

<div align="center">

```
┌─────────────────────────────────────────────────────────────────────┐
│  📄 Upload PDF/DOCX/TXT  →  🧠 LLM Parse  →  📊 Score 0-100%       │
│  💬 4-Question Chat Screen  →  📅 Book Slot  →  📊 Excel MIS        │
└─────────────────────────────────────────────────────────────────────┘
```

<img src="https://raw.githubusercontent.com/Anmol-Baranwal/Cool-GIFs-For-GitHub/main/Icons/Rocket/Rocket.gif" width="40"/>

</div>

> Open `http://127.0.0.1:8080` after setup → click **Ingest sample resumes** → watch 10 Indian CVs become structured pipeline rows in under 10 seconds.

---

## 📋 Table of Contents

<div align="center">

| | Section |
|---|---|
| ⚡ | [What This Is](#-what-this-is) |
| 🏗️ | [Architecture](#️-architecture) |
| ✨ | [Features](#-features) |
| 🔑 | [Keys & LLM Setup](#-keys--llm-setup) |
| 🚀 | [Quick Start](#-quick-start) |
| 📡 | [API Reference](#-api-reference) |
| 🆚 | [Real vs Mocked](#-real-vs-mocked) |
| 🗺️ | [BRD Coverage Map](#️-brd-coverage-map) |
| 🧪 | [Tests](#-tests) |
| 📂 | [Project Structure](#-project-structure) |
| 📚 | [Documentation](#-documentation) |
| 💰 | [Cost at Scale](#-cost-at-scale) |
| 🤝 | [Contributing](#-contributing) |

</div>

---

## ⚡ What This Is

<div align="center">
<img src="https://raw.githubusercontent.com/Anmol-Baranwal/Cool-GIFs-For-GitHub/main/Icons/Arrow/Arrow-Right.gif" width="30"/>
</div>

TalentOps AI automates high-volume recruitment pipelines across an end-to-end **6-module enterprise architecture** spanning CEIPAL, Naukri, LinkedIn, WhatsApp, Google/M365, Kredily, TeamLogger, TallyPrime, and CredFlow.

This repo implements **the complete AI intelligence and automation layer**:

| Module | What it covers | Status |
|---|---|---|
| **Module 1** | Resume ingest + structured parse (BRD-F-201) | ✅ **Built & running** |
| **Module 2** | Fitment scoring 0–100% + auto-tagging (BRD-F-202/203) | ✅ **Built & running** |
| **Module 3** | 4-question chat screen + mock calendar (BRD-F-301/302/303) | ✅ **Built & running** |
| **Module 5** | Executive dashboard + 3-sheet Excel MIS (BRD-F-501/502) | ✅ **Built & running** |
| **Module 4** | HR productivity sync (Kredily/TeamLogger) | 📄 Specced in [MODULE_4_6_NOTES.md](docs/MODULE_4_6_NOTES.md) |
| **Module 6** | Finance/commission (Tally/CredFlow) | 📄 Specced in [MODULE_4_6_NOTES.md](docs/MODULE_4_6_NOTES.md) |

---

## 🏗️ Architecture

```
┌──────────────────────────────────────────────────────────────────────────┐
│                         TalentOps AI — Request Flow                       │
├──────────────────────────────────────────────────────────────────────────┤
│                                                                            │
│   Browser (Vanilla JS 4-tab UI)                                           │
│       │                                                                    │
│       ▼                                                                    │
│   FastAPI (app/main.py)  ──►  Pydantic validation  ──►  SQLite (db.py)   │
│       │                                                                    │
│       ├──► app/parser.py    PDF/DOCX/TXT → 14-field JSON                 │
│       │         │                                                          │
│       │         ▼                                                          │
│       │    LLM Router (app/llm.py)                                        │
│       │    ┌──────────────────────────────────────────┐                   │
│       │    │ 1. Gemini (free)  → GEMINI_API_KEY       │                   │
│       │    │ 2. Anthropic      → ANTHROPIC_API_KEY    │                   │
│       │    │ 3. Groq Llama     → GROQ_API_KEY         │                   │
│       │    │ 4. Ollama (local) → no key               │                   │
│       │    │ 5. Heuristic      → always works         │                   │
│       │    └──────────────────────────────────────────┘                   │
│       │                                                                    │
│       ├──► app/scorer.py    Fitment 0–100% + 3-bullet summary             │
│       ├──► app/chat_agent.py  4-question screening + slot booking         │
│       ├──► app/scheduler.py  Mock calendar + reminder queue               │
│       ├──► app/dashboard.py  KPI aggregation                              │
│       ├──► app/dossier.py    AI-generated submission brief                │
│       └──► app/excel_export.py  3-sheet BRD-F-502 MIS                    │
│                                                                            │
└──────────────────────────────────────────────────────────────────────────┘
```

---

## ✨ Features

<div align="center">
<img src="https://raw.githubusercontent.com/Anmol-Baranwal/Cool-GIFs-For-GitHub/main/Icons/Star/Star.gif" width="30"/>
</div>

### 🧠 AI-Powered Resume Intelligence
- Parses **PDF, DOCX, and plain text** — including messy, unformatted CVs
- Extracts **14 structured fields**: name, email, phone, location, CTC (current + expected), notice period, skills, experience, education, LinkedIn, GitHub, and more
- **Multi-LLM fallback chain** — switches providers automatically; heuristic ensures zero-downtime even with no API key
- Email/phone/LinkedIn **deduplication** (stand-in for CEIPAL's dedup logic)

### 📊 Semantic Fitment Scoring
- **0–100% fitment score** per candidate per JD
- **≥70 → auto-tagged "Screened – AI Fit"** (BRD-F-203 stage transition)
- **3-bullet AI summary** explaining *why* — not just a number
- Per-candidate score history with full audit trail

### 💬 AI Screening Chat
- **4 qualification gates**: employment status, notice period, CTC, relocation
- LLM path: natural conversation that reflects candidate answers back
- Scripted fallback: deterministic flow if LLM is unavailable
- **Hinglish detection** — ready for India's bilingual recruitment reality
- Warm, branded close: "You're all set, [Name]! Interview confirmed: …"

### 📅 Interview Scheduling
- Mock **3-way calendar** (candidate + interviewer + recruiter)
- Slot booking with conflict prevention (already-booked slots disappear)
- **T-24h / T-2h / T-15m reminder queue** (mock WhatsApp dispatch)
- Clear visual: booked → slot removed from available list

### 📊 Executive Dashboard & MIS
- Live KPIs: sourced, AI Fit, avg score, interviews, reminders, TTF estimate
- Funnel charts: by status, by channel, interview pipeline
- Recruiter activity table (mocked Kredily + TeamLogger data)
- **3-sheet Excel MIS** (BRD-F-502 exact column spec):
  - Sheet 1: Master Daily Pipeline
  - Sheet 2: Recruiter KPI Leaderboard
  - Sheet 3: Channel Performance Matrix

### 🔍 Advanced Search & Collaboration
- Fast substring search across name, skills, company, email
- **Recruiter notes** per candidate (timestamped, author-tagged)
- **Skill tags** — attach, list, remove
- **Pipeline timeline** — every status change with timestamp
- **AI dossier** — one-click submission brief for clients

---

## 🔑 Keys & LLM Setup

<div align="center">

| Provider | Env Var | Cost | Get It |
|---|---|---|---|
| 🟢 **Gemini** (recommended free) | `GEMINI_API_KEY` | Free tier | [aistudio.google.com/apikey](https://aistudio.google.com/apikey) |
| 🟡 Groq Llama | `GROQ_API_KEY` | Free tier | [console.groq.com/keys](https://console.groq.com/keys) |
| 🟠 Ollama (local) | none needed | Free | [ollama.com](https://ollama.com) |
| 🔵 Anthropic Claude | `ANTHROPIC_API_KEY` | Paid | [console.anthropic.com](https://console.anthropic.com/settings/keys) |
| ⚪ **Heuristic fallback** | none | Always free | Built-in — zero config |

</div>

> **⚠️ No key required to run.** Set `LLM_PROVIDER=auto` (the default) and the system falls through to heuristic. Add any free key for richer AI output.

**No free workaround for:** CEIPAL · Naukri/Shine · LinkedIn Recruiter · WhatsApp Business · Google/M365 Calendar · Kredily · TeamLogger · TallyPrime · CredFlow → see [docs/SCOPE_AND_GAPS.md](docs/SCOPE_AND_GAPS.md)

---

## 🚀 Quick Start

<div align="center">
<img src="https://raw.githubusercontent.com/Anmol-Baranwal/Cool-GIFs-For-GitHub/main/Icons/Arrow/Down-Arrow.gif" width="30"/>
</div>

### Prerequisites

| Requirement | Version | Check |
|---|---|---|
| Python | ≥ 3.10 (3.11 recommended) | `python --version` |
| Git | Any | `git --version` |
| RAM | ≥ 2 GB | — |

### Installation

```bash
# 1 — Clone
git clone https://github.com/Anshul-an/talentops-ai.git
cd talentops-ai

# 2 — Virtual environment
python -m venv .venv

# Windows PowerShell
.\.venv\Scripts\Activate.ps1

# macOS / Linux
source .venv/bin/activate

# 3 — Dependencies
pip install -r requirements.txt

# 4 — Generate sample data
python scripts/generate_samples.py

# 5 — Environment (copy and optionally add a free LLM key)
copy .env.example .env        # Windows
# cp .env.example .env        # macOS/Linux

# 6 — Run
uvicorn app.main:app --reload --port 8080
```

Open **[http://127.0.0.1:8080](http://127.0.0.1:8080)** 🎉

> **Port note:** If 8080 is also in use, try `--port 8000` or any free port.

### One-command demo flow

```
1. Click "Ingest sample resumes"          # 10 CVs → structured rows
2. Select JD → Click "Score all"          # Fitment 0-100%, AI Fit tags
3. Click any candidate → Screening desk   # 4-question chat, slot booking
4. Executive MIS tab → Download Excel     # BRD-F-502 three-sheet MIS
```

### Run tests

```bash
pytest                      # 40 tests
pytest -v                   # verbose
pytest tests/test_parser.py # single file
```

---

## 📡 API Reference

> Full interactive docs at **[http://127.0.0.1:8080/docs](http://127.0.0.1:8080/docs)** (Swagger UI)

<details>
<summary><strong>📄 Resume & Candidate Endpoints</strong></summary>

| Method | Path | Purpose |
|---|---|---|
| `POST` | `/api/resumes/upload` | Upload PDF/DOCX/TXT files |
| `POST` | `/api/resumes/ingest-samples` | Parse `data/sample_resumes/` |
| `GET` | `/api/candidates` | List candidates (`?status=` `?source=`) |
| `GET` | `/api/candidates/{id}` | Full record + chat + scores |
| `DELETE` | `/api/candidates/{id}` | Soft-delete candidate |
| `GET` | `/api/candidates/{id}/timeline` | Stage-change audit trail |
| `GET` | `/api/candidates/{id}/dossier` | AI-generated submission brief |
| `GET` | `/api/candidates/{id}/score-history` | Per-candidate score history |
| `POST` | `/api/candidates/search/advanced` | Structured search with filters |

</details>

<details>
<summary><strong>📝 Notes & Tags</strong></summary>

| Method | Path | Purpose |
|---|---|---|
| `POST` | `/api/candidates/{id}/notes` | Add recruiter note |
| `GET` | `/api/candidates/{id}/notes` | List notes |
| `POST` | `/api/candidates/{id}/tags` | Add skill tag |
| `GET` | `/api/candidates/{id}/tags` | List tags |
| `DELETE` | `/api/candidates/{id}/tags/{tag}` | Remove tag |

</details>

<details>
<summary><strong>💼 Jobs & Scoring</strong></summary>

| Method | Path | Purpose |
|---|---|---|
| `GET` | `/api/jobs` | List job descriptions |
| `POST` | `/api/jobs` | Create JD |
| `POST` | `/api/jobs/{id}/archive` | Archive a job |
| `GET` | `/api/jobs/{id}/candidates` | Candidates for a JD |
| `POST` | `/api/score` | `{ "job_id": 1 }` — score all |

</details>

<details>
<summary><strong>💬 Chat & Scheduling</strong></summary>

| Method | Path | Purpose |
|---|---|---|
| `POST` | `/api/chat/{candidate_id}` | `{ "message": "..." }` |
| `POST` | `/api/chat/{candidate_id}/reset` | Clear session + history |
| `GET` | `/api/interviews` | Open slots + booked interviews |
| `POST` | `/api/interviews/book/{candidate_id}` | `?slot_id=slot-mon-1500` |
| `POST` | `/api/interviews/propose/{id}` | Propose free slots |
| `POST` | `/api/interviews/confirm/{id}` | confirm / reschedule / noshow |
| `POST` | `/api/reminders/dispatch` | Mock-dispatch queued reminders |

</details>

<details>
<summary><strong>📊 Dashboard & Export</strong></summary>

| Method | Path | Purpose |
|---|---|---|
| `GET` | `/api/dashboard/summary` | KPI JSON |
| `GET` | `/api/health` | Engine status |
| `GET` | `/api/export/excel` | 3-sheet BRD-F-502 workbook |
| `GET` | `/api/export/csv` | Candidates CSV |

</details>

---

## 🆚 Real vs Mocked

<div align="center">

| Component | Status | Notes |
|---|---|---|
| 📄 PDF/DOCX/TXT text extract + field mapping | ✅ **Real** | pdfplumber + python-docx |
| 🧠 LLM parse / score / chat | ✅ **Real** | Gemini, Anthropic, Groq, Ollama, or heuristic |
| ⚡ Heuristic fallback (zero-key demo) | ✅ **Real** | Always runs |
| 🗄️ SQLite candidate store + dedup | ✅ **Real** | Stand-in for CEIPAL |
| 🏷️ Fitment threshold tagging | ✅ **Real** | BRD-F-203 |
| 💬 Screening conversation | ✅ **Real UI** | Web UI (not WhatsApp) |
| 📊 Excel MIS 3 sheets | ✅ **Real** | BRD-F-502 columns |
| 📅 Interview calendar | 🟡 **Mock** | `data/mock_calendar.json` |
| 📱 WhatsApp reminders | 🟡 **Mock** | Queued locally; Meta API documented |
| 👥 Recruiter KPI (Kredily/TeamLogger) | 🟡 **Mock** | `data/mock_recruiters.json` |
| 🔐 Role-based dashboard access | ❌ **Not built** | No auth layer; see SCOPE_AND_GAPS |
| 🔗 CEIPAL / Naukri / LinkedIn API | ❌ **Not called** | Documented in MODULE_4_6_NOTES |
| 💰 TallyPrime / CredFlow / Commission | ❌ **Not called** | Specced in MODULE_4_6_NOTES |

</div>

Full gap analysis → **[docs/SCOPE_AND_GAPS.md](docs/SCOPE_AND_GAPS.md)**

---

## 🗺️ BRD Coverage Map

<div align="center">

| BRD Ref | Requirement | Implementation |
|---|---|---|
| **F-101** | Multi-job-board aggregation | 🟡 `source_channel` field; see SCOPE_AND_GAPS |
| **F-102** | Candidate de-duplication | ✅ `db.upsert_candidate()` — email/phone/LinkedIn |
| **F-201** | Resume structured parse (14 fields) | ✅ `app/parser.py` — PDF/DOCX/TXT |
| **F-202** | Fitment scoring | ✅ LLM-scored JSON + keyword heuristic |
| **F-203** | ATS stage transition | ✅ `status = "Screened – AI Fit"` |
| **F-301** | 4 qualification questions | ✅ `app/chat_agent.py` |
| **F-302** | 3-way calendar orchestration | 🟡 `data/mock_calendar.json` |
| **F-303** | T-24h/T-2h/T-15m reminders | ✅ Queued in SQLite |
| **F-401/402** | Recruiter productivity | 🟡 Mock + spec in MODULE_4_6_NOTES |
| **F-501** | Executive dashboard | ✅ `app/dashboard.py` |
| **F-502** | 3-sheet Excel MIS | ✅ `app/excel_export.py` |
| **F-601/602/603** | Finance/commission | 📄 Specced in MODULE_4_6_NOTES |

</div>

---

## 🧪 Tests

```bash
pytest                          # run all 40 tests
pytest -v --tb=short            # verbose with short tracebacks
pytest tests/test_parser.py     # parser only
pytest tests/test_scorer.py     # scorer only
pytest tests/test_chat.py       # chat agent only
pytest -k "not slow"            # skip slow LLM tests
```

| Test File | Coverage |
|---|---|
| `test_parser.py` | Resume parsing, field extraction, heuristic |
| `test_scorer.py` | Fitment scoring, threshold, bullets |
| `test_chat.py` | 4-question flow, slot extraction, fallback |
| `test_scheduler.py` | Slot booking, conflicts, reminders |
| `test_dashboard.py` | KPI aggregation, funnel, Excel export |
| `test_db.py` | CRUD, dedup, soft-delete, timeline |
| `test_dossier.py` | Dossier generation, markdown output |
| `test_api.py` | API endpoints, validation, status codes |
| `test_llm.py` | Multi-provider fallback chain |

---

## 📂 Project Structure

```
talentops-ai/
├── app/
│   ├── main.py            # FastAPI routes (40+ endpoints)
│   ├── parser.py          # Resume → 14-field JSON
│   ├── scorer.py          # Fitment 0-100% + bullets
│   ├── chat_agent.py      # 4-question screening + booking
│   ├── scheduler.py       # Mock calendar + reminder queue
│   ├── dashboard.py       # KPI aggregation
│   ├── dossier.py         # AI submission brief
│   ├── excel_export.py    # 3-sheet BRD-F-502 MIS
│   ├── db.py              # SQLite data layer
│   ├── llm.py             # Multi-provider LLM router
│   ├── models.py          # Pydantic schemas
│   ├── config.py          # Env var loading
│   ├── constants.py       # Shared constants
│   └── logging_config.py  # Structured JSON logging
├── frontend/
│   ├── index.html         # 4-tab UI shell
│   ├── app.js             # Vanilla JS (417 lines)
│   └── styles.css         # UI styles + dark mode
├── data/
│   ├── sample_resumes/    # 10 fictional Indian CVs (PDF/DOCX/TXT)
│   ├── sample_jds/        # 2 sample job descriptions
│   ├── mock_calendar.json # Mock interview slots
│   └── mock_recruiters.json
├── docs/
│   ├── ENGINEERING_REVIEW.md  # 4-panel, 15-expert, 107-issue review
│   ├── ARCHITECTURE.md
│   ├── MODULE_4_6_NOTES.md    # Kredily/TeamLogger/Tally/CredFlow specs
│   ├── SCOPE_AND_GAPS.md      # BRD gap analysis
│   ├── DEMO_SCRIPT.md         # 5-min demo with Q&A
│   ├── CHAT_WALKTHROUGH.md    # Sample conversation + rejection path
│   └── KEYS_AND_SETUP.md
├── tests/                 # 9 files, 40 tests
├── scripts/
│   └── generate_samples.py
├── .env.example           # All vars documented, none required
├── requirements.txt
├── pytest.ini
├── Makefile
└── .editorconfig
```

---

## 💰 Cost at Scale

> Running on **Gemini 1.5 Flash** (free tier → then `$0.15/1M tokens`):

| Scale | Parse | Score | Chat | **Monthly total** |
|---|---|---|---|---|
| 100 resumes/month | ~\$0.001 | ~\$0.002 | ~\$0.005 | **< \$0.01** |
| 1,000 resumes/month | ~\$0.01 | ~\$0.02 | ~\$0.05 | **~\$0.08** |
| 10,000 resumes/month | ~\$0.10 | ~\$0.20 | ~\$0.50 | **~\$0.80** |
| 100,000 resumes/month | ~\$1.00 | ~\$2.00 | ~\$5.00 | **~\$8.00** |

*At typical staffing/agency volume (500–2,000 resumes/month): well under \$1/month on Gemini. Switching to Anthropic Claude multiplies cost ~5×.*

---

## 📚 Documentation

<div align="center">

| Document | Purpose |
|---|---|
| [🚀 Quick Start](#-quick-start) | Get running in 5 minutes |
| [🔑 KEYS_AND_SETUP.md](docs/KEYS_AND_SETUP.md) | Free LLM key setup, step by step |
| [🏗️ ARCHITECTURE.md](docs/ARCHITECTURE.md) | System design, data flow, module map |
| [🗺️ MODULE_4_6_NOTES.md](docs/MODULE_4_6_NOTES.md) | Integration roadmap for Modules 4 & 6 |
| [📋 SCOPE_AND_GAPS.md](docs/SCOPE_AND_GAPS.md) | BRD feature gaps — what's built vs specced |
| [🎬 DEMO_SCRIPT.md](docs/DEMO_SCRIPT.md) | 5-min live demo with narration & Q&A |
| [💬 CHAT_WALKTHROUGH.md](docs/CHAT_WALKTHROUGH.md) | Sample chat conversation + rejection path |
| [🔍 ENGINEERING_REVIEW.md](docs/ENGINEERING_REVIEW.md) | 4-panel, 15-expert, 107-issue code review |

</div>

---

## 🛠️ Tech Stack

<div align="center">

<img src="https://img.shields.io/badge/Python-3776AB?style=flat-square&logo=python&logoColor=white"/>
<img src="https://img.shields.io/badge/FastAPI-009688?style=flat-square&logo=fastapi&logoColor=white"/>
<img src="https://img.shields.io/badge/SQLite-003B57?style=flat-square&logo=sqlite&logoColor=white"/>
<img src="https://img.shields.io/badge/Pydantic-E92063?style=flat-square&logo=pydantic&logoColor=white"/>
<img src="https://img.shields.io/badge/Google%20Gemini-4285F4?style=flat-square&logo=google&logoColor=white"/>
<img src="https://img.shields.io/badge/Anthropic-412991?style=flat-square&logo=anthropic&logoColor=white"/>
<img src="https://img.shields.io/badge/Groq-F55036?style=flat-square&logo=groq&logoColor=white"/>
<img src="https://img.shields.io/badge/Ollama-000000?style=flat-square&logo=ollama&logoColor=white"/>
<img src="https://img.shields.io/badge/pandas-150458?style=flat-square&logo=pandas&logoColor=white"/>
<img src="https://img.shields.io/badge/openpyxl-217346?style=flat-square&logo=microsoftexcel&logoColor=white"/>
<img src="https://img.shields.io/badge/pdfplumber-red?style=flat-square"/>
<img src="https://img.shields.io/badge/pytest-0A9EDC?style=flat-square&logo=pytest&logoColor=white"/>
<img src="https://img.shields.io/badge/Uvicorn-499848?style=flat-square"/>
<img src="https://img.shields.io/badge/Vanilla%20JS-F7DF1E?style=flat-square&logo=javascript&logoColor=black"/>

</div>

---

## 🗺️ Roadmap

- [x] Multi-LLM fallback chain (Gemini / Anthropic / Groq / Ollama / Heuristic)
- [x] Resume parse → 14 fields (PDF / DOCX / TXT)
- [x] Fitment scoring 0-100% with 3-bullet summary
- [x] 4-question screening chat + slot booking
- [x] Executive dashboard + 3-sheet Excel MIS
- [x] Recruiter notes + tags + pipeline timeline
- [x] AI submission dossier
- [ ] `sentence-transformers` vector embeddings (BRD-F-202 true compliance)
- [ ] Google / M365 OAuth calendar integration (BRD-F-302)
- [ ] Kredily / TeamLogger webhook (Module 4)
- [ ] TallyPrime XML-over-HTTP + CredFlow aging (Module 6)
- [ ] CEIPAL REST stage-transition API
- [ ] Role-based dashboard access (CEO / Practice Head / Recruiter / Ops)
- [ ] Meta WhatsApp Business API for reminders

---

## 👤 Author

<div align="center">

**Anshul Maravi**

[![GitHub](https://img.shields.io/badge/GitHub-Anshul--an-181717?style=for-the-badge&logo=github)](https://github.com/Anshul-an)
[![Email](https://img.shields.io/badge/Email-maravianshul01%40gmail.com-EA4335?style=for-the-badge&logo=gmail&logoColor=white)](mailto:maravianshul01@gmail.com)

*Designed and developed as an autonomous recruitment intelligence platform.*
*Scoping philosophy: build production-ready core engines; spec and mock enterprise connectors.*

</div>

---

<div align="center">

<img src="https://capsule-render.vercel.app/api?type=waving&color=gradient&customColorList=6,11,20&height=120&section=footer&animation=twinkling" width="100%"/>

<img src="https://readme-typing-svg.demolab.com?font=Fira+Code&size=14&duration=3000&pause=1000&color=6366F1&center=true&vCenter=true&width=600&lines=If+this+helped%2C+drop+a+%E2%AD%90+—+it+means+a+lot!;Built+with+%F0%9F%A4%96+AI+%2B+%E2%9D%A4%EF%B8%8F+for+Modern+Recruiting" alt="Footer typing" />

</div>
