"""
SQLAlchemy ORM models: User and JobApplication.
"""
import enum
from datetime import datetime, date

from sqlalchemy import (
    Column,
    Integer,
    String,
    DateTime,
    Date,
    ForeignKey,
    Enum as SAEnum,
    Text,
)
from sqlalchemy.orm import relationship

from app.database import Base


class ApplicationStatus(str, enum.Enum):
    """Controlled set of allowed status values for a job application."""

    APPLIED = "applied"
    OA = "oa"
    INTERVIEW = "interview"
    REJECTED = "rejected"
    OFFER = "offer"


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String(100), nullable=False)
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    applications = relationship(
        "JobApplication",
        back_populates="owner",
        cascade="all, delete-orphan",
    )


class JobApplication(Base):
    __tablename__ = "job_applications"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)

    company = Column(String(150), nullable=False)
    role = Column(String(150), nullable=False)
    location = Column(String(150), nullable=True)
    apply_link = Column(String(500), nullable=True)
    date_applied = Column(Date, nullable=True)
    status = Column(
        SAEnum(ApplicationStatus, native_enum=False, length=20),
        default=ApplicationStatus.APPLIED,
        nullable=False,
    )
    resume_version = Column(String(100), nullable=True)
    notes = Column(Text, nullable=True)
    follow_up_date = Column(Date, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    owner = relationship("User", back_populates="applications")
