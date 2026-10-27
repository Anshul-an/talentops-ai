import io
import json
from datetime import date

import pandas as pd

from app import db
from app.config import MOCK_RECRUITERS


def build_workbook() -> bytes:
    candidates = db.list_candidates()
    interviews = {i["candidate_id"]: i for i in reversed(db.list_interviews())}
    jobs = {j["id"]: j for j in db.list_jobs()}
    scores = db.fetchall("SELECT * FROM scores ORDER BY id ASC")
    latest_job = {s["candidate_id"]: s for s in scores}

    pipeline_rows = []
    for c in candidates:
        sc = latest_job.get(c["id"], {})
        job = jobs.get(sc.get("job_id")) if sc else None
        iv = interviews.get(c["id"], {})
        pipeline_rows.append(
            {
                "Candidate Name": c.get("full_name"),
                "Recruiter Name": "Aisha Khan",  # mock assignment
                "Job Title": job.get("title") if job else "",
                "Client Name": job.get("client_name") if job else "",
                "Sourcing Channel": c.get("source_channel"),
                "Status": c.get("latest_status") or "Sourced - Unscored",
                "Fitment Score": c.get("latest_score"),
                "Interview Date": iv.get("slot_time"),
                "Interview Status": iv.get("confirmation_status"),
                "Current CTC (L)": c.get("current_ctc"),
                "Expected CTC (L)": c.get("expected_ctc"),
                "Offer CTC": "",
                "Expected Revenue": "",
            }
        )
    kpi = json.loads(MOCK_RECRUITERS.read_text(encoding="utf-8"))
    kpi_rows = [
        {
            "Recruiter Name": r["recruiter_name"],
            "Login Hours (Kredily)": r["login_hours"],
            "Productive Hours (TeamLogger)": r["productive_hours"],
            "Profiles Added (CEIPAL)": r["profiles_added"],
            "Submissions": r["submissions"],
            "1st Rounds": r["first_rounds"],
            "2nd Rounds": r["second_rounds"],
            "Final Rounds": r["final_rounds"],
            "Selections": r["selections"],
            "Closures": r["closures"],
        }
        for r in kpi
    ]

    channel_map: dict[str, dict[str, float]] = {}
    for c in candidates:
        ch = c.get("source_channel") or "Unknown"
        channel_map.setdefault(ch, {"sourced": 0, "qualified": 0, "spend": 0})
        channel_map[ch]["sourced"] += 1
        if (c.get("latest_status") or "") == "Screened - AI Fit":
            channel_map[ch]["qualified"] += 1
    mock_spend = {"Naukri": 45000, "LinkedIn": 62000, "Shine": 18000, "Direct upload": 0, "Inbound email": 0}
    channel_rows = []
    for ch, stats in channel_map.items():
        spend = mock_spend.get(ch, 12000)
        channel_rows.append(
            {
                "Channel": ch,
                "Sourcing Spend (INR)": spend,
                "Candidates Sourced": stats["sourced"],
                "Qualified (AI Fit)": stats["qualified"],
                "Cost per Qualified": round(spend / stats["qualified"], 0) if stats["qualified"] else None,
            }
        )
    if not channel_rows:
        channel_rows = [{"Channel": "Naukri", "Sourcing Spend (INR)": 45000, "Candidates Sourced": 0, "Qualified (AI Fit)": 0, "Cost per Qualified": None}]

    buf = io.BytesIO()
    with pd.ExcelWriter(buf, engine="openpyxl") as writer:
        pd.DataFrame(pipeline_rows).to_excel(writer, sheet_name="Master Daily Pipeline", index=False)
        pd.DataFrame(kpi_rows).to_excel(writer, sheet_name="Recruiter KPI Leaderboard", index=False)
        pd.DataFrame(channel_rows).to_excel(writer, sheet_name="Channel Performance Matrix", index=False)
        pd.DataFrame(
            [{"Generated on": date.today().isoformat(), "Note": "TalentOps AI demo MIS — pipeline is live; KPI hours are mocked Kredily/TeamLogger values"}]
        ).to_excel(writer, sheet_name="Notes", index=False)
    return buf.getvalue()
