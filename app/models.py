from typing import Any, Optional

from pydantic import BaseModel, Field


class CandidateOut(BaseModel):
    id: int
    full_name: Optional[str] = None
    current_location: Optional[str] = None
    preferred_location: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    linkedin_url: Optional[str] = None
    total_experience_years: Optional[float] = None
    relevant_experience_years: Optional[float] = None
    current_ctc: Optional[float] = None
    expected_ctc: Optional[float] = None
    notice_period_days: Optional[int] = None
    current_company: Optional[str] = None
    previous_employers: Optional[str] = None
    skills: Optional[str] = None
    certifications: Optional[str] = None
    education: Optional[str] = None
    source_channel: Optional[str] = None
    resume_path: Optional[str] = None
    created_at: Optional[str] = None
    latest_score: Optional[float] = None
    latest_status: Optional[str] = None
    latest_summary: Optional[str] = None
    parser_engine: Optional[str] = None


class JobIn(BaseModel):
    title: str
    client_name: str = "Internal / Demo Client"
    jd_text: str


class JobOut(BaseModel):
    id: int
    title: str
    client_name: Optional[str] = None
    jd_text: str
    created_at: Optional[str] = None


class ScoreRequest(BaseModel):
    job_id: int
    candidate_ids: Optional[list[int]] = None
    threshold: Optional[float] = None


class ScoreOut(BaseModel):
    id: int
    candidate_id: int
    job_id: int
    fitment_score: float
    summary_bullets: str
    status: str
    domain_relevance: Optional[float] = None
    skill_recency: Optional[float] = None
    stability_index: Optional[float] = None
    created_at: Optional[str] = None
    engine: Optional[str] = None


class ChatIn(BaseModel):
    message: str = Field(..., min_length=1)


class ChatOut(BaseModel):
    reply: str
    qualified: bool = False
    captured: dict[str, Any] = Field(default_factory=dict)
    proposed_slots: list[dict[str, Any]] = Field(default_factory=list)
    engine: Optional[str] = None


class InterviewConfirm(BaseModel):
    slot_id: Optional[str] = None
    action: str = "confirm"  # confirm | reschedule | noshow
    new_slot_id: Optional[str] = None


class NoteIn(BaseModel):
    note: str = Field(..., min_length=1)
    author: Optional[str] = "Recruiter"


class CandidateNote(BaseModel):
    id: int
    candidate_id: int
    note: str
    author: Optional[str] = "Recruiter"
    created_at: Optional[str] = None


class TagIn(BaseModel):
    tag: str = Field(..., min_length=1)


class CandidateTag(BaseModel):
    id: int
    candidate_id: int
    tag: str
    created_at: Optional[str] = None

from enum import Enum


class CandidateStatusEnum(str, Enum):
    SOURCED_UNSCORED = "Sourced - Unscored"
    SCREENED_AI_FIT = "Screened - AI Fit"
    SOURCED_BELOW_THRESHOLD = "Sourced - Below Threshold"
    INTERVIEW_SCHEDULED = "Interview Scheduled"
    OFFERED = "Offered"
    REJECTED = "Rejected"


class StatusUpdateIn(BaseModel):
    status: str
    note: Optional[str] = None


class SearchResult(BaseModel):
    query: str
    count: int
    candidates: list[dict[str, Any]] = Field(default_factory=list)


class PipelineVelocity(BaseModel):
    sourced_to_screened_days: float
    screened_to_interview_days: float
    interview_to_offer_days: float
    offer_to_join_days: float
    avg_total_days: float


class ChannelROIItem(BaseModel):
    channel: str
    spend: float
    sourced: int
    qualified: int
    avg_score: float
    cpa: Optional[float] = None


class ChannelROI(BaseModel):
    channels: list[ChannelROIItem] = Field(default_factory=list)


class VersionInfo(BaseModel):
    name: str = "TalentOps AI"
    version: str = "0.1.0"
    git_sha: str = "unknown"


class DatabaseCounts(BaseModel):
    candidates: int
    jobs: int
    interviews: int
    scores: int


class DetailedHealth(BaseModel):
    ok: bool = True
    llm: dict[str, Any] = Field(default_factory=dict)
    database: DatabaseCounts


class BulkScoreRequest(ScoreRequest):
    batch_name: Optional[str] = None
    priority: Optional[str] = "normal"


class InterviewDetail(BaseModel):
    id: int
    candidate_id: int
    job_id: Optional[int] = None
    stage: str
    slot_id: Optional[str] = None
    slot_time: Optional[str] = None
    confirmation_status: str
    created_at: Optional[str] = None
    full_name: Optional[str] = None
    email: Optional[str] = None
