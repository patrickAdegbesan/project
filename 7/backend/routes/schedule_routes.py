"""
routes/schedule_routes.py — Study schedule endpoints
GET    /api/schedule           — get blocks for a week
POST   /api/schedule           — create block
PUT    /api/schedule/<id>      — update block
DELETE /api/schedule/<id>      — delete block
GET    /api/schedule/today     — today's blocks
POST   /api/progress/log       — log a study session
GET    /api/progress/logs      — get study logs
GET    /api/goals              — list goals
POST   /api/goals              — create goal
PUT    /api/goals/<id>         — update goal
DELETE /api/goals/<id>         — delete goal
"""

from flask import Blueprint, request
from models.schedule import (
    create_block, get_block_by_id, get_blocks_by_week,
    get_blocks_by_date_range, update_block, delete_block
)
from models.progress import (
    log_study_session, get_study_logs,
    create_goal, get_goal_by_id, get_goals, update_goal, delete_goal
)
from utils.validators import validate_block_data, sanitise_string
from utils.helpers import require_auth, success, error, week_range
from datetime import date

schedule_bp = Blueprint("schedule", __name__, url_prefix="/api")


# ---------------------------------------------------------------------------
# Schedule blocks
# ---------------------------------------------------------------------------

@schedule_bp.route("/schedule", methods=["GET"])
@require_auth
def list_schedule(current_user):
    week_start = request.args.get("week")
    if not week_start:
        week_start, _ = week_range()
    blocks = get_blocks_by_week(current_user["id"], week_start)
    return success({"blocks": blocks, "week_start": week_start})


@schedule_bp.route("/schedule/today", methods=["GET"])
@require_auth
def today_schedule(current_user):
    today = date.today().isoformat()
    blocks = get_blocks_by_date_range(current_user["id"], today, today)
    return success({"blocks": blocks, "date": today})


@schedule_bp.route("/schedule", methods=["POST"])
@require_auth
def create(current_user):
    data = request.get_json(silent=True) or {}
    ok, msg = validate_block_data(data)
    if not ok:
        return error(msg)
    block = create_block(current_user["id"], data)
    return success({"block": block}, message="Schedule block created.", status=201)


@schedule_bp.route("/schedule/<int:block_id>", methods=["PUT"])
@require_auth
def update(block_id, current_user):
    block = get_block_by_id(block_id, current_user["id"])
    if not block:
        return error("Schedule block not found.", 404)
    data = request.get_json(silent=True) or {}
    updated = update_block(block_id, current_user["id"], data)
    return success({"block": updated}, message="Block updated.")


@schedule_bp.route("/schedule/<int:block_id>", methods=["DELETE"])
@require_auth
def delete(block_id, current_user):
    block = get_block_by_id(block_id, current_user["id"])
    if not block:
        return error("Schedule block not found.", 404)
    delete_block(block_id, current_user["id"])
    return success(message="Block deleted.")


# ---------------------------------------------------------------------------
# Study session logging
# ---------------------------------------------------------------------------

@schedule_bp.route("/progress/log", methods=["POST"])
@require_auth
def log_session(current_user):
    data = request.get_json(silent=True) or {}
    minutes = data.get("minutes")
    if not minutes or not isinstance(minutes, int) or minutes < 1:
        return error("'minutes' must be a positive integer.")

    log_id = log_study_session(
        user_id=current_user["id"],
        minutes=minutes,
        subject=sanitise_string(data.get("subject", ""), 100),
        task_id=data.get("task_id"),
        note=sanitise_string(data.get("note", ""), 500),
        log_date=data.get("log_date"),
    )
    return success({"log_id": log_id}, message="Study session logged.", status=201)


@schedule_bp.route("/progress/logs", methods=["GET"])
@require_auth
def get_logs(current_user):
    logs = get_study_logs(
        current_user["id"],
        start_date=request.args.get("start"),
        end_date=request.args.get("end"),
    )
    return success({"logs": logs})


# ---------------------------------------------------------------------------
# Goals
# ---------------------------------------------------------------------------

@schedule_bp.route("/goals", methods=["GET"])
@require_auth
def list_goals(current_user):
    status = request.args.get("status")
    goals = get_goals(current_user["id"], status=status)
    return success({"goals": goals})


@schedule_bp.route("/goals", methods=["POST"])
@require_auth
def create_g(current_user):
    data = request.get_json(silent=True) or {}
    if not data.get("title", "").strip():
        return error("Goal title is required.")
    goal = create_goal(current_user["id"], data)
    return success({"goal": goal}, message="Goal created.", status=201)


@schedule_bp.route("/goals/<int:goal_id>", methods=["PUT"])
@require_auth
def update_g(goal_id, current_user):
    goal = get_goal_by_id(goal_id, current_user["id"])
    if not goal:
        return error("Goal not found.", 404)
    data = request.get_json(silent=True) or {}
    updated = update_goal(goal_id, current_user["id"], data)
    return success({"goal": updated}, message="Goal updated.")


@schedule_bp.route("/goals/<int:goal_id>", methods=["DELETE"])
@require_auth
def delete_g(goal_id, current_user):
    goal = get_goal_by_id(goal_id, current_user["id"])
    if not goal:
        return error("Goal not found.", 404)
    delete_goal(goal_id, current_user["id"])
    return success(message="Goal deleted.")
