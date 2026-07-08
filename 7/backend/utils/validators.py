"""
utils/validators.py — Input validation helpers
"""

import re
from datetime import datetime


def validate_email(email: str) -> bool:
    pattern = r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"
    return bool(re.match(pattern, email))


def validate_password(password: str) -> tuple[bool, str]:
    """Return (ok, message). Password must be 8+ chars with digit and letter."""
    if len(password) < 8:
        return False, "Password must be at least 8 characters."
    if not re.search(r"[A-Za-z]", password):
        return False, "Password must contain at least one letter."
    if not re.search(r"\d", password):
        return False, "Password must contain at least one digit."
    return True, ""


def validate_username(username: str) -> tuple[bool, str]:
    if len(username) < 3:
        return False, "Username must be at least 3 characters."
    if len(username) > 30:
        return False, "Username must be at most 30 characters."
    if not re.match(r"^[a-zA-Z0-9_-]+$", username):
        return False, "Username may only contain letters, digits, hyphens, and underscores."
    return True, ""


def validate_date_string(date_str: str) -> bool:
    """Validate ISO 8601 date or datetime string."""
    for fmt in ("%Y-%m-%d", "%Y-%m-%dT%H:%M:%S", "%Y-%m-%dT%H:%M"):
        try:
            datetime.strptime(date_str, fmt)
            return True
        except ValueError:
            continue
    return False


def validate_time_string(time_str: str) -> bool:
    """Validate HH:MM time string."""
    try:
        datetime.strptime(time_str, "%H:%M")
        return True
    except ValueError:
        return False


def sanitise_string(value: str, max_length=500) -> str:
    """Strip whitespace and truncate to max_length."""
    return str(value).strip()[:max_length]


VALID_PRIORITIES = {"low", "medium", "high", "urgent"}
VALID_STATUSES   = {"pending", "in_progress", "completed", "cancelled"}
VALID_BLOCK_TYPES = {"study", "break", "review", "exam"}
VALID_NEURO_MODES = {"standard", "asd", "adhd"}


def validate_task_data(data: dict) -> tuple[bool, str]:
    if not data.get("title", "").strip():
        return False, "Task title is required."
    if "priority" in data and data["priority"] not in VALID_PRIORITIES:
        return False, f"Priority must be one of: {', '.join(VALID_PRIORITIES)}."
    if "status" in data and data["status"] not in VALID_STATUSES:
        return False, f"Status must be one of: {', '.join(VALID_STATUSES)}."
    if "due_date" in data and data["due_date"]:
        if not validate_date_string(data["due_date"]):
            return False, "due_date must be ISO format (YYYY-MM-DD or YYYY-MM-DDTHH:MM)."
    if "estimated_minutes" in data:
        try:
            mins = int(data["estimated_minutes"])
            if mins < 1 or mins > 1440:
                return False, "estimated_minutes must be between 1 and 1440."
        except (ValueError, TypeError):
            return False, "estimated_minutes must be an integer."
    return True, ""


def validate_block_data(data: dict) -> tuple[bool, str]:
    if not data.get("title", "").strip():
        return False, "Block title is required."
    if not data.get("block_date"):
        return False, "block_date is required."
    if not validate_date_string(data["block_date"]):
        return False, "block_date must be YYYY-MM-DD."
    for field in ("start_time", "end_time"):
        if data.get(field) and not validate_time_string(data[field]):
            return False, f"{field} must be HH:MM."
    if "block_type" in data and data["block_type"] not in VALID_BLOCK_TYPES:
        return False, f"block_type must be one of: {', '.join(VALID_BLOCK_TYPES)}."
    return True, ""
