import time
from contextlib import asynccontextmanager
from typing import Optional

from fastapi import FastAPI, File, Form, HTTPException, Query, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, Response
from fastapi.staticfiles import StaticFiles
from starlette.requests import Request
from starlette.responses import Response as StarletteResponse

from app import chat_agent, db, scheduler
from app.config import FRONTEND_DIR, SAMPLE_RESUMES, UPLOAD_DIR
from app.dashboard import summary
from app.dossier import build_dossier
from app.excel_export import build_workbook
from app.logging_config import get_logger
from app.models import ChatIn, InterviewConfirm, JobIn, ScoreRequest
from app.parser import parse_resume
from app.scorer import score_candidate
from app.seed import seed_if_empty

logger = get_logger("main")


@asynccontextmanager
async def lifespan(_app: FastAPI):
    logger.info("Starting TalentOps AI service — initializing database")
    db.init_db()
    seed_if_empty()
    logger.info("TalentOps AI service ready")
    yield
    logger.info("Shutting down TalentOps AI service")


app = FastAPI(
    title="TalentOps AI",
    description="Scoped recruitment-automation prototype for Virtuous (AI Intern demo).",
    version="0.1.0",
    lifespan=lifespan,
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.perf_counter()
    response: StarletteResponse = await call_next(request)
    duration_ms = round((time.perf_counter() - start_time) * 1000, 2)
    logger.info(
        f"{request.method} {request.url.path} -> {response.status_code} ({duration_ms}ms)",
        extra={
            "extra_data": {
                "method": request.method,
                "path": request.url.path,
                "status_code": response.status_code,
                "duration_ms": duration_ms,
            }
        },
    )
    return response


@app.get("/api/health")
@app.get("/health")
def health() -> dict:
    from app.llm import status as llm_status

    st = llm_status()
    logger.debug(f"Health check invoked: provider={st.get('provider')}")
    return {"ok": True, **st}


@app.post("/resumes/upload")
@app.post("/api/resumes/upload")
async def upload_resumes(
    files: list[UploadFile] = File(...),
    source_channel: str = Form("Direct upload"),
) -> dict:
    logger.info(f"Upload received for {len(files)} files via channel '{source_channel}'")
    results = []
    for f in files:
        dest = UPLOAD_DIR / (f.filename or "resume.bin")
        dest.write_bytes(await f.read())
        try:
            parsed = parse_resume(dest, source_channel=source_channel)
        except Exception as exc:
            logger.error(f"Failed to parse uploaded file {dest.name}: {exc}")
            results.append({"file": dest.name, "error": str(exc)})
            continue
        cid, action = db.upsert_candidate(parsed)
        logger.info(f"Uploaded resume {dest.name} -> candidate #{cid} ({action})")
        results.append({"file": dest.name, "candidate_id": cid, "action": action, "parsed": db.get_candidate(cid)})
    return {"results": results}


@app.post("/api/resumes/ingest-samples")
def ingest_samples() -> dict:
    files = sorted(p for p in SAMPLE_RESUMES.iterdir() if p.suffix.lower() in {".pdf", ".docx", ".txt"})
    if not files:
        logger.warning("Ingest samples called but no sample files found on disk")
        raise HTTPException(400, "No sample resumes found. Run: python scripts/generate_samples.py")
    results = []
    channels = ["Naukri", "LinkedIn", "Shine", "Inbound email", "Direct upload"]
    for i, path in enumerate(files):
        parsed = parse_resume(path, source_channel=channels[i % len(channels)])
        cid, action = db.upsert_candidate(parsed)
        results.append({"file": path.name, "candidate_id": cid, "action": action})
    logger.info(f"Ingested {len(results)} sample resumes successfully")
    return {"ingested": len(results), "results": results}


@app.get("/candidates")
@app.get("/api/candidates")
def candidates(status: Optional[str] = None, source: Optional[str] = None) -> dict:
    cands = db.list_candidates(status=status, source=source)
    logger.debug(f"Retrieved {len(cands)} candidates (filter status={status}, source={source})")
    return {"candidates": cands}


@app.get("/api/candidates/search")
def search_candidates(q: str = Query(..., min_length=1)) -> dict:
    results = db.search_candidates(q)
    logger.info(f"Candidate search for '{q}' returned {len(results)} matches")
    return {"query": q, "count": len(results), "candidates": results}


@app.post("/api/candidates/{cid}/notes")
def add_note(cid: int, payload: dict) -> dict:
    note = payload.get("note") or payload.get("text", "")
    author = payload.get("author", "Recruiter")
    if not note.strip():
        raise HTTPException(400, "Note text cannot be empty")
    nid = db.add_candidate_note(cid, note, author)
    return {"id": nid, "candidate_id": cid, "note": note, "author": author}


@app.get("/api/candidates/{cid}/notes")
def list_notes(cid: int) -> dict:
    return {"candidate_id": cid, "notes": db.get_candidate_notes(cid)}


@app.patch("/api/candidates/{cid}/status")
def update_candidate_status(cid: int, payload: dict) -> dict:
    status = payload.get("status")
    if not status:
        raise HTTPException(400, "status is required")
    db.update_candidate_status(cid, status, payload.get("note"))
    return {"candidate_id": cid, "status": status, "updated": True}


@app.delete("/api/candidates/{cid}")
def delete_candidate(cid: int) -> dict:
    ok = db.soft_delete_candidate(cid)
    if not ok:
        raise HTTPException(404, "Candidate not found")
    logger.info(f"Candidate #{cid} soft-deleted")
    return {"candidate_id": cid, "deleted": True}


@app.get("/api/candidates/{cid}/timeline")
def get_timeline(cid: int) -> dict:
    return {"candidate_id": cid, "timeline": db.get_candidate_timeline(cid)}


@app.post("/api/candidates/{cid}/tags")
def add_tag(cid: int, payload: dict) -> dict:
    tag = payload.get("tag")
    if not tag:
        raise HTTPException(400, "tag is required")
    tid = db.add_candidate_tag(cid, tag)
    return {"id": tid, "candidate_id": cid, "tag": tag, "all_tags": db.get_candidate_tags(cid)}


@app.get("/candidates/{cid}")
@app.get("/api/candidates/{cid}")
def candidate_detail(cid: int) -> dict:
    row = db.get_candidate(cid)
    if not row:
        logger.warning(f"Candidate #{cid} not found")
        raise HTTPException(404, "Candidate not found")
    scores = db.fetchall("SELECT * FROM scores WHERE candidate_id = ? ORDER BY id DESC", (cid,))
    chats = db.chat_history(cid)
    interviews = db.fetchall("SELECT * FROM interviews WHERE candidate_id = ? ORDER BY id DESC", (cid,))
    session = db.get_session(cid)
    return {"candidate": row, "scores": scores, "chat": chats, "interviews": interviews, "screening": session}


@app.get("/jobs")
@app.get("/api/jobs")
def list_jobs() -> dict:
    return {"jobs": db.list_jobs()}


@app.get("/api/jobs/{jid}")
def get_job_detail(jid: int) -> dict:
    job = db.get_job(jid)
    if not job:
        raise HTTPException(404, "Job not found")
    return {"job": job}


@app.patch("/api/jobs/{jid}")
def patch_job(jid: int, payload: dict) -> dict:
    if not db.get_job(jid):
        raise HTTPException(404, "Job not found")
    db.update_job(jid, payload.get("title"), payload.get("client_name"), payload.get("jd_text"))
    return {"job": db.get_job(jid)}


@app.post("/jobs")
@app.post("/api/jobs")
def create_job(body: JobIn) -> dict:
    jid = db.insert_job(body.title, body.client_name, body.jd_text)
    logger.info(f"Created job #{jid} '{body.title}' for client '{body.client_name}'")
    return {"job": db.get_job(jid)}


@app.post("/api/score/bulk")
def score_bulk(body: ScoreRequest) -> dict:
    return score(body)


@app.post("/score")
@app.post("/api/score")
def score(body: ScoreRequest) -> dict:
    job = db.get_job(body.job_id)
    if not job:
        raise HTTPException(404, "Job not found")
    if body.candidate_ids:
        people = [db.get_candidate(i) for i in body.candidate_ids]
        people = [p for p in people if p]
    else:
        people = db.fetchall("SELECT * FROM candidates")
    out = []
    logger.info(f"Scoring {len(people)} candidate(s) against job #{body.job_id} ('{job.get('title')}')")
    for cand in people:
        result = score_candidate(cand, job, body.threshold)
        sid = db.insert_score({**result, "candidate_id": cand["id"], "job_id": body.job_id})
        out.append({**result, "id": sid, "candidate_id": cand["id"], "job_id": body.job_id})
    return {"scores": out}


@app.post("/chat/{candidate_id}")
@app.post("/api/chat/{candidate_id}")
def chat(candidate_id: int, body: ChatIn) -> dict:
    try:
        return chat_agent.start_or_continue(candidate_id, body.message)
    except ValueError as exc:
        raise HTTPException(404, str(exc)) from exc


@app.get("/api/interviews/{iid}")
def get_interview_detail(iid: int) -> dict:
    iv = db.get_interview(iid)
    if not iv:
        raise HTTPException(404, "Interview not found")
    reminders = db.list_reminders(iid)
    return {"interview": iv, "reminders": reminders}


@app.delete("/api/interviews/{iid}")
def cancel_interview_endpoint(iid: int) -> dict:
    ok = db.cancel_interview(iid)
    if not ok:
        raise HTTPException(404, "Interview not found")
    logger.info(f"Interview #{iid} cancelled")
    return {"interview_id": iid, "status": "Cancelled"}


@app.get("/interviews")
@app.get("/api/interviews")
def interviews() -> dict:
    return {
        "interviews": db.list_interviews(),
        "open_slots": scheduler.available_slots(),
        "reminders": db.list_reminders(),
    }


@app.post("/api/interviews/{iid}/reminders/dispatch")
def dispatch_reminders(iid: int) -> dict:
    if not db.fetchone("SELECT id FROM interviews WHERE id = ?", (iid,)):
        raise HTTPException(404, "Interview not found")
    return scheduler.dispatch_reminders(iid)


@app.post("/api/reminders/dispatch")
def dispatch_all_reminders() -> dict:
    return scheduler.dispatch_reminders()


@app.get("/api/candidates/{cid}/dossier")
def candidate_dossier(cid: int, job_id: Optional[int] = None) -> dict:
    try:
        return build_dossier(cid, job_id)
    except ValueError as exc:
        raise HTTPException(404, str(exc)) from exc


@app.post("/interviews/propose/{candidate_id}")
@app.post("/api/interviews/propose/{candidate_id}")
def propose(candidate_id: int) -> dict:
    if not db.get_candidate(candidate_id):
        raise HTTPException(404, "Candidate not found")
    return {"slots": scheduler.propose(3)}


@app.post("/api/interviews/book/{candidate_id}")
def book(candidate_id: int, slot_id: str = Query(...), job_id: Optional[int] = None) -> dict:
    try:
        return scheduler.book(candidate_id, slot_id, job_id=job_id)
    except ValueError as exc:
        raise HTTPException(409, str(exc)) from exc


@app.post("/interviews/confirm/{iid}")
@app.post("/api/interviews/confirm/{iid}")
def confirm(iid: int, body: InterviewConfirm) -> dict:
    try:
        return scheduler.confirm(iid, body.action, body.new_slot_id)
    except ValueError as exc:
        raise HTTPException(400, str(exc)) from exc


@app.get("/api/dashboard/channel-roi")
def get_channel_roi() -> dict:
    from app.dashboard import channel_roi
    return channel_roi()


@app.get("/api/dashboard/pipeline-velocity")
def get_pipeline_velocity() -> dict:
    from app.dashboard import pipeline_velocity
    return pipeline_velocity()


@app.get("/dashboard/summary")
@app.get("/api/dashboard/summary")
def dashboard_summary() -> dict:
    return summary()


@app.get("/export/excel")
@app.get("/api/export/excel")
def export_excel() -> Response:
    data = build_workbook()
    return Response(
        content=data,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": "attachment; filename=TalentOps_MIS.xlsx"},
    )


if FRONTEND_DIR.exists():
    app.mount("/assets", StaticFiles(directory=FRONTEND_DIR), name="assets")


@app.get("/")
def index() -> FileResponse:
    return FileResponse(FRONTEND_DIR / "index.html")
