"""
Rule-based AI suggestion engine.

This module is intentionally isolated from the route layer so it can later
be swapped for a real LLM call (OpenAI / Gemini / Claude) without touching
any routing or DB logic — only this function's internals would change,
and the function signature (JobApplication in, suggestion string out)
would stay the same.
"""
from datetime import date
from typing import Optional

from app.models import JobApplication, ApplicationStatus

# Rough mapping of role keywords -> relevant prep topics, used to make
# suggestions feel tailored to the specific role rather than generic.
ROLE_TOPIC_HINTS = {
    "backend": "FastAPI/Django fundamentals, REST API design, and SQL joins",
    "frontend": "React component design, state management, and accessibility basics",
    "full stack": "end-to-end feature design across the frontend and backend",
    "data": "SQL, data cleaning, and basic statistics",
    "ml": "core ML concepts, model evaluation metrics, and a recent project walkthrough",
    "ai": "LLM/agent fundamentals and a recent project walkthrough",
    "android": "Kotlin/Java fundamentals and Android lifecycle concepts",
    "devops": "CI/CD pipelines, containers, and basic cloud networking",
    "qa": "test case design and common testing frameworks",
}


def _topic_hint_for_role(role: str) -> str:
    role_lower = role.lower()
    for keyword, hint in ROLE_TOPIC_HINTS.items():
        if keyword in role_lower:
            return hint
    return "your core CS fundamentals (DSA, OOP, DBMS, OS) and one strong project walkthrough"


def _days_since(target: Optional[date]) -> Optional[int]:
    if target is None:
        return None
    return (date.today() - target).days


def generate_suggestion(application: JobApplication) -> str:
    """
    Build a natural-language next-step suggestion for a single application,
    based on its status, company, role, dates, and notes.
    """
    company = application.company
    role = application.role
    status = application.status
    topic_hint = _topic_hint_for_role(role)
    days_applied = _days_since(application.date_applied)
    days_to_followup = (
        (application.follow_up_date - date.today()).days
        if application.follow_up_date
        else None
    )

    if status == ApplicationStatus.APPLIED:
        if days_applied is None:
            timing = "Since there's no applied date on file, set one so we can time your follow-up properly."
        elif days_applied < 4:
            timing = (
                f"You applied {days_applied} day(s) ago, so it's still early — "
                "give it a few more days before reaching out."
            )
        else:
            timing = (
                f"It's been {days_applied} days since you applied, which is a good window "
                "to send a polite follow-up email to the recruiter or hiring manager."
            )
        return (
            f"You applied for the {role} role at {company}. {timing} "
            f"In the meantime, use the wait time to brush up on {topic_hint}."
        )

    if status == ApplicationStatus.OA:
        return (
            f"Your online assessment for the {role} role at {company} is the next hurdle. "
            "Spend the next few days on timed DSA practice (arrays, strings, trees, graphs), "
            "a quick pass on aptitude/MCQ-style questions, and a refresher on "
            f"{topic_hint}. Treat it like a real exam: simulate the time limit at least once."
        )

    if status == ApplicationStatus.INTERVIEW:
        followup_note = (
            f"Your next follow-up is in {days_to_followup} day(s) — keep that date in mind."
            if days_to_followup is not None and days_to_followup >= 0
            else "If you don't have one yet, set a follow-up date so this doesn't slip."
        )
        return (
            f"You have an interview stage for the {role} role at {company}. "
            f"Research the company's products and recent news, prepare a 2-3 minute walkthrough "
            f"of your strongest project, and revise {topic_hint}. {followup_note}"
        )

    if status == ApplicationStatus.REJECTED:
        notes_line = (
            f" Your notes mention: \"{application.notes.strip()[:120]}\" — "
            "worth revisiting before your next application."
            if application.notes
            else " Consider jotting down what you think went wrong while it's fresh."
        )
        return (
            f"The {role} application at {company} didn't work out this time, and that's okay — "
            "it happens to almost everyone. Take a few minutes to write down what you'd do "
            f"differently next time.{notes_line} Then redirect that energy into applying to "
            "a couple of similar roles this week rather than dwelling on this one."
        )

    if status == ApplicationStatus.OFFER:
        return (
            f"Congratulations on the offer for the {role} role at {company}! "
            "Before accepting, compare it against your other options on stipend/CTC, "
            "location and remote flexibility, the learning curve and tech stack, and the "
            "team you'd be joining. Make sure you also note the joining date and any "
            "documents you need to submit."
        )

    # Fallback for any unexpected status value
    return (
        f"No specific guidance is available for the current status of your {role} "
        f"application at {company}. Double-check the status value is correct."
    )
