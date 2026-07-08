"""
routes/task_routes.py — Task CRUD + semantic search + reminders
GET    /api/tasks              — list (with optional filters)
POST   /api/tasks              — create
GET    /api/tasks/<id>         — get single
PUT    /api/tasks/<id>         — update
DELETE /api/tasks/<id>         — delete
GET    /api/tasks/search       — semantic search
GET    /api/reminders          — list reminders
POST   /api/reminders/read     — mark reminders read
GET    /api/reminders/count    — unread count
"""

from flask import Blueprint, request
from models.task import (
    create_task, get_task_by_id, get_tasks, update_task, delete_task
)
from services.semantic_search import index_task, remove_task_from_index, semantic_search
from services.reminder_service import (
    check_and_create_reminders, get_reminders,
    mark_reminders_read, get_unread_count
)
from utils.validators import validate_task_data, sanitise_string
from utils.helpers import require_auth, success, error

task_bp = Blueprint("tasks", __name__, url_prefix="/api")


# ---------------------------------------------------------------------------
# Task CRUD
# ---------------------------------------------------------------------------

@task_bp.route("/tasks", methods=["GET"])
@require_auth
def list_tasks(current_user):
    # Trigger reminder check on each authenticated list call
    check_and_create_reminders(current_user["id"])

    filters = {
        "status":     request.args.get("status"),
        "priority":   request.args.get("priority"),
        "subject":    request.args.get("subject"),
        "due_before": request.args.get("due_before"),
        "due_after":  request.args.get("due_after"),
    }
    filters = {k: v for k, v in filters.items() if v}
    tasks = get_tasks(current_user["id"], filters)
    return success({"tasks": tasks, "total": len(tasks)})


@task_bp.route("/tasks", methods=["POST"])
@require_auth
def create(current_user):
    data = request.get_json(silent=True) or {}
    ok, msg = validate_task_data(data)
    if not ok:
        return error(msg)

    task = create_task(current_user["id"], data)
    index_task(task)  # Add to semantic index
    return success({"task": task}, message="Task created.", status=201)


@task_bp.route("/tasks/<int:task_id>", methods=["GET"])
@require_auth
def get_one(task_id, current_user):
    task = get_task_by_id(task_id, current_user["id"])
    if not task:
        return error("Task not found.", 404)
    return success({"task": task})


@task_bp.route("/tasks/<int:task_id>", methods=["PUT"])
@require_auth
def update(task_id, current_user):
    task = get_task_by_id(task_id, current_user["id"])
    if not task:
        return error("Task not found.", 404)

    data = request.get_json(silent=True) or {}
    # Partial updates are allowed — only validate present fields
    ok, msg = validate_task_data({**task, **data})
    if not ok:
        return error(msg)

    updated = update_task(task_id, current_user["id"], data)
    index_task(updated)  # Re-index after update
    return success({"task": updated}, message="Task updated.")


@task_bp.route("/tasks/<int:task_id>", methods=["DELETE"])
@require_auth
def delete(task_id, current_user):
    task = get_task_by_id(task_id, current_user["id"])
    if not task:
        return error("Task not found.", 404)
    delete_task(task_id, current_user["id"])
    remove_task_from_index(task_id, current_user["id"])
    return success(message="Task deleted.")


# ---------------------------------------------------------------------------
# Semantic search
# ---------------------------------------------------------------------------

@task_bp.route("/tasks/search", methods=["GET"])
@require_auth
def search(current_user):
    query = sanitise_string(request.args.get("q", ""), 200)
    if not query:
        return error("Search query 'q' is required.")
    top_k = min(int(request.args.get("limit", 10)), 50)
    results = semantic_search(query, current_user["id"], top_k=top_k)
    return success({"results": results, "query": query})


# ---------------------------------------------------------------------------
# Reminders
# ---------------------------------------------------------------------------

@task_bp.route("/reminders", methods=["GET"])
@require_auth
def list_reminders(current_user):
    unread_only = request.args.get("unread", "false").lower() == "true"
    reminders = get_reminders(current_user["id"], unread_only=unread_only)
    return success({"reminders": reminders})


@task_bp.route("/reminders/read", methods=["POST"])
@require_auth
def mark_read(current_user):
    data = request.get_json(silent=True) or {}
    ids = data.get("ids", [])
    if not isinstance(ids, list):
        return error("'ids' must be a list of reminder IDs.")
    mark_reminders_read(current_user["id"], [int(i) for i in ids])
    return success(message="Reminders marked as read.")


@task_bp.route("/reminders/count", methods=["GET"])
@require_auth
def unread_count(current_user):
    count = get_unread_count(current_user["id"])
    return success({"unread_count": count})
