"""
services/reminder_service.py — Reminder logic for upcoming and overdue tasks.

Reminders are stored as in-app notifications in the `reminders` table.
The frontend polls /api/reminders to display them.
"""

from datetime import datetime, timedelta
from models.user import get_db
from models.task import get_upcoming_tasks, get_overdue_tasks, update_task


def init_reminders_table(conn):
    conn.execute("""
        CREATE TABLE IF NOT EXISTS reminders (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id     INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
            task_id     INTEGER REFERENCES tasks(id) ON DELETE CASCADE,
            message     TEXT    NOT NULL,
            type        TEXT    DEFAULT 'upcoming',  -- upcoming | overdue | goal
            is_read     INTEGER DEFAULT 0,
            created_at  TEXT    NOT NULL
        )
    """)
    conn.commit()


def _add_reminder(user_id, message, task_id=None, rtype="upcoming"):
    now = datetime.utcnow().isoformat()
    with get_db() as conn:
        init_reminders_table(conn)
        conn.execute(
            """INSERT INTO reminders (user_id, task_id, message, type, created_at)
               VALUES (?,?,?,?,?)""",
            (user_id, task_id, message, rtype, now)
        )
        conn.commit()


def _already_reminded(user_id, task_id) -> bool:
    """Avoid duplicate reminders for the same task within 12 hours."""
    cutoff = (datetime.utcnow() - timedelta(hours=12)).isoformat()
    with get_db() as conn:
        init_reminders_table(conn)
        row = conn.execute(
            """SELECT id FROM reminders
               WHERE user_id = ? AND task_id = ? AND created_at > ?""",
            (user_id, task_id, cutoff)
        ).fetchone()
        return row is not None


def check_and_create_reminders(user_id: int):
    """
    Called on each authenticated request (or scheduled).
    Creates reminder records for upcoming and overdue tasks.
    """
    # Upcoming (within 24h)
    for task in get_upcoming_tasks(user_id, hours=24):
        if not _already_reminded(user_id, task["id"]):
            due = task.get("due_date", "soon")
            _add_reminder(
                user_id,
                f"Reminder: '{task['title']}' is due on {due}.",
                task_id=task["id"],
                rtype="upcoming",
            )
            update_task(task["id"], user_id, {"reminder_sent": 1})

    # Overdue
    for task in get_overdue_tasks(user_id):
        if not _already_reminded(user_id, task["id"]):
            _add_reminder(
                user_id,
                f"Overdue: '{task['title']}' was due on {task.get('due_date', 'unknown')}.",
                task_id=task["id"],
                rtype="overdue",
            )


def get_reminders(user_id: int, unread_only=False) -> list[dict]:
    query = "SELECT * FROM reminders WHERE user_id = ?"
    params = [user_id]
    if unread_only:
        query += " AND is_read = 0"
    query += " ORDER BY created_at DESC LIMIT 50"
    with get_db() as conn:
        init_reminders_table(conn)
        rows = conn.execute(query, params).fetchall()
        return [dict(r) for r in rows]


def mark_reminders_read(user_id: int, reminder_ids: list[int]):
    if not reminder_ids:
        return
    placeholders = ",".join("?" * len(reminder_ids))
    with get_db() as conn:
        conn.execute(
            f"UPDATE reminders SET is_read = 1 WHERE user_id = ? AND id IN ({placeholders})",
            [user_id] + reminder_ids
        )
        conn.commit()


def get_unread_count(user_id: int) -> int:
    with get_db() as conn:
        init_reminders_table(conn)
        row = conn.execute(
            "SELECT COUNT(*) as cnt FROM reminders WHERE user_id = ? AND is_read = 0",
            (user_id,)
        ).fetchone()
        return row["cnt"] if row else 0
