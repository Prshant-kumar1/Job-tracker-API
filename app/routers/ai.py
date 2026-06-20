"""
AI suggestion route. Delegates the actual recommendation logic to
app.services.ai_service so this file stays a thin route handler.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import get_current_user
from app.models import JobApplication, User
from app.schemas import AISuggestionResponse
from app.services.ai_service import generate_suggestion

router = APIRouter(prefix="/ai", tags=["AI Suggestions"])


@router.post("/suggest/{application_id}", response_model=AISuggestionResponse)
def suggest_next_step(
    application_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Generate a next-step suggestion for one of the user's applications."""
    application = (
        db.query(JobApplication)
        .filter(
            JobApplication.id == application_id,
            JobApplication.user_id == current_user.id,
        )
        .first()
    )
    if application is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Application not found",
        )

    suggestion_text = generate_suggestion(application)
    return AISuggestionResponse(application_id=application.id, suggestion=suggestion_text)
