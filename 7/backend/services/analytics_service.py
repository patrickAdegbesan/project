"""
services/analytics_service.py — Aggregate analytics for the dashboard.
"""

from datetime import datetime, date, timedelta
from models.task import get_tasks
from models.progress import get_study_logs, get_daily_totals, get_goals


def get_dashboard_stats(user_id: int) -> dict:
    """Return all data required by the frontend analytics dashboard."""
    today = date.today()
    seven_days_ago  = (today - timedelta(days=6)).isoformat()
    thirty_days_ago = (today - timedelta(days=29)).isoformat()

    tasks = get_tasks(user_id)
    logs_30 = get_study_logs(user_id, start_date=thirty_days_ago)

    # -----------------------------------------------------------------------
    # Task summary
    # -----------------------------------------------------------------------
    total       = len(tasks)
    completed   = sum(1 for t in tasks if t["status"] == "completed")
    in_progress = sum(1 for t in tasks if t["status"] == "in_progress")
    pending     = sum(1 for t in tasks if t["status"] == "pending")
    overdue     = sum(
        1 for t in tasks
        if t.get("due_date") and t["due_date"] < datetime.utcnow().isoformat()
        and t["status"] not in ("completed", "cancelled")
    )
    completion_rate = round(completed / total * 100, 1) if total else 0.0

    # -----------------------------------------------------------------------
    # Priority breakdown
    # -----------------------------------------------------------------------
    priority_counts = {"low": 0, "medium": 0, "high": 0, "urgent": 0}
    for t in tasks:
        p = t.get("priority", "medium")
        priority_counts[p] = priority_counts.get(p, 0) + 1

    # -----------------------------------------------------------------------
    # Study hours — last 7 days (for bar chart)
    # -----------------------------------------------------------------------
    daily_totals = get_daily_totals(user_id, seven_days_ago, today.isoformat())
    study_hours_week = []
    for i in range(7):
        day = (today - timedelta(days=6 - i)).isoformat()
        mins = daily_totals.get(day, 0)
        study_hours_week.append({"date": day, "minutes": mins, "hours": round(mins / 60, 2)})

    total_minutes_7d  = sum(d["minutes"] for d in study_hours_week)
    total_minutes_30d = sum(log["minutes"] for log in logs_30)

    # -----------------------------------------------------------------------
    # Subject distribution (pie chart)
    # -----------------------------------------------------------------------
    subject_map = {}
    for t in tasks:
        sub = t.get("subject") or "General"
        subject_map[sub] = subject_map.get(sub, 0) + 1
    subject_distribution = [{"subject": k, "count": v} for k, v in subject_map.items()]

    # -----------------------------------------------------------------------
    # Task completion trend — last 30 days
    # -----------------------------------------------------------------------
    completion_trend = _completion_trend(tasks, thirty_days_ago, today.isoformat())

    # -----------------------------------------------------------------------
    # Goals progress
    # -----------------------------------------------------------------------
    goals = get_goals(user_id, status="active")
    goals_summary = []
    for g in goals:
        target = g.get("target_value") or 1
        current = g.get("current_value") or 0
        pct = round(min(current / target * 100, 100), 1)
        goals_summary.append({
            "id": g["id"],
            "title": g["title"],
            "metric": g["metric"],
            "target_value": target,
            "current_value": current,
            "percent": pct,
            "target_date": g.get("target_date"),
        })

    # -----------------------------------------------------------------------
    # Recent completions (last 5)
    # -----------------------------------------------------------------------
    recent_completed = sorted(
        [t for t in tasks if t["status"] == "completed" and t.get("completed_at")],
        key=lambda x: x["completed_at"],
        reverse=True
    )[:5]

    return {
        "task_summary": {
            "total": total,
            "completed": completed,
            "in_progress": in_progress,
            "pending": pending,
            "overdue": overdue,
            "completion_rate": completion_rate,
        },
        "priority_breakdown": priority_counts,
        "study_hours_week": study_hours_week,
        "total_minutes_7d": total_minutes_7d,
        "total_minutes_30d": total_minutes_30d,
        "subject_distribution": subject_distribution,
        "completion_trend": completion_trend,
        "goals_summary": goals_summary,
        "recent_completed": recent_completed,
    }


def _completion_trend(tasks: list, start_date: str, end_date: str) -> list[dict]:
    """Return daily completed-task counts between start_date and end_date."""
    start = datetime.strptime(start_date, "%Y-%m-%d").date()
    end   = datetime.strptime(end_date,   "%Y-%m-%d").date()

    # Build {date: count} map
    counts = {}
    for t in tasks:
        if t["status"] == "completed" and t.get("completed_at"):
            try:
                d = t["completed_at"][:10]  # YYYY-MM-DD portion
                if start_date <= d <= end_date:
                    counts[d] = counts.get(d, 0) + 1
            except Exception:
                pass

    trend = []
    current = start
    while current <= end:
        iso = current.isoformat()
        trend.append({"date": iso, "completed": counts.get(iso, 0)})
        current += timedelta(days=1)
    return trend
