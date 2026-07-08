"""
routes/admin_routes.py — Admin dashboard endpoints

All routes require a valid session token AND is_admin = 1 on the user record.

GET  /api/admin/stats            — system-wide summary statistics
GET  /api/admin/users            — list all users with per-user stats
GET  /api/admin/users/<id>       — single user detail + their tasks
DELETE /api/admin/users/<id>     — delete a user and all their data
PUT  /api/admin/users/<id>/toggle-admin — grant / revoke admin flag
GET  /api/admin/activity         — recent activity feed across all users
GET  /api/admin/subjects         — most popular subjects system-wide
GET  /api/admin/chart/signups    — daily signups over last 30 days
GET  /api/admin/chart/tasks      — daily task completions over last 30 days
"""

from flask import Blueprint, request
from datetime import datetime, date, timedelta
from models.user import get_db, safe_user
from utils.helpers import require_auth, success, error

admin_bp = Blueprint("admin", __name__, url_prefix="/api/admin")


# ---------------------------------------------------------------------------
# Admin-only guard decorator
# ---------------------------------------------------------------------------

from functools import wraps

def require_admin(f):
    """Wraps require_auth and additionally checks is_admin == 1."""
    @require_auth
    @wraps(f)
    def decorated(*args, current_user, **kwargs):
        if not current_user.get("is_admin"):
            return error("Admin access required.", 403)
        return f(*args, current_user=current_user, **kwargs)
    return decorated


# ---------------------------------------------------------------------------
# System-wide stats
# ---------------------------------------------------------------------------

@admin_bp.route("/stats", methods=["GET"])
@require_admin
def system_stats(current_user):
    with get_db() as conn:
        total_users    = conn.execute("SELECT COUNT(*) FROM users").fetchone()[0]
        total_tasks    = conn.execute("SELECT COUNT(*) FROM tasks").fetchone()[0]
        completed      = conn.execute("SELECT COUNT(*) FROM tasks WHERE status='completed'").fetchone()[0]
        total_minutes  = conn.execute("SELECT COALESCE(SUM(minutes),0) FROM study_logs").fetchone()[0]
        total_goals    = conn.execute("SELECT COUNT(*) FROM goals").fetchone()[0]
        achieved_goals = conn.execute("SELECT COUNT(*) FROM goals WHERE status='achieved'").fetchone()[0]
        total_blocks   = conn.execute("SELECT COUNT(*) FROM schedule_blocks").fetchone()[0]
        active_today   = conn.execute(
            "SELECT COUNT(DISTINCT user_id) FROM study_logs WHERE log_date = ?",
            (date.today().isoformat(),)
        ).fetchone()[0]
        new_users_7d = conn.execute(
            "SELECT COUNT(*) FROM users WHERE created_at >= ?",
            ((datetime.utcnow() - timedelta(days=7)).isoformat(),)
        ).fetchone()[0]
        overdue = conn.execute(
            "SELECT COUNT(*) FROM tasks WHERE due_date < ? AND status NOT IN ('completed','cancelled')",
            (datetime.utcnow().isoformat(),)
        ).fetchone()[0]

    completion_rate = round(completed / total_tasks * 100, 1) if total_tasks else 0.0

    return success({"stats": {
        "total_users":      total_users,
        "new_users_7d":     new_users_7d,
        "active_today":     active_today,
        "total_tasks":      total_tasks,
        "completed_tasks":  completed,
        "overdue_tasks":    overdue,
        "completion_rate":  completion_rate,
        "total_minutes":    total_minutes,
        "total_goals":      total_goals,
        "achieved_goals":   achieved_goals,
        "total_blocks":     total_blocks,
    }})


# ---------------------------------------------------------------------------
# User list
# ---------------------------------------------------------------------------

@admin_bp.route("/users", methods=["GET"])
@require_admin
def list_users(current_user):
    search = request.args.get("search", "").strip()
    with get_db() as conn:
        if search:
            rows = conn.execute(
                """SELECT u.*,
                   (SELECT COUNT(*) FROM tasks t WHERE t.user_id = u.id) AS task_count,
                   (SELECT COUNT(*) FROM tasks t WHERE t.user_id = u.id AND t.status='completed') AS completed_count,
                   (SELECT COALESCE(SUM(minutes),0) FROM study_logs s WHERE s.user_id = u.id) AS total_minutes
                   FROM users u
                   WHERE u.username LIKE ? OR u.email LIKE ? OR u.full_name LIKE ?
                   ORDER BY u.created_at DESC""",
                (f"%{search}%", f"%{search}%", f"%{search}%")
            ).fetchall()
        else:
            rows = conn.execute(
                """SELECT u.*,
                   (SELECT COUNT(*) FROM tasks t WHERE t.user_id = u.id) AS task_count,
                   (SELECT COUNT(*) FROM tasks t WHERE t.user_id = u.id AND t.status='completed') AS completed_count,
                   (SELECT COALESCE(SUM(minutes),0) FROM study_logs s WHERE s.user_id = u.id) AS total_minutes
                   FROM users u
                   ORDER BY u.created_at DESC"""
            ).fetchall()

    users = []
    for r in rows:
        u = dict(r)
        u.pop("password", None)
        users.append(u)

    return success({"users": users, "total": len(users)})


# ---------------------------------------------------------------------------
# Single user detail
# ---------------------------------------------------------------------------

@admin_bp.route("/users/<int:user_id>", methods=["GET"])
@require_admin
def user_detail(user_id, current_user):
    with get_db() as conn:
        user_row = conn.execute(
            "SELECT * FROM users WHERE id = ?", (user_id,)
        ).fetchone()
        if not user_row:
            return error("User not found.", 404)

        tasks = conn.execute(
            "SELECT * FROM tasks WHERE user_id = ? ORDER BY created_at DESC LIMIT 20",
            (user_id,)
        ).fetchall()

        logs = conn.execute(
            """SELECT log_date, SUM(minutes) as total_minutes
               FROM study_logs WHERE user_id = ?
               GROUP BY log_date ORDER BY log_date DESC LIMIT 30""",
            (user_id,)
        ).fetchall()

        goals = conn.execute(
            "SELECT * FROM goals WHERE user_id = ? ORDER BY created_at DESC",
            (user_id,)
        ).fetchall()

        # Subject breakdown
        subjects = conn.execute(
            """SELECT subject,
               COUNT(*) as total,
               SUM(CASE WHEN status='completed' THEN 1 ELSE 0 END) as done
               FROM tasks WHERE user_id = ? AND subject != ''
               GROUP BY subject ORDER BY total DESC""",
            (user_id,)
        ).fetchall()

    u = dict(user_row)
    u.pop("password", None)

    return success({
        "user":     u,
        "tasks":    [dict(t) for t in tasks],
        "logs":     [dict(l) for l in logs],
        "goals":    [dict(g) for g in goals],
        "subjects": [dict(s) for s in subjects],
    })


# ---------------------------------------------------------------------------
# Delete user
# ---------------------------------------------------------------------------

@admin_bp.route("/users/<int:user_id>", methods=["DELETE"])
@require_admin
def delete_user(user_id, current_user):
    if user_id == current_user["id"]:
        return error("You cannot delete your own account.", 400)
    with get_db() as conn:
        row = conn.execute("SELECT id FROM users WHERE id = ?", (user_id,)).fetchone()
        if not row:
            return error("User not found.", 404)
        conn.execute("DELETE FROM users WHERE id = ?", (user_id,))
        conn.commit()
    return success(message="User deleted successfully.")


# ---------------------------------------------------------------------------
# Toggle admin flag
# ---------------------------------------------------------------------------

@admin_bp.route("/users/<int:user_id>/toggle-admin", methods=["PUT"])
@require_admin
def toggle_admin(user_id, current_user):
    if user_id == current_user["id"]:
        return error("You cannot change your own admin status.", 400)
    with get_db() as conn:
        row = conn.execute("SELECT id, is_admin FROM users WHERE id = ?", (user_id,)).fetchone()
        if not row:
            return error("User not found.", 404)
        new_val = 0 if row["is_admin"] else 1
        conn.execute("UPDATE users SET is_admin = ? WHERE id = ?", (new_val, user_id))
        conn.commit()
    return success({
        "is_admin": new_val,
        "message": f"Admin access {'granted' if new_val else 'revoked'}."
    })


# ---------------------------------------------------------------------------
# Recent activity feed
# ---------------------------------------------------------------------------

@admin_bp.route("/activity", methods=["GET"])
@require_admin
def activity_feed(current_user):
    limit = min(int(request.args.get("limit", 30)), 100)
    with get_db() as conn:
        # Recent task completions
        completions = conn.execute(
            """SELECT t.title, t.completed_at as event_time, u.username, u.full_name,
               'task_completed' as event_type
               FROM tasks t JOIN users u ON u.id = t.user_id
               WHERE t.status = 'completed' AND t.completed_at IS NOT NULL
               ORDER BY t.completed_at DESC LIMIT ?""",
            (limit // 2,)
        ).fetchall()

        # Recent registrations
        signups = conn.execute(
            """SELECT username, full_name, created_at as event_time,
               'user_signup' as event_type
               FROM users ORDER BY created_at DESC LIMIT ?""",
            (limit // 2,)
        ).fetchall()

    feed = []
    for r in completions:
        feed.append({
            "type":      "task_completed",
            "time":      r["event_time"],
            "username":  r["username"],
            "full_name": r["full_name"],
            "detail":    r["title"],
        })
    for r in signups:
        feed.append({
            "type":      "user_signup",
            "time":      r["event_time"],
            "username":  r["username"],
            "full_name": r["full_name"],
            "detail":    "Joined the platform",
        })

    feed.sort(key=lambda x: x["time"] or "", reverse=True)
    return success({"activity": feed[:limit]})


# ---------------------------------------------------------------------------
# Popular subjects
# ---------------------------------------------------------------------------

@admin_bp.route("/subjects", methods=["GET"])
@require_admin
def popular_subjects(current_user):
    with get_db() as conn:
        rows = conn.execute(
            """SELECT subject,
               COUNT(*) as total_tasks,
               SUM(CASE WHEN status='completed' THEN 1 ELSE 0 END) as completed,
               COUNT(DISTINCT user_id) as user_count
               FROM tasks WHERE subject != ''
               GROUP BY subject ORDER BY total_tasks DESC LIMIT 15"""
        ).fetchall()
    subjects = [dict(r) for r in rows]
    for s in subjects:
        s["completion_rate"] = round(s["completed"] / s["total_tasks"] * 100, 1) if s["total_tasks"] else 0
    return success({"subjects": subjects})


# ---------------------------------------------------------------------------
# Chart data — daily signups (last 30 days)
# ---------------------------------------------------------------------------

@admin_bp.route("/chart/signups", methods=["GET"])
@require_admin
def chart_signups(current_user):
    today = date.today()
    start = (today - timedelta(days=29)).isoformat()
    with get_db() as conn:
        rows = conn.execute(
            """SELECT DATE(created_at) as day, COUNT(*) as count
               FROM users WHERE created_at >= ?
               GROUP BY day ORDER BY day""",
            (start,)
        ).fetchall()

    counts = {r["day"]: r["count"] for r in rows}
    trend = []
    for i in range(30):
        day = (today - timedelta(days=29 - i)).isoformat()
        trend.append({"date": day, "count": counts.get(day, 0)})
    return success({"trend": trend})


# ---------------------------------------------------------------------------
# Chart data — daily task completions (last 30 days)
# ---------------------------------------------------------------------------

@admin_bp.route("/chart/tasks", methods=["GET"])
@require_admin
def chart_tasks(current_user):
    today = date.today()
    start = (today - timedelta(days=29)).isoformat()
    with get_db() as conn:
        rows = conn.execute(
            """SELECT DATE(completed_at) as day, COUNT(*) as count
               FROM tasks WHERE status='completed' AND completed_at >= ?
               GROUP BY day ORDER BY day""",
            (start,)
        ).fetchall()

    counts = {r["day"]: r["count"] for r in rows}
    trend = []
    for i in range(30):
        day = (today - timedelta(days=29 - i)).isoformat()
        trend.append({"date": day, "count": counts.get(day, 0)})
    return success({"trend": trend})
