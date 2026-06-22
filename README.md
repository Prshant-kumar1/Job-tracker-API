# AI Job Tracker API

A production-ready FastAPI backend for tracking internship/job applications with JWT authentication, dashboard analytics, and AI-powered next-step suggestions — built to be portfolio-ready, not a toy CRUD demo.

## Description

Job hunting means juggling dozens of applications across different stages (applied, online assessment, interview, rejected, offer), and it's easy to lose track of who needs a follow-up or what to prepare for next. This API gives a logged-in user a single place to log every application, see aggregate stats on a dashboard, and get a tailored "what should I do next" suggestion for any application based on its current status, role, and dates.

The AI suggestion layer is built as a **rule-based engine** (`app/services/ai_service.py`) so the project runs completely offline with no API keys required, while being structured so it can later be swapped for a real LLM call (OpenAI / Gemini / Claude) without touching the routes or database layer.

**Live Demo**: [https://job-tracker-api-dgs0.onrender.com/docs](https://job-tracker-api-dgs0.onrender.com/docs)

## Features

- **Authentication** — JWT-based register/login with bcrypt password hashing
- **Job application tracking** — full CRUD with status filtering
- **Ownership enforcement** — every user only ever sees their own applications (verified with cross-user tests)
- **Dashboard analytics** — status breakdown, recent applications, upcoming follow-ups
- **AI next-step suggestions** — tailored, natural-language guidance per application
- **Interactive API docs** — full Swagger UI out of the box via FastAPI

## Tech Stack

- **Python 3** + **FastAPI**
- **SQLite** + **SQLAlchemy** ORM
- **Pydantic** / **pydantic-settings** for validation and config
- **JWT** auth via `python-jose`
- **bcrypt** password hashing via `passlib`
- **Uvicorn** ASGI server

## Folder Structure

```
job-tracker-api/
│
├── app/
│   ├── main.py              # FastAPI app, router registration
│   ├── database.py          # SQLAlchemy engine/session setup
│   ├── models.py             # User, JobApplication ORM models
│   ├── schemas.py            # Pydantic request/response schemas
│   ├── auth.py                # Password hashing + JWT create/decode
│   ├── dependencies.py       # get_current_user dependency
│   ├── config.py             # Settings loaded from environment
│   │
│   ├── routers/
│   │   ├── auth.py            # /auth/register, /auth/login
│   │   ├── applications.py    # /applications CRUD
│   │   ├── dashboard.py       # /dashboard/summary
│   │   └── ai.py               # /ai/suggest/{id}
│   │
│   └── services/
│       └── ai_service.py      # Rule-based suggestion engine
│
├── requirements.txt
├── .env.example
├── .gitignore
└── README.md
```

## Prerequisites

- **Python 3.8+** (Python 3.11 recommended)
- **pip** package manager
- **Virtual environment** tool (venv or virtualenv)

## Setup Instructions

### Local Development

```bash
# 1. Clone the repository
git clone https://github.com/Prshant-kumar1/Job-tracker-API.git
cd job-tracker-api

# 2. Create and activate a virtual environment
python -m venv venv

# Windows
venv\Scripts\activate

# macOS/Linux
source venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Set up environment variables
# Copy the example file
cp .env.example .env

# Edit .env and set your SECRET_KEY (optional for local dev)
# For production, generate a strong secret:
# python -c "import secrets; print(secrets.token_hex(32))"

# 5. Run the development server
uvicorn app.main:app --reload

# 6. Open the interactive API documentation
# Swagger UI: http://127.0.0.1:8000/docs
# ReDoc: http://127.0.0.1:8000/redoc
```

A `job_tracker.db` SQLite file is created automatically on first run — no separate database setup needed.

### Important Notes

> **Bcrypt Version Pin:** `requirements.txt` pins `bcrypt==4.0.1` alongside `passlib==1.7.4`. Newer bcrypt releases (4.1+) removed an internal attribute that this version of passlib checks for, which causes password hashing to fail with a `ValueError` about 72-byte limits. Keep this pin unless you upgrade passlib too.

> **Database:** SQLite is used for development. For production, consider PostgreSQL and update `DATABASE_URL` in your `.env` file.

## Endpoint Summary

| Method | Endpoint | Auth required | Description |
|---|---|---|---|
| POST | `/auth/register` | No | Create a new account |
| POST | `/auth/login` | No | Log in, get a JWT access token |
| POST | `/applications/` | Yes | Create a job application |
| GET | `/applications/` | Yes | List your applications (optional `?status=interview`) |
| GET | `/applications/{id}` | Yes | Get one application |
| PUT | `/applications/{id}` | Yes | Update an application |
| DELETE | `/applications/{id}` | Yes | Delete an application |
| GET | `/dashboard/summary` | Yes | Aggregate stats + recent + upcoming follow-ups |
| POST | `/ai/suggest/{id}` | Yes | Get an AI next-step suggestion for one application |

Allowed `status` values: `applied`, `oa`, `interview`, `rejected`, `offer`.

For protected routes, send the token from `/auth/login` as:
```
Authorization: Bearer <your_access_token>
```

## Sample Requests & Responses

### Register

```http
POST /auth/register
Content-Type: application/json

{
  "name": "Prashant Kumar",
  "email": "prashant@example.com",
  "password": "securepass123"
}
```

```json
{
  "id": 1,
  "name": "Prashant Kumar",
  "email": "prashant@example.com",
  "created_at": "2026-06-20T12:04:00.339135"
}
```

### Login

```http
POST /auth/login
Content-Type: application/json

{
  "email": "prashant@example.com",
  "password": "securepass123"
}
```

```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

### Create Application

```http
POST /applications/
Authorization: Bearer <token>
Content-Type: application/json

{
  "company": "Zomato",
  "role": "Backend Intern",
  "location": "Gurgaon",
  "apply_link": "https://example.com/job/1",
  "date_applied": "2026-06-15",
  "status": "applied",
  "resume_version": "v3-ats",
  "notes": "Referred by alum"
}
```

```json
{
  "id": 1,
  "user_id": 1,
  "company": "Zomato",
  "role": "Backend Intern",
  "location": "Gurgaon",
  "apply_link": "https://example.com/job/1",
  "date_applied": "2026-06-15",
  "status": "applied",
  "resume_version": "v3-ats",
  "notes": "Referred by alum",
  "follow_up_date": null,
  "created_at": "2026-06-20T12:04:00.951007"
}
```

### Dashboard Summary

```http
GET /dashboard/summary
Authorization: Bearer <token>
```

```json
{
  "total_applications": 3,
  "applied_count": 0,
  "oa_count": 1,
  "interview_count": 1,
  "rejected_count": 1,
  "offer_count": 0,
  "recent_applications": [ /* latest 5 applications */ ],
  "upcoming_followups": [ /* applications with follow_up_date >= today, ascending */ ]
}
```

### AI Suggestion

```http
POST /ai/suggest/1
Authorization: Bearer <token>
```

```json
{
  "application_id": 1,
  "suggestion": "Your online assessment for the Backend Intern role at Zomato is the next hurdle. Spend the next few days on timed DSA practice (arrays, strings, trees, graphs), a quick pass on aptitude/MCQ-style questions, and a refresher on FastAPI/Django fundamentals, REST API design, and SQL joins. Treat it like a real exam: simulate the time limit at least once."
}
```

## Security Notes

- Passwords are hashed with **bcrypt** — never stored in plain text.
- JWTs are signed with `SECRET_KEY` from your `.env` and expire after `ACCESS_TOKEN_EXPIRE_MINUTES`.
- Every application route checks `JobApplication.user_id == current_user.id` server-side — a user can never read, modify, or delete another user's applications, and a missing-or-not-yours record returns the same `404` either way (no enumeration).
- Login failures return a generic "Incorrect email or password" message rather than revealing whether the email exists.
- **Before deploying anywhere real:** generate a strong random `SECRET_KEY` (e.g. `python -c "import secrets; print(secrets.token_hex(32))"`), never commit your real `.env`, and put the API behind HTTPS.

## Extending This Project

- Swap `app/services/ai_service.py`'s rule-based logic for a real LLM call — the route layer and response schema (`AISuggestionResponse`) don't need to change.
- Add a frontend (Next.js / React) that consumes these endpoints.
- Add Alembic migrations instead of `Base.metadata.create_all()` once the schema needs to evolve in production.
- Add rate limiting on `/auth/login` to slow down brute-force attempts.
#
