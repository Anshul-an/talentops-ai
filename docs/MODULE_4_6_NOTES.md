# Modules 4 & 6 — integration notes (not built)

These modules require enterprise admin access to Kredily, TeamLogger, CEIPAL, TallyPrime, and CredFlow. In standalone execution, these connectors are cleanly decoupled and mocked. This architecture specification outlines the exact integration contracts for enterprise deployment.

## Module 4 — Recruiter productivity (CEIPAL + Kredily + TeamLogger)

**Cadence:** a scheduler every 15 minutes (BRD).

**Ingest (keyed by recruiter_id + date):**

1. **Kredily Attendance API** — login, shift, approved leave. This is official presence, not activity.
2. **TeamLogger export / webhook** — active seconds, idle seconds, app/URL categories (ATS vs job boards vs mail).
3. **CEIPAL activity endpoints** — profiles added, screens, client submissions, interviews, closures for the same window.

**Join:** one `activity_to_output` row per recruiter per day:

| recruiter_id | date | login_hours (Kredily) | active_hours (TeamLogger) | idle_hours | sourced | screened | submitted | interviewed | closed |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |

**Time allocation (BRD-F-402):** classify TeamLogger URLs:

- Naukri / LinkedIn / Shine / CEIPAL search → Active Talent Sourcing
- Calls, Meet, dossier docs → Screening & Evaluation
- CEIPAL note/edit screens → Administrative / ATS
- Idle reconciled against logged calls → Idle / Non-Productive

**Anomaly rules (BRD-F-403):**

- `active_hours > 6 AND sourced_count < 2` → high screen time, low sourcing velocity
- `submissions > 0 AND interview_rate < practice baseline` → loose screening / weak JD read
- candidate stuck in `Submitted to Client` beyond SLA hours → pipeline stagnation alert to practice lead

**Mock of that joined table** (illustrates the logic with fictional names):

| Recruiter | Kredily login | TeamLogger active | CEIPAL sourced | CEIPAL submitted | Flag |
| --- | --- | --- | --- | --- | --- |
| Aisha Khan | 8.2 | 6.4 | 18 | 7 | — |
| Sneha Kulkarni | 8.5 | 5.0 | 22 | 3 | High activity, weak conversion |
| Rahul Menon | 7.9 | 7.1 | 9 | 5 | — |

These four rows are also what the Recruiter KPI sheet in the Excel export uses.

## Module 6 — Finance loop (CEIPAL → TallyPrime → CredFlow → Kredily payroll)

**Trigger:** CEIPAL placement status becomes `Joined`.

**Invoice (BRD-F-601):** read `final_ctc`, `fee_percentage`, replacement/retention window, client legal entity, GSTIN. Build a Tally sales-voucher payload (XML over HTTP / Tally connector) as a **draft** proforma/tax invoice — human finance still approves.

**AR (BRD-F-602):** after Tally assigns an invoice number, push that id to CredFlow. Age buckets T+30 / T+45 / T+60 / T+90 fire email + WhatsApp to the client finance contact via CredFlow, not a homegrown spam loop.

**Commission (BRD-F-603):**

- **Accrued** when status is Joined (on books, not payable).
- **Realized** only when CredFlow/Tally marks Paid **and** the replacement-guarantee window has lapsed.
- Realized amount is the payload to **Kredily payroll** for that month.

I would not compute commissions from recruiter self-reported closures; the cash event in Tally/CredFlow is the source of truth.

## What a real API adapter looks like in this codebase

Keep FastAPI + SQLite as the system of record for the demo. Replace `db.upsert_candidate` / `db.insert_score` with:

```
# REAL CALL WOULD GO HERE:
# PUT https://api.ceipal.com/v1/candidates/{id}
# headers: Authorization: Bearer <CEIPAL_TOKEN>
```

Calendar: replace `scheduler.load_calendar()` with Microsoft Graph `getSchedule` / Google Calendar freebusy.

WhatsApp: replace `/api/chat` UI with Meta Cloud API inbound webhooks; same `chat_agent` state machine.
