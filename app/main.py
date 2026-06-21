"""
AI Job Tracker API — application entrypoint.

Run with:
    uvicorn app.main:app --reload
"""
import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database import Base, engine
from app.routers import auth, applications, dashboard, ai

# Create all tables on startup if they don't already exist.
# For a production app you'd use Alembic migrations instead.
# Drop and recreate tables to fix UUID vs Integer mismatch issue
try:
    Base.metadata.drop_all(bind=engine)
    print("Dropped existing tables")
    Base.metadata.create_all(bind=engine)
    print("Database tables created successfully")
except Exception as e:
    print(f"Error creating database tables: {e}")
    # Continue anyway - tables might already exist

app = FastAPI(
    title="AI Job Tracker API",
    description=(
        "A backend API for tracking internship/job applications, managing "
        "status updates, viewing dashboard analytics, and generating "
        "AI-powered next-step suggestions."
    ),
    version="1.0.0",
)

# ── CORS ─────────────────────────────────────────────────────────────────────
# Allow the deployed frontend origin plus localhost for local development.
# FRONTEND_URL env var should be set in Render to your frontend's public URL,
# e.g. https://job-tracker-frontend.onrender.com
_frontend_url = os.getenv("FRONTEND_URL", "")
_allowed_origins = [
    "http://localhost:5173",   # Vite dev server
    "http://localhost:4173",   # Vite preview
    "http://127.0.0.1:5173",
]
if _frontend_url:
    _allowed_origins.append(_frontend_url.rstrip("/"))

app.add_middleware(
    CORSMiddleware,
    allow_origins=_allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
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


@app.get("/health", tags=["Health"])
def health_check():
    """Detailed health check including CORS and environment info."""
    import os
    from sqlalchemy import text
    
    db_test = "unknown"
    try:
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1"))
            db_test = "connected"
    except Exception as e:
        db_test = f"failed: {str(e)[:100]}"
    
    return {
        "status": "healthy",
        "frontend_url_configured": os.getenv("FRONTEND_URL", "NOT_SET"),
        "allowed_origins": _allowed_origins,
        "database_url_set": bool(os.getenv("DATABASE_URL")),
        "secret_key_set": bool(os.getenv("SECRET_KEY")),
        "database_connection": db_test,
    }
