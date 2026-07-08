"""
services/adaptive_engine.py — Adaptive learning and recommendation engine

Analyses a user's task completion patterns and study logs to produce
personalised recommendations. Adjusts for ASD/ADHD neuro profiles.
"""

from datetime import datetime, date, timedelta
from models.task import get_tasks
from models.progress import get_study_logs, get_daily_totals
from models.user import get_user_by_id


# ---------------------------------------------------------------------------
# Core analysis helpers
# ---------------------------------------------------------------------------

def _completion_rate(tasks: list) -> float:
    """Fraction of non-cancelled tasks that are completed."""
    active = [t for t in tasks if t["status"] != "cancelled"]
    if not active:
        return 0.0
    done = [t for t in active if t["status"] == "completed"]
    return len(done) / len(active)


def _average_actual_minutes(tasks: list) -> float:
    logged = [t for t in tasks if t.get("actual_minutes", 0) > 0]
    if not logged:
        return 0.0
    return sum(t["actual_minutes"] for t in logged) / len(logged)


def _hour_distribution(logs: list) -> dict:
    """Return {hour_of_day: total_minutes} for the last 30 days."""
    dist = {h: 0 for h in range(24)}
    for log in logs:
        try:
            dt = datetime.fromisoformat(log["created_at"])
            dist[dt.hour] += log["minutes"]
        except Exception:
            pass
    return dist


def _peak_study_hours(dist: dict, top_n=3) -> list[int]:
    """Return the top_n hours with the most accumulated study minutes."""
    sorted_hours = sorted(dist.items(), key=lambda x: x[1], reverse=True)
    return [h for h, _ in sorted_hours[:top_n] if sorted_hours[0][1] > 0]


def _subject_breakdown(tasks: list) -> dict:
    """Return {subject: {total, done, rate}} for all subjects."""
    subjects = {}
    for t in tasks:
        sub = t.get("subject") or "General"
        if sub not in subjects:
            subjects[sub] = {"total": 0, "done": 0}
        subjects[sub]["total"] += 1
        if t["status"] == "completed":
            subjects[sub]["done"] += 1
    for sub in subjects:
        total = subjects[sub]["total"]
        subjects[sub]["rate"] = round(subjects[sub]["done"] / total, 2) if total else 0.0
    return subjects


# ---------------------------------------------------------------------------
# Neuro-adaptive parameters
# ---------------------------------------------------------------------------

def _pomodoro_params(neuro_mode: str) -> dict:
    """
    Return recommended Pomodoro-style intervals.
    - standard : 25 min work / 5 min break
    - adhd     : 15 min work / 5 min break  (shorter focus bursts)
    - asd      : 30 min work / 10 min break (predictable, structured)
    """
    profiles = {
        "standard": {"work_minutes": 25, "break_minutes": 5,  "long_break": 15},
        "adhd":     {"work_minutes": 15, "break_minutes": 5,  "long_break": 10},
        "asd":      {"work_minutes": 30, "break_minutes": 10, "long_break": 20},
    }
    return profiles.get(neuro_mode, profiles["standard"])


def _reminder_frequency(neuro_mode: str) -> str:
    """Return recommended reminder frequency label."""
    return {"standard": "normal", "adhd": "frequent", "asd": "structured"}.get(
        neuro_mode, "normal"
    )


# ---------------------------------------------------------------------------
# Task breakdown suggestion
# ---------------------------------------------------------------------------

def _suggest_subtasks(task: dict) -> list[str]:
    """
    Heuristic subtask suggestions for a given task.
    Uses estimated_minutes as a proxy for complexity.
    """
    est = task.get("estimated_minutes", 60)
    title = task.get("title", "Task")
    subject = task.get("subject", "")

    if est <= 30:
        return []  # Already small enough

    steps = [
        f"Review notes / materials for '{title}'",
        f"Outline key points or steps for '{title}'",
        f"Work on main body of '{title}'",
        f"Revise and check '{title}'",
    ]
    if subject:
        steps.insert(0, f"Gather {subject} resources for '{title}'")
    # Return proportional number of steps based on size
    if est > 180:
        return steps
    elif est > 90:
        return steps[1:]
    else:
        return steps[1:3]


# ---------------------------------------------------------------------------
# Main recommendation function
# ---------------------------------------------------------------------------

def generate_recommendations(user_id: int) -> dict:
    """
    Return a recommendations dict for the given user:
    {
        "completion_rate": float,
        "peak_hours": [int, ...],
        "pomodoro": {...},
        "subject_breakdown": {...},
        "tips": [str, ...],
        "urgent_tasks": [task, ...],
        "subtask_suggestions": [{task_id, title, subtasks}, ...],
        "reminder_mode": str,
        "weekly_study_minutes": int,
    }
    """
    user = get_user_by_id(user_id)
    if not user:
        return {}

    neuro_mode = user.get("neuro_mode", "standard")

    # Fetch data
    all_tasks = get_tasks(user_id)
    today = date.today()
    thirty_days_ago = (today - timedelta(days=30)).isoformat()
    logs = get_study_logs(user_id, start_date=thirty_days_ago)
    week_start = (today - timedelta(days=today.weekday())).isoformat()
    daily = get_daily_totals(user_id, week_start, today.isoformat())
    weekly_minutes = sum(daily.values())

    # Analytics
    rate = _completion_rate(all_tasks)
    hour_dist = _hour_distribution(logs)
    peak = _peak_study_hours(hour_dist)
    subjects = _subject_breakdown(all_tasks)
    pomodoro = _pomodoro_params(neuro_mode)
    reminder = _reminder_frequency(neuro_mode)

    # Urgent tasks (due in < 48 h, not completed)
    two_days = (datetime.utcnow() + timedelta(hours=48)).isoformat()
    urgent = [
        t for t in all_tasks
        if t.get("due_date") and t["due_date"] <= two_days
        and t["status"] not in ("completed", "cancelled")
    ]

    # Subtask suggestions for large pending tasks
    large = [
        t for t in all_tasks
        if t["status"] in ("pending", "in_progress")
        and t.get("estimated_minutes", 0) > 60
    ][:5]
    subtask_suggestions = [
        {"task_id": t["id"], "title": t["title"], "subtasks": _suggest_subtasks(t)}
        for t in large
        if _suggest_subtasks(t)
    ]

    # Human-readable tips
    tips = _build_tips(rate, peak, neuro_mode, weekly_minutes, subjects)

    return {
        "completion_rate": round(rate, 2),
        "peak_hours": peak,
        "pomodoro": pomodoro,
        "subject_breakdown": subjects,
        "tips": tips,
        "urgent_tasks": urgent,
        "subtask_suggestions": subtask_suggestions,
        "reminder_mode": reminder,
        "weekly_study_minutes": weekly_minutes,
    }


def _build_tips(rate, peak_hours, neuro_mode, weekly_minutes, subjects) -> list[str]:
    tips = []

    # Completion rate advice
    if rate < 0.40:
        tips.append(
            "Your completion rate is below 40%. Try breaking larger tasks into "
            "smaller steps and tackling one at a time."
        )
    elif rate < 0.70:
        tips.append(
            "You're completing about half your tasks. Prioritise your top 3 "
            "tasks each morning and mark progress as you go."
        )
    else:
        tips.append(
            "Great completion rate! Keep up the momentum and challenge yourself "
            "with slightly larger goals."
        )

    # Study hours advice
    if weekly_minutes < 60:
        tips.append("You've logged very few study hours this week. Even 30 minutes daily makes a big difference.")
    elif weekly_minutes > 600:
        tips.append("You're putting in a lot of hours — make sure to schedule regular breaks to avoid burnout.")

    # Peak hour advice
    if peak_hours:
        hour_label = ", ".join(f"{h:02d}:00" for h in peak_hours)
        tips.append(f"Your most productive hours are around {hour_label}. Schedule difficult tasks then.")
    else:
        tips.append("Log your study sessions consistently so the system can detect your peak productivity hours.")

    # Neuro-specific advice
    if neuro_mode == "adhd":
        tips.append("ADHD tip: Use short 15-minute focus sprints with a 5-minute movement break. Tick off each sprint.")
        tips.append("ADHD tip: Keep your task list visible and use colour-coding to distinguish subjects.")
    elif neuro_mode == "asd":
        tips.append("ASD tip: Follow the same schedule structure each day — consistency reduces cognitive load.")
        tips.append("ASD tip: Use the structured daily view and block unexpected tasks in a 'buffer' slot.")

    # Weakest subject
    if subjects:
        weakest = min(subjects.items(), key=lambda x: x[1]["rate"])
        if weakest[1]["rate"] < 0.5 and weakest[1]["total"] > 1:
            tips.append(
                f"You have the lowest completion rate in '{weakest[0]}'. "
                "Consider dedicating a focused session to it this week."
            )

    return tips
