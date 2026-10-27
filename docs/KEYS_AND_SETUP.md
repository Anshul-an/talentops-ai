# Keys and setup

This system **runs with zero API keys** (heuristic parse / score / chat). You can optionally plug in an LLM. **Gemini, Groq, and Ollama provide zero-cost LLM backends**, and Anthropic Claude is supported for high-precision inference.

CEIPAL, WhatsApp, Naukri, Tally, Kredily, TeamLogger, CredFlow, and Google/M365 calendars have **no free production workaround**. Those stay mocked. See [MODULE_4_6_NOTES.md](MODULE_4_6_NOTES.md).

Never commit `.env`. Copy `.env.example` → `.env` and paste real values only.

---

## Required to run locally

**None.**

```powershell
cd talentops-ai
copy .env.example .env
.\.venv\Scripts\Activate.ps1
uvicorn app.main:app --reload --port 8080
```

Open http://127.0.0.1:8000 — header shows the active engine (`heuristic` if no keys).

---

## Pick a provider

Set in `.env`:

```
LLM_PROVIDER=auto
```

Allowed values: `auto` | `anthropic` | `gemini` | `groq` | `ollama` | `heuristic`

**`auto` order:** Anthropic → Gemini → Groq → Ollama (if the local daemon is up) → heuristic.

To force a free path even if you later add an Anthropic key, set `LLM_PROVIDER=gemini` (or `groq` / `ollama`).

---

## Optional LLMs (Cloud and Local)

### 1. Anthropic Claude (preferred, not free)

| | |
| --- | --- |
| Env | `ANTHROPIC_API_KEY` |
| Model | `CLAUDE_MODEL=claude-sonnet-4-5` |
| Signup / key | [https://console.anthropic.com/settings/keys](https://console.anthropic.com/settings/keys) |

Paste `ANTHROPIC_API_KEY=sk-ant-…` into `.env`, restart uvicorn. Header: **anthropic**.

### 2. Google Gemini (free-tier workaround)

| | |
| --- | --- |
| Env | `GEMINI_API_KEY` |
| Model | `GEMINI_MODEL=gemini-2.0-flash` |
| Get a key | [https://aistudio.google.com/apikey](https://aistudio.google.com/apikey) |

1. Open Google AI Studio, sign in with a Google account.
2. Create API key (free tier; Google may ask you to enable the Generative Language API).
3. Paste `GEMINI_API_KEY=…` into `.env`.
4. Restart uvicorn. With `LLM_PROVIDER=auto` and no Anthropic key, Gemini is used.

### 3. Groq + Llama (free-tier workaround)

| | |
| --- | --- |
| Env | `GROQ_API_KEY` |
| Model | `GROQ_MODEL=llama-3.1-8b-instant` |
| Get a key | [https://console.groq.com/keys](https://console.groq.com/keys) |

1. Create a Groq Cloud account.
2. API Keys → Create. Copy `gsk_…`.
3. Paste `GROQ_API_KEY=…` into `.env`. If Gemini is also set and `LLM_PROVIDER=auto`, Gemini wins — set `LLM_PROVIDER=groq` to force Groq.
4. If Groq renamed the model, pick a current Llama id from their console.

### 4. Ollama on your laptop (no cloud key)

| | |
| --- | --- |
| Env | `OLLAMA_BASE_URL=http://127.0.0.1:11434`  `OLLAMA_MODEL=llama3.2` |
| Install | [https://ollama.com](https://ollama.com) |

```powershell
# after installing Ollama
ollama pull llama3.2
# leave Ollama running, then:
# .env
LLM_PROVIDER=ollama
OLLAMA_MODEL=llama3.2
```

`auto` only selects Ollama if `http://127.0.0.1:11434/api/tags` responds. First chat may be slow while the model loads.

### 5. Heuristic (always on)

No key. Regex/rules for parse, score, and scripted screening questions. Fine for a walkthrough if you cannot get any LLM key.

---

## Company-only (no free production workaround)

Do not configure these for local standalone mode. This repo **does not call external vendor endpoints**.

| System | BRD use | After joining |
| --- | --- | --- |
| CEIPAL ATS | Candidate/job/placement REST | Enterprise IT token. [ceipal.com](https://www.ceipal.com/) |
| Naukri / Shine | Job-board ingest | Corporate recruiter login. **Do not scrape.** |
| LinkedIn Recruiter | Sourcing | Company Recruiter seat. |
| WhatsApp Business | Screening + reminders | [Meta Cloud API](https://developers.facebook.com/docs/whatsapp/cloud-api) + verified business number. |
| Google Calendar / M365 | Free/busy + Meet/Teams | Workspace / Azure admin consent. |
| Kredily | Attendance / payroll | Employer tenant. |
| TeamLogger | Active/idle time | Org API. |
| TallyPrime | Invoices | XML over HTTP on finance’s Tally. |
| CredFlow | AR / collections | Finance partner API. |

Gemini/Groq/Ollama replace **Claude for parse/score/chat only**. They do not replace CEIPAL or Tally.

---

## Other `.env` knobs (not secrets)

| Variable | Default | Meaning |
| --- | --- | --- |
| `LLM_PROVIDER` | `auto` | Which engine to use |
| `FITMENT_THRESHOLD` | `70` | Score at/above this → `Screened - AI Fit` |
| `DATABASE_PATH` | `talentops.db` | Local SQLite file |
| `UPLOAD_DIR` | `uploads` | Uploaded CVs |
