"""
models/progress.py — Progress logs, goals, and study-hour records
"""

import sqlite3
from datetime import datetime, date
from models.user import get_db


def init_progress_tables(conn):
    # Daily study-hour log
    conn.execute("""
        CREATE TABLE IF NOT EXISTS study_logs (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id     INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
            log_date    TEXT    NOT NULL,   -- YYYY-MM-DD
            subject     TEXT    DEFAULT '',
            minutes     INTEGER NOT NULL DEFAULT 0,
            task_id     INTEGER REFERENCES tasks(id) ON DELETE SET NULL,
            note        TEXT    DEFAULT '',
            created_at  TEXT    NOT NULL
        )
    """)
    # Academic goals
    conn.execute("""
        CREATE TABLE IF NOT EXISTS goals (
            id           INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id      INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
            title        TEXT    NOT NULL,
            description  TEXT    DEFAULT '',
            target_date  TEXT,
            metric       TEXT    DEFAULT 'tasks',    -- tasks | hours | score
            target_value REAL    DEFAULT 10,
            current_value REAL   DEFAULT 0,
            status       TEXT    DEFAULT 'active',   -- active | achieved | cancelled
            created_at   TEXT    NOT NULL,
            updated_at   TEXT    NOT NULL
        )
    """)
    conn.commit()


# ---------------------------------------------------------------------------
# Study log operations
# ---------------------------------------------------------------------------

def log_study_session(user_id, minutes, subject="", task_id=None, note="", log_date=None):
    now = datetime.utcnow().isoformat()
    day = log_date or date.today().isoformat()
    with get_db() as conn:
        init_progress_tables(conn)
        cursor = conn.execute(
            """INSERT INTO study_logs
               (user_id, log_date, subject, minutes, task_id, note, created_at)
               VALUES (?,?,?,?,?,?,?)""",
            (user_id, day, subject, minutes, task_id, note, now)
        )
        conn.commit()
        return cursor.lastrowid


def get_study_logs(user_id, start_date=None, end_date=None):
    query = "SELECT * FROM study_logs WHERE user_id = ?"
    params = [user_id]
    if start_date:
        query += " AND log_date >= ?"
        params.append(start_date)
    if end_date:
        query += " AND log_date <= ?"
        params.append(end_date)
    query += " ORDER BY log_date DESC, created_at DESC"
    with get_db() as conn:
        init_progress_tables(conn)
        rows = conn.execute(query, params).fetchall()
        return [dict(r) for r in rows]


def get_daily_totals(user_id, start_date, end_date):
    """Return {date: total_minutes} for a date range."""
    with get_db() as conn:
        init_progress_tables(conn)
        rows = conn.execute(
            """SELECT log_date, SUM(minutes) as total
               FROM study_logs WHERE user_id = ?
               AND log_date BETWEEN ? AND ?
               GROUP BY log_date ORDER BY log_date""",
            (user_id, start_date, end_date)
        ).fetchall()
        return {r["log_date"]: r["total"] for r in rows}


# ---------------------------------------------------------------------------
# Goal operations
# ---------------------------------------------------------------------------

def create_goal(user_id, data: dict):
    now = datetime.utcnow().isoformat()
    with get_db() as conn:
        init_progress_tables(conn)
        cursor = conn.execute(
            """INSERT INTO goals
               (user_id, title, description, target_date, metric,
                target_value, status, created_at, updated_at)
               VALUES (?,?,?,?,?,?,?,?,?)""",
            (
                user_id,
                data.get("title", "").strip(),
                data.get("description", "").strip(),
                data.get("target_date"),
                data.get("metric", "tasks"),
                float(data.get("target_value", 10)),
                "active",
                now, now
            )
        )
        conn.commit()
        return get_goal_by_id(cursor.lastrowid, user_id)


def get_goal_by_id(goal_id, user_id):
    with get_db() as conn:
        init_progress_tables(conn)
        row = conn.execute(
            "SELECT * FROM goals WHERE id = ? AND user_id = ?",
            (goal_id, user_id)
        ).fetchone()
        return dict(row) if row else None


def get_goals(user_id, status=None):
    query = "SELECT * FROM goals WHERE user_id = ?"
    params = [user_id]
    if status:
        query += " AND status = ?"
        params.append(status)
    query += " ORDER BY target_date ASC, created_at DESC"
    with get_db() as conn:
        init_progress_tables(conn)
        rows = conn.execute(query, params).fetchall()
        return [dict(r) for r in rows]


def update_goal(goal_id, user_id, data: dict):
    allowed = {"title", "description", "target_date", "metric",
               "target_value", "current_value", "status"}
    updates = {k: v for k, v in data.items() if k in allowed}
    if not updates:
        return get_goal_by_id(goal_id, user_id)
    updates["updated_at"] = datetime.utcnow().isoformat()
    set_clause = ", ".join(f"{k} = ?" for k in updates)
    values = list(updates.values()) + [goal_id, user_id]
    with get_db() as conn:
        conn.execute(
            f"UPDATE goals SET {set_clause} WHERE id = ? AND user_id = ?",
            values
        )
        conn.commit()
    return get_goal_by_id(goal_id, user_id)


def delete_goal(goal_id, user_id):
    with get_db() as conn:
        conn.execute(
            "DELETE FROM goals WHERE id = ? AND user_id = ?",
            (goal_id, user_id)
        )
        conn.commit()
