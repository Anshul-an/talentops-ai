# TalentOps AI architecture

Prototype of Modules 1–3 and 5 from the Virtuous BRD. Modules 4 and 6 are specified in `MODULE_4_6_NOTES.md` and are not implemented against live vendor APIs.

```
[Resume PDF/DOCX/TXT]
        │  parser.py  (Claude JSON extract, heuristic fallback)
        ▼
   SQLite candidates  ←── de-dupe on email / phone / LinkedIn
        │  scorer.py  (domain + recency + stability → 0–100)
        ▼
   scores.status = "Screened - AI Fit" if ≥ threshold
        │  chat_agent.py  (notice / CTC / relocation / employment)
        ▼
   mock calendar  → interviews (Scheduled / Confirmed / Rescheduled)
        │
        ▼
   dashboard + 3-sheet Excel MIS
```

## Mapping to the BRD

| BRD | This repo |
| --- | --- |
| BRD-F-201 resume fields | `parser.py` → `candidates` table |
| BRD-F-202 semantic fitment | `scorer.py` + three bullets |
| BRD-F-203 CEIPAL stage | local status `Screened - AI Fit` (would be a CEIPAL PATCH) |
| BRD-F-102 de-dupe | `db.upsert_candidate` |
| BRD-F-301 screening | `/api/chat/{id}` |
| BRD-F-302/303 calendar | `data/mock_calendar.json` + `scheduler.py` |
| BRD-F-501/502 MIS | `/` dashboard + `/api/export/excel` |

A production CEIPAL integration is mostly a swap of SQLite writes for REST calls on the same fields (`full_name`, CTC, notice, skills, activity notes).

## Runtime

- FastAPI serves `/api/*` and the static UI from `frontend/`.
- Default LLM: Anthropic `claude-sonnet-4-5` when `ANTHROPIC_API_KEY` is set.
- Without a key, parsers, scores, and chat still run so the demo is reviewable offline.


## Additional Endpoints (v0.1.0)
- `GET /api/candidates/search?q=`: Search candidates by full-text query.
- `POST/GET /api/candidates/{id}/notes`: Recruiter notes CRUD.
- `PATCH /api/candidates/{id}/status`: Manual status updates.
- `DELETE /api/candidates/{id}`: Soft-delete candidate.
- `GET/PATCH /api/jobs/{id}`: Job description inspection and editing.
- `POST /api/jobs/{id}/archive`: Soft-archive job mandate.
- `GET /api/dashboard/channel-roi`: Sourcing channel efficiency and cost per acquisition.
- `GET /api/dashboard/pipeline-velocity`: Sourcing stage cycle times.
- `GET /api/export/csv`: Export candidates dataset as CSV.
- `GET /api/version`: Application version and build git sha.
- `GET /api/health/detailed`: Database health and entity counts.
