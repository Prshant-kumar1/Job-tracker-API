"""
Pydantic schemas used for request validation and response serialization.
"""
from datetime import date, datetime
from typing import Optional, List

from pydantic import BaseModel, EmailStr, ConfigDict, Field

from app.models import ApplicationStatus


# ---------------------------------------------------------------------------
# User / Auth schemas
# ---------------------------------------------------------------------------

class UserCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    email: EmailStr
    password: str = Field(..., min_length=6, max_length=128)


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    email: EmailStr
    created_at: datetime


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    user_id: Optional[int] = None


# ---------------------------------------------------------------------------
# Job Application schemas
# ---------------------------------------------------------------------------

class JobApplicationCreate(BaseModel):
    company: str = Field(..., min_length=1, max_length=150)
    role: str = Field(..., min_length=1, max_length=150)
    location: Optional[str] = None
    apply_link: Optional[str] = None
    date_applied: Optional[date] = None
    status: ApplicationStatus = ApplicationStatus.APPLIED
    resume_version: Optional[str] = None
    notes: Optional[str] = None
    follow_up_date: Optional[date] = None


class JobApplicationUpdate(BaseModel):
    """All fields optional — only provided fields are updated (PATCH-style PUT)."""

    company: Optional[str] = Field(None, min_length=1, max_length=150)
    role: Optional[str] = Field(None, min_length=1, max_length=150)
    location: Optional[str] = None
    apply_link: Optional[str] = None
    date_applied: Optional[date] = None
    status: Optional[ApplicationStatus] = None
    resume_version: Optional[str] = None
    notes: Optional[str] = None
    follow_up_date: Optional[date] = None


class JobApplicationOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    company: str
    role: str
    location: Optional[str] = None
    apply_link: Optional[str] = None
    date_applied: Optional[date] = None
    status: ApplicationStatus
    resume_version: Optional[str] = None
    notes: Optional[str] = None
    follow_up_date: Optional[date] = None
    created_at: datetime


# ---------------------------------------------------------------------------
# Dashboard schemas
# ---------------------------------------------------------------------------

class DashboardSummaryResponse(BaseModel):
    total_applications: int
    applied_count: int
    oa_count: int
    interview_count: int
    rejected_count: int
    offer_count: int
    recent_applications: List[JobApplicationOut]
    upcoming_followups: List[JobApplicationOut]


# ---------------------------------------------------------------------------
# AI Suggestion schema
# ---------------------------------------------------------------------------

class AISuggestionResponse(BaseModel):
    application_id: int
    suggestion: str
