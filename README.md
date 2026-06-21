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
#   J o b - t r a c k e r - A P I 
 
 


## Environment Variables

Create a `.env` file in the root directory with the following variables:

```env
# JWT Secret Key - MUST be changed for production
SECRET_KEY=your-secret-key-here

# JWT Algorithm
ALGORITHM=HS256

# Token expiration time in minutes
ACCESS_TOKEN_EXPIRE_MINUTES=60

# Database connection string
# SQLite (default for local dev)
DATABASE_URL=sqlite:///./job_tracker.db

# PostgreSQL (for production)
# DATABASE_URL=postgresql://user:password@localhost/dbname

# Frontend URL for CORS (production)
FRONTEND_URL=https://your-frontend-domain.com
```

### Generate a Secure Secret Key

```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

## Deployment

### Deploy to Render

1. **Create a new Web Service** on [Render](https://render.com)
2. **Connect your GitHub repository**
3. **Configure the service:**
   - **Environment**: Python 3
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
4. **Add environment variables:**
   ```
   SECRET_KEY=<generate-strong-random-key>
   DATABASE_URL=<your-postgres-url>
   FRONTEND_URL=https://your-frontend-domain.com
   ALGORITHM=HS256
   ACCESS_TOKEN_EXPIRE_MINUTES=60
   ```
5. **Deploy!**

### Deploy to Heroku

```bash
# Install Heroku CLI and login
heroku login

# Create a new app
heroku create your-app-name

# Add PostgreSQL addon
heroku addons:create heroku-postgresql:mini

# Set environment variables
heroku config:set SECRET_KEY=$(python -c "import secrets; print(secrets.token_hex(32))")
heroku config:set FRONTEND_URL=https://your-frontend-domain.com

# Deploy
git push heroku main

# Open the app
heroku open
```

### Deploy to Railway

1. **Create a new project** on [Railway](https://railway.app)
2. **Connect your GitHub repository**
3. **Add PostgreSQL database** (optional, or use SQLite)
4. **Set environment variables** in the Railway dashboard
5. **Deploy automatically** on git push

### Production Checklist

Before deploying to production, ensure:

- ✅ Strong random `SECRET_KEY` is set
- ✅ `DATABASE_URL` points to production database (PostgreSQL recommended)
- ✅ `FRONTEND_URL` is set for proper CORS configuration
- ✅ HTTPS is enabled (most platforms do this automatically)
- ✅ `.env` file is in `.gitignore` and never committed
- ✅ Database backups are configured
- ✅ Error logging and monitoring are set up

## Testing the API

### Using Swagger UI

1. Navigate to `http://127.0.0.1:8000/docs`
2. Click **"Authorize"** button
3. Register a new user via `/auth/register`
4. Login via `/auth/login` and copy the `access_token`
5. Paste the token in the authorization dialog
6. Test all endpoints interactively

### Using cURL

```bash
# Register a new user
curl -X POST http://127.0.0.1:8000/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Test User",
    "email": "test@example.com",
    "password": "password123"
  }'

# Login
curl -X POST http://127.0.0.1:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "password123"
  }'

# Create an application (replace TOKEN with your JWT)
curl -X POST http://127.0.0.1:8000/applications/ \
  -H "Authorization: Bearer TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "company": "Google",
    "role": "Software Engineer",
    "location": "Mountain View, CA",
    "apply_link": "https://careers.google.com",
    "date_applied": "2026-06-20",
    "status": "applied",
    "notes": "Applied via LinkedIn"
  }'
```

## Troubleshooting

### Database Issues

**Problem**: `OperationalError: unable to open database file`

**Solution**: 
- Ensure you have write permissions in the project directory
- The SQLite file will be created automatically if it doesn't exist
- For production, use PostgreSQL instead

### Authentication Errors

**Problem**: `401 Unauthorized` on protected endpoints

**Solution**:
- Ensure you're sending the JWT token in the `Authorization` header
- Format: `Authorization: Bearer <your_token>`
- Check that the token hasn't expired (default: 60 minutes)
- Verify `SECRET_KEY` hasn't changed between login and request

### CORS Errors

**Problem**: Frontend can't access the API due to CORS

**Solution**:
- Set `FRONTEND_URL` environment variable to your frontend's URL
- For local development, add your dev server URL to `_allowed_origins` in `app/main.py`
- Check that the frontend is using the correct API URL

### Password Hashing Errors

**Problem**: `ValueError` related to bcrypt

**Solution**:
- Keep `bcrypt==4.0.1` and `passlib==1.7.4` versions as pinned
- Don't upgrade bcrypt without upgrading passlib
- Clear your virtual environment and reinstall: `pip install -r requirements.txt`

### Port Already in Use

**Problem**: `OSError: [Errno 48] Address already in use`

**Solution**:
```bash
# Find process using port 8000
# Windows
netstat -ano | findstr :8000

# macOS/Linux
lsof -i :8000

# Kill the process or use a different port
uvicorn app.main:app --reload --port 8001
```

## API Architecture

### Authentication Flow

1. User registers with email and password
2. Password is hashed with bcrypt and stored
3. User logs in with credentials
4. Server validates and returns JWT access token
5. Client stores token (localStorage/cookies)
6. Client sends token in `Authorization` header for protected routes
7. Server validates token and extracts user identity
8. Server enforces data ownership (users only see their own data)

### Database Schema

**Users Table**
- `id` (Integer, Primary Key)
- `name` (String)
- `email` (String, Unique)
- `hashed_password` (String)
- `created_at` (DateTime)

**JobApplications Table**
- `id` (Integer, Primary Key)
- `user_id` (Integer, Foreign Key → users.id)
- `company` (String)
- `role` (String)
- `location` (String, Optional)
- `apply_link` (String, Optional)
- `date_applied` (Date, Optional)
- `status` (String: applied/oa/interview/rejected/offer)
- `resume_version` (String, Optional)
- `notes` (Text, Optional)
- `follow_up_date` (Date, Optional)
- `created_at` (DateTime)

### AI Suggestion Engine

The rule-based AI engine (`app/services/ai_service.py`) provides context-aware suggestions based on:

- **Application status** (applied, oa, interview, rejected, offer)
- **Time elapsed** since application
- **Follow-up date** if set
- **Role type** (keywords like "backend", "frontend", "data")

**Example outputs:**
- Applied → Suggests follow-up timing and networking
- OA → Recommends DSA practice and domain prep
- Interview → Provides interview preparation tips
- Rejected → Offers constructive next steps
- Offer → Guides negotiation and decision-making

The engine is designed to be **swappable** with real LLM APIs (OpenAI, Claude, Gemini) without changing routes or schemas.

## Advanced Extensions

### Add Real LLM Integration

Swap `app/services/ai_service.py`'s rule-based logic for OpenAI/Claude:

```python
import openai

def generate_ai_suggestion(application: JobApplication) -> str:
    prompt = f"Suggest next steps for {application.status} application to {application.company} for {application.role}"
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}]
    )
    return response.choices[0].message.content
```

### Add Database Migrations

Replace `Base.metadata.create_all()` with Alembic:

```bash
pip install alembic
alembic init alembic
alembic revision --autogenerate -m "Initial migration"
alembic upgrade head
```

### Add Rate Limiting

Protect endpoints from abuse:

```bash
pip install slowapi
```

```python
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter

@app.post("/auth/login")
@limiter.limit("5/minute")
async def login(...):
    ...
```

### Add Email Notifications

Send follow-up reminders:

```bash
pip install fastapi-mail
```

### Add File Upload

Store resumes and cover letters:

```python
from fastapi import UploadFile

@app.post("/applications/{id}/resume")
async def upload_resume(id: int, file: UploadFile):
    ...
```

## Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/amazing-feature`
3. Make your changes and commit: `git commit -m 'Add amazing feature'`
4. Push to the branch: `git push origin feature/amazing-feature`
5. Open a Pull Request

### Development Guidelines

- Follow PEP 8 style guide
- Add type hints to all functions
- Write docstrings for public functions
- Add tests for new features
- Update README if adding new features

## License

This project is open source and available for portfolio and educational purposes.

## Related Projects

- **Frontend Application**: [Job Tracker Frontend](./job-tracker-frontend/README.md) — React frontend with Vite and React Router

## Support

For issues, questions, or suggestions:
- Open an issue on GitHub
- Check existing issues for solutions
- Review the troubleshooting section above

---

Built with ❤️ using FastAPI and Python
