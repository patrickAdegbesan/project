"""
models/user.py — User model and database operations
"""

import sqlite3
import hashlib
import secrets
from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash, check_password_hash
from config import active_config as cfg


def get_db():
    """Return a database connection with row_factory set."""
    conn = sqlite3.connect(cfg.DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_users_table(conn):
    conn.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            username    TEXT    NOT NULL UNIQUE,
            email       TEXT    NOT NULL UNIQUE,
            password    TEXT    NOT NULL,
            full_name   TEXT,
            is_admin    INTEGER DEFAULT 0,
            -- Neurodiversity profile
            neuro_mode  TEXT    DEFAULT 'standard',  -- standard | asd | adhd
            font_size   TEXT    DEFAULT 'medium',     -- small | medium | large
            high_contrast INTEGER DEFAULT 0,
            simplified_view INTEGER DEFAULT 0,
            created_at  TEXT    NOT NULL,
            last_login  TEXT
        )
    """)
    # Add is_admin column to existing databases that predate this field
    try:
        conn.execute("ALTER TABLE users ADD COLUMN is_admin INTEGER DEFAULT 0")
        conn.commit()
    except Exception:
        pass  # Column already exists
    conn.execute("""
        CREATE TABLE IF NOT EXISTS sessions (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id     INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
            token       TEXT    NOT NULL UNIQUE,
            expires_at  TEXT    NOT NULL,
            created_at  TEXT    NOT NULL
        )
    """)
    conn.commit()


# ---------------------------------------------------------------------------
# User CRUD
# ---------------------------------------------------------------------------

def create_user(username, email, password, full_name=""):
    """Insert a new user; returns user dict or raises ValueError on duplicate."""
    pw_hash = generate_password_hash(password)
    now = datetime.utcnow().isoformat()
    with get_db() as conn:
        init_users_table(conn)
        try:
            cursor = conn.execute(
                """INSERT INTO users (username, email, password, full_name, created_at)
                   VALUES (?, ?, ?, ?, ?)""",
                (username.strip(), email.lower().strip(), pw_hash, full_name.strip(), now)
            )
            conn.commit()
            return get_user_by_id(cursor.lastrowid)
        except sqlite3.IntegrityError as exc:
            if "username" in str(exc):
                raise ValueError("Username already taken.")
            raise ValueError("Email already registered.")


def get_user_by_id(user_id):
    with get_db() as conn:
        init_users_table(conn)
        row = conn.execute(
            "SELECT * FROM users WHERE id = ?", (user_id,)
        ).fetchone()
        return dict(row) if row else None


def get_user_by_email(email):
    with get_db() as conn:
        init_users_table(conn)
        row = conn.execute(
            "SELECT * FROM users WHERE email = ?", (email.lower().strip(),)
        ).fetchone()
        return dict(row) if row else None


def get_user_by_username(username):
    with get_db() as conn:
        init_users_table(conn)
        row = conn.execute(
            "SELECT * FROM users WHERE username = ?", (username.strip(),)
        ).fetchone()
        return dict(row) if row else None


def verify_password(user_dict, password):
    """Return True if plain-text password matches stored hash."""
    return check_password_hash(user_dict["password"], password)


def update_user_profile(user_id, fields: dict):
    """Update allowed profile fields for a user."""
    allowed = {"full_name", "neuro_mode", "font_size", "high_contrast", "simplified_view"}
    updates = {k: v for k, v in fields.items() if k in allowed}
    if not updates:
        return
    set_clause = ", ".join(f"{k} = ?" for k in updates)
    values = list(updates.values()) + [user_id]
    with get_db() as conn:
        conn.execute(f"UPDATE users SET {set_clause} WHERE id = ?", values)
        conn.commit()


def update_last_login(user_id):
    with get_db() as conn:
        conn.execute(
            "UPDATE users SET last_login = ? WHERE id = ?",
            (datetime.utcnow().isoformat(), user_id)
        )
        conn.commit()


# ---------------------------------------------------------------------------
# Session / token management
# ---------------------------------------------------------------------------

def create_session(user_id):
    """Generate a secure session token; return token string."""
    token = secrets.token_hex(32)
    now = datetime.utcnow()
    expires = (now + timedelta(hours=cfg.JWT_EXPIRY_HOURS)).isoformat()
    with get_db() as conn:
        init_users_table(conn)
        conn.execute(
            """INSERT INTO sessions (user_id, token, expires_at, created_at)
               VALUES (?, ?, ?, ?)""",
            (user_id, token, expires, now.isoformat())
        )
        conn.commit()
    return token


def get_user_by_token(token):
    """Return user dict if token is valid and not expired, else None."""
    now = datetime.utcnow().isoformat()
    with get_db() as conn:
        init_users_table(conn)
        row = conn.execute(
            """SELECT u.* FROM users u
               JOIN sessions s ON s.user_id = u.id
               WHERE s.token = ? AND s.expires_at > ?""",
            (token, now)
        ).fetchone()
        return dict(row) if row else None


def delete_session(token):
    with get_db() as conn:
        conn.execute("DELETE FROM sessions WHERE token = ?", (token,))
        conn.commit()


def safe_user(user_dict):
    """Return user dict without the password field."""
    return {k: v for k, v in user_dict.items() if k != "password"}
