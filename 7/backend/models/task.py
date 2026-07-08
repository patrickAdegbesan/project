"""
models/task.py — Task model and CRUD operations
"""

import sqlite3
from datetime import datetime
from models.user import get_db


def init_tasks_table(conn):
    conn.execute("""
        CREATE TABLE IF NOT EXISTS tasks (
            id           INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id      INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
            title        TEXT    NOT NULL,
            description  TEXT    DEFAULT '',
            subject      TEXT    DEFAULT '',
            priority     TEXT    DEFAULT 'medium',   -- low | medium | high | urgent
            status       TEXT    DEFAULT 'pending',  -- pending | in_progress | completed | cancelled
            due_date     TEXT,
            estimated_minutes INTEGER DEFAULT 60,
            actual_minutes    INTEGER DEFAULT 0,
            tags         TEXT    DEFAULT '',         -- comma-separated
            recurrence   TEXT    DEFAULT 'none',     -- none | daily | weekly
            parent_id    INTEGER REFERENCES tasks(id),  -- for sub-tasks
            reminder_sent INTEGER DEFAULT 0,
            created_at   TEXT    NOT NULL,
            updated_at   TEXT    NOT NULL,
            completed_at TEXT
        )
    """)
    conn.commit()


# ---------------------------------------------------------------------------
# CRUD
# ---------------------------------------------------------------------------

def create_task(user_id, data: dict):
    now = datetime.utcnow().isoformat()
    with get_db() as conn:
        init_tasks_table(conn)
        cursor = conn.execute(
            """INSERT INTO tasks
               (user_id, title, description, subject, priority, status,
                due_date, estimated_minutes, tags, recurrence, parent_id,
                created_at, updated_at)
               VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)""",
            (
                user_id,
                data.get("title", "").strip(),
                data.get("description", "").strip(),
                data.get("subject", "").strip(),
                data.get("priority", "medium"),
                data.get("status", "pending"),
                data.get("due_date"),
                int(data.get("estimated_minutes", 60)),
                data.get("tags", ""),
                data.get("recurrence", "none"),
                data.get("parent_id"),
                now, now
            )
        )
        conn.commit()
        return get_task_by_id(cursor.lastrowid, user_id)


def get_task_by_id(task_id, user_id):
    with get_db() as conn:
        init_tasks_table(conn)
        row = conn.execute(
            "SELECT * FROM tasks WHERE id = ? AND user_id = ?",
            (task_id, user_id)
        ).fetchone()
        return dict(row) if row else None


def get_tasks(user_id, filters: dict = None):
    """Return tasks for a user with optional filters."""
    query = "SELECT * FROM tasks WHERE user_id = ?"
    params = [user_id]

    if filters:
        if filters.get("status"):
            query += " AND status = ?"
            params.append(filters["status"])
        if filters.get("priority"):
            query += " AND priority = ?"
            params.append(filters["priority"])
        if filters.get("subject"):
            query += " AND subject LIKE ?"
            params.append(f"%{filters['subject']}%")
        if filters.get("due_before"):
            query += " AND due_date <= ?"
            params.append(filters["due_before"])
        if filters.get("due_after"):
            query += " AND due_date >= ?"
            params.append(filters["due_after"])

    query += " ORDER BY due_date ASC, priority DESC, created_at DESC"

    with get_db() as conn:
        init_tasks_table(conn)
        rows = conn.execute(query, params).fetchall()
        return [dict(r) for r in rows]


def update_task(task_id, user_id, data: dict):
    allowed = {
        "title", "description", "subject", "priority", "status",
        "due_date", "estimated_minutes", "actual_minutes", "tags",
        "recurrence", "reminder_sent"
    }
    updates = {k: v for k, v in data.items() if k in allowed}
    if not updates:
        return get_task_by_id(task_id, user_id)

    updates["updated_at"] = datetime.utcnow().isoformat()

    # Track completion timestamp
    if updates.get("status") == "completed":
        updates["completed_at"] = datetime.utcnow().isoformat()

    set_clause = ", ".join(f"{k} = ?" for k in updates)
    values = list(updates.values()) + [task_id, user_id]

    with get_db() as conn:
        conn.execute(
            f"UPDATE tasks SET {set_clause} WHERE id = ? AND user_id = ?",
            values
        )
        conn.commit()
    return get_task_by_id(task_id, user_id)


def delete_task(task_id, user_id):
    with get_db() as conn:
        conn.execute(
            "DELETE FROM tasks WHERE id = ? AND user_id = ?",
            (task_id, user_id)
        )
        conn.commit()


def get_overdue_tasks(user_id):
    """Return non-completed tasks whose due_date has passed."""
    now = datetime.utcnow().isoformat()
    with get_db() as conn:
        init_tasks_table(conn)
        rows = conn.execute(
            """SELECT * FROM tasks
               WHERE user_id = ? AND due_date < ? AND status NOT IN ('completed','cancelled')
               ORDER BY due_date ASC""",
            (user_id, now)
        ).fetchall()
        return [dict(r) for r in rows]


def get_upcoming_tasks(user_id, hours=24):
    """Return tasks due within the next `hours` hours."""
    from datetime import timedelta
    now = datetime.utcnow()
    window = (now + timedelta(hours=hours)).isoformat()
    with get_db() as conn:
        init_tasks_table(conn)
        rows = conn.execute(
            """SELECT * FROM tasks
               WHERE user_id = ? AND due_date BETWEEN ? AND ?
               AND status NOT IN ('completed','cancelled')
               ORDER BY due_date ASC""",
            (user_id, now.isoformat(), window)
        ).fetchall()
        return [dict(r) for r in rows]
