"""
Dashboard analytics route: aggregate counts, recent applications, and
upcoming follow-ups for the logged-in user.
"""
from datetime import date

from fastapi import APIRouter, Depends
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import get_current_user
from app.models import JobApplication, User, ApplicationStatus
from app.schemas import DashboardSummaryResponse

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])

RECENT_APPLICATIONS_LIMIT = 5


@router.get("/summary", response_model=DashboardSummaryResponse)
def get_dashboard_summary(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Return aggregate stats, recent applications, and upcoming follow-ups."""
    base_query = db.query(JobApplication).filter(JobApplication.user_id == current_user.id)

    total_applications = base_query.count()

    # Single grouped query for all status counts, then fill in zeros for
    # any status the user has no applications in.
    status_rows = (
        db.query(JobApplication.status, func.count(JobApplication.id))
        .filter(JobApplication.user_id == current_user.id)
        .group_by(JobApplication.status)
        .all()
    )
    counts = {status_value.value: 0 for status_value in ApplicationStatus}
    for status_value, count in status_rows:
        # Handle both Enum objects and string values (PostgreSQL returns strings)
        if isinstance(status_value, ApplicationStatus):
            key = status_value.value
        elif hasattr(status_value, "value"):
            key = status_value.value
        else:
            key = str(status_value)
        counts[key] = count

    recent_applications = (
        base_query.order_by(JobApplication.created_at.desc())
        .limit(RECENT_APPLICATIONS_LIMIT)
        .all()
    )

    upcoming_followups = (
        base_query.filter(JobApplication.follow_up_date != None)
        .filter(JobApplication.follow_up_date >= date.today())
        .order_by(JobApplication.follow_up_date.asc())
        .all()
    )

    return DashboardSummaryResponse(
        total_applications=total_applications,
        applied_count=counts[ApplicationStatus.APPLIED.value],
        oa_count=counts[ApplicationStatus.OA.value],
        interview_count=counts[ApplicationStatus.INTERVIEW.value],
        rejected_count=counts[ApplicationStatus.REJECTED.value],
        offer_count=counts[ApplicationStatus.OFFER.value],
        recent_applications=recent_applications,
        upcoming_followups=upcoming_followups,
    )
