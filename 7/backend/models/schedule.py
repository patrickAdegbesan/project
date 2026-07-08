"""
models/schedule.py — Study schedule and time-block model
"""

import sqlite3
from datetime import datetime
from models.user import get_db


def init_schedule_table(conn):
    conn.execute("""
        CREATE TABLE IF NOT EXISTS schedule_blocks (
            id           INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id      INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
            task_id      INTEGER REFERENCES tasks(id) ON DELETE SET NULL,
            title        TEXT    NOT NULL,
            subject      TEXT    DEFAULT '',
            block_date   TEXT    NOT NULL,   -- ISO date YYYY-MM-DD
            start_time   TEXT    NOT NULL,   -- HH:MM (24h)
            end_time     TEXT    NOT NULL,
            block_type   TEXT    DEFAULT 'study',  -- study | break | review | exam
            color        TEXT    DEFAULT '#4A90D9',
            notes        TEXT    DEFAULT '',
            completed    INTEGER DEFAULT 0,
            created_at   TEXT    NOT NULL,
            updated_at   TEXT    NOT NULL
        )
    """)
    conn.commit()


# ---------------------------------------------------------------------------
# CRUD
# ---------------------------------------------------------------------------

def create_block(user_id, data: dict):
    now = datetime.utcnow().isoformat()
    with get_db() as conn:
        init_schedule_table(conn)
        cursor = conn.execute(
            """INSERT INTO schedule_blocks
               (user_id, task_id, title, subject, block_date, start_time,
                end_time, block_type, color, notes, created_at, updated_at)
               VALUES (?,?,?,?,?,?,?,?,?,?,?,?)""",
            (
                user_id,
                data.get("task_id"),
                data.get("title", "Study Block").strip(),
                data.get("subject", "").strip(),
                data.get("block_date"),
                data.get("start_time", "09:00"),
                data.get("end_time", "10:00"),
                data.get("block_type", "study"),
                data.get("color", "#4A90D9"),
                data.get("notes", "").strip(),
                now, now
            )
        )
        conn.commit()
        return get_block_by_id(cursor.lastrowid, user_id)


def get_block_by_id(block_id, user_id):
    with get_db() as conn:
        init_schedule_table(conn)
        row = conn.execute(
            "SELECT * FROM schedule_blocks WHERE id = ? AND user_id = ?",
            (block_id, user_id)
        ).fetchone()
        return dict(row) if row else None


def get_blocks_by_date_range(user_id, start_date, end_date):
    with get_db() as conn:
        init_schedule_table(conn)
        rows = conn.execute(
            """SELECT * FROM schedule_blocks
               WHERE user_id = ? AND block_date BETWEEN ? AND ?
               ORDER BY block_date ASC, start_time ASC""",
            (user_id, start_date, end_date)
        ).fetchall()
        return [dict(r) for r in rows]


def get_blocks_by_week(user_id, week_start):
    """week_start: YYYY-MM-DD of Monday."""
    from datetime import timedelta
    start = datetime.strptime(week_start, "%Y-%m-%d")
    end = (start + timedelta(days=6)).strftime("%Y-%m-%d")
    return get_blocks_by_date_range(user_id, week_start, end)


def update_block(block_id, user_id, data: dict):
    allowed = {
        "title", "subject", "block_date", "start_time", "end_time",
        "block_type", "color", "notes", "completed", "task_id"
    }
    updates = {k: v for k, v in data.items() if k in allowed}
    if not updates:
        return get_block_by_id(block_id, user_id)

    updates["updated_at"] = datetime.utcnow().isoformat()
    set_clause = ", ".join(f"{k} = ?" for k in updates)
    values = list(updates.values()) + [block_id, user_id]

    with get_db() as conn:
        conn.execute(
            f"UPDATE schedule_blocks SET {set_clause} WHERE id = ? AND user_id = ?",
            values
        )
        conn.commit()
    return get_block_by_id(block_id, user_id)


def delete_block(block_id, user_id):
    with get_db() as conn:
        conn.execute(
            "DELETE FROM schedule_blocks WHERE id = ? AND user_id = ?",
            (block_id, user_id)
        )
        conn.commit()
