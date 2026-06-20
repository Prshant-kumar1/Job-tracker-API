"""
Job application CRUD routes. Every route is protected and every
single-object operation verifies the application belongs to the
currently logged-in user (ownership enforcement / access control).
"""
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import get_current_user
from app.models import JobApplication, User, ApplicationStatus
from app.schemas import JobApplicationCreate, JobApplicationUpdate, JobApplicationOut

router = APIRouter(prefix="/applications", tags=["Job Applications"])


def _get_owned_application_or_404(
    application_id: int, db: Session, current_user: User
) -> JobApplication:
    """
    Fetch an application by id, scoped to the current user.
    Returns 404 (not 403) for applications that exist but belong to someone
    else, so we don't leak whether the id exists at all.
    """
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
    return application


@router.post("/", response_model=JobApplicationOut, status_code=status.HTTP_201_CREATED)
def create_application(
    application_in: JobApplicationCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Create a new job application for the logged-in user."""
    new_application = JobApplication(
        user_id=current_user.id,
        **application_in.model_dump(),
    )
    db.add(new_application)
    db.commit()
    db.refresh(new_application)
    return new_application


@router.get("/", response_model=List[JobApplicationOut])
def list_applications(
    status_filter: Optional[ApplicationStatus] = Query(None, alias="status"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    List all applications belonging to the logged-in user, newest first.
    Optional `?status=interview` query param narrows the results.
    """
    query = db.query(JobApplication).filter(JobApplication.user_id == current_user.id)
    if status_filter is not None:
        query = query.filter(JobApplication.status == status_filter)
    return query.order_by(JobApplication.created_at.desc()).all()


@router.get("/{application_id}", response_model=JobApplicationOut)
def get_application(
    application_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get a single application by id (must belong to the current user)."""
    return _get_owned_application_or_404(application_id, db, current_user)


@router.put("/{application_id}", response_model=JobApplicationOut)
def update_application(
    application_id: int,
    application_update: JobApplicationUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Update one or more fields of an existing application."""
    application = _get_owned_application_or_404(application_id, db, current_user)

    update_data = application_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(application, field, value)

    db.commit()
    db.refresh(application)
    return application


@router.delete("/{application_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_application(
    application_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Delete an application owned by the current user."""
    application = _get_owned_application_or_404(application_id, db, current_user)
    db.delete(application)
    db.commit()
    return None
