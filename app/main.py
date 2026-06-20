"""
AI Job Tracker API — application entrypoint.

Run with:
    uvicorn app.main:app --reload
"""
from fastapi import FastAPI

from app.database import Base, engine
from app.routers import auth, applications, dashboard, ai

# Create all tables on startup if they don't already exist.
# For a production app you'd use Alembic migrations instead.
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="AI Job Tracker API",
    description=(
        "A backend API for tracking internship/job applications, managing "
        "status updates, viewing dashboard analytics, and generating "
        "AI-powered next-step suggestions."
    ),
    version="1.0.0",
)

app.include_router(auth.router)
app.include_router(applications.router)
app.include_router(dashboard.router)
app.include_router(ai.router)


@app.get("/", tags=["Health"])
def root():
    """Simple health-check / welcome route."""
    return {
        "message": "AI Job Tracker API is running",
        "docs": "/docs",
    }
