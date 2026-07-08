"""
utils/helpers.py — Shared utility functions
"""

from datetime import datetime, date, timedelta
from functools import wraps
from flask import request, jsonify
from models.user import get_user_by_token


def require_auth(f):
    """Decorator: validates the X-Auth-Token header and injects `current_user`."""
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get("X-Auth-Token", "")
        if not token:
            return jsonify({"error": "Authentication required."}), 401
        user = get_user_by_token(token)
        if not user:
            return jsonify({"error": "Invalid or expired session. Please log in again."}), 401
        return f(*args, current_user=user, **kwargs)
    return decorated


def success(data=None, message="OK", status=200):
    body = {"success": True, "message": message}
    if data is not None:
        body["data"] = data
    return jsonify(body), status


def error(message, status=400):
    return jsonify({"success": False, "error": message}), status


def paginate(items: list, page: int, page_size: int) -> dict:
    total = len(items)
    start = (page - 1) * page_size
    end = start + page_size
    return {
        "items": items[start:end],
        "total": total,
        "page": page,
        "page_size": page_size,
        "total_pages": max(1, (total + page_size - 1) // page_size),
    }


def iso_to_display(iso_str: str) -> str:
    """Convert an ISO datetime string to a readable format."""
    if not iso_str:
        return ""
    for fmt in ("%Y-%m-%dT%H:%M:%S", "%Y-%m-%dT%H:%M", "%Y-%m-%d"):
        try:
            dt = datetime.strptime(iso_str, fmt)
            return dt.strftime("%d %b %Y, %I:%M %p")
        except ValueError:
            continue
    return iso_str


def week_range(reference_date: str = None):
    """Return (monday_iso, sunday_iso) for the week containing reference_date."""
    if reference_date:
        ref = datetime.strptime(reference_date, "%Y-%m-%d").date()
    else:
        ref = date.today()
    monday = ref - timedelta(days=ref.weekday())
    sunday = monday + timedelta(days=6)
    return monday.isoformat(), sunday.isoformat()


def minutes_to_hm(minutes: int) -> str:
    """Convert integer minutes to '2h 30m' string."""
    h = minutes // 60
    m = minutes % 60
    if h and m:
        return f"{h}h {m}m"
    if h:
        return f"{h}h"
    return f"{m}m"
