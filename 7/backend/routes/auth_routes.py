"""
routes/auth_routes.py — Authentication endpoints
POST /api/auth/register
POST /api/auth/login
POST /api/auth/logout
GET  /api/auth/me
PUT  /api/auth/profile
"""

from flask import Blueprint, request
from models.user import (
    create_user, get_user_by_email, verify_password,
    create_session, delete_session, update_user_profile,
    update_last_login, safe_user
)
from utils.validators import (
    validate_email, validate_password, validate_username, sanitise_string
)
from utils.helpers import require_auth, success, error

auth_bp = Blueprint("auth", __name__, url_prefix="/api/auth")


@auth_bp.route("/register", methods=["POST"])
def register():
    data = request.get_json(silent=True) or {}

    username  = sanitise_string(data.get("username", ""), 30)
    email     = sanitise_string(data.get("email", ""), 100)
    password  = data.get("password", "")
    full_name = sanitise_string(data.get("full_name", ""), 100)

    # Validation
    ok, msg = validate_username(username)
    if not ok:
        return error(msg)
    if not validate_email(email):
        return error("Please provide a valid email address.")
    ok, msg = validate_password(password)
    if not ok:
        return error(msg)

    try:
        user = create_user(username, email, password, full_name)
    except ValueError as exc:
        return error(str(exc))

    token = create_session(user["id"])
    return success(
        {"user": safe_user(user), "token": token},
        message="Account created successfully.",
        status=201
    )


@auth_bp.route("/login", methods=["POST"])
def login():
    data = request.get_json(silent=True) or {}
    email    = sanitise_string(data.get("email", ""), 100)
    password = data.get("password", "")

    if not email or not password:
        return error("Email and password are required.")

    user = get_user_by_email(email)
    if not user or not verify_password(user, password):
        return error("Invalid email or password.", 401)

    update_last_login(user["id"])
    token = create_session(user["id"])
    return success(
        {"user": safe_user(user), "token": token},
        message="Logged in successfully."
    )


@auth_bp.route("/logout", methods=["POST"])
@require_auth
def logout(current_user):
    token = request.headers.get("X-Auth-Token", "")
    delete_session(token)
    return success(message="Logged out successfully.")


@auth_bp.route("/me", methods=["GET"])
@require_auth
def me(current_user):
    return success({"user": safe_user(current_user)})


@auth_bp.route("/profile", methods=["PUT"])
@require_auth
def update_profile(current_user):
    data = request.get_json(silent=True) or {}
    allowed_fields = {"full_name", "neuro_mode", "font_size", "high_contrast", "simplified_view"}

    # Validate neuro_mode
    from utils.validators import VALID_NEURO_MODES
    if "neuro_mode" in data and data["neuro_mode"] not in VALID_NEURO_MODES:
        return error(f"neuro_mode must be one of: {', '.join(VALID_NEURO_MODES)}.")

    # Validate font_size
    if "font_size" in data and data["font_size"] not in {"small", "medium", "large"}:
        return error("font_size must be 'small', 'medium', or 'large'.")

    updates = {k: v for k, v in data.items() if k in allowed_fields}
    update_user_profile(current_user["id"], updates)

    # Re-fetch updated user
    from models.user import get_user_by_id
    updated = get_user_by_id(current_user["id"])
    return success({"user": safe_user(updated)}, message="Profile updated.")
