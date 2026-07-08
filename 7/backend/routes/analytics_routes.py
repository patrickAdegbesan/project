"""
routes/analytics_routes.py — Dashboard analytics and adaptive recommendations
GET /api/analytics/dashboard    — full dashboard stats
GET /api/analytics/recommendations — adaptive engine output
POST /api/analytics/reindex     — rebuild semantic index for user
"""

from flask import Blueprint
from services.analytics_service import get_dashboard_stats
from services.adaptive_engine import generate_recommendations
from services.semantic_search import reindex_all_tasks
from utils.helpers import require_auth, success, error

analytics_bp = Blueprint("analytics", __name__, url_prefix="/api/analytics")


@analytics_bp.route("/dashboard", methods=["GET"])
@require_auth
def dashboard(current_user):
    stats = get_dashboard_stats(current_user["id"])
    return success({"stats": stats})


@analytics_bp.route("/recommendations", methods=["GET"])
@require_auth
def recommendations(current_user):
    recs = generate_recommendations(current_user["id"])
    return success({"recommendations": recs})


@analytics_bp.route("/reindex", methods=["POST"])
@require_auth
def reindex(current_user):
    """Rebuild the semantic search index for the current user's tasks."""
    try:
        reindex_all_tasks(current_user["id"])
        return success(message="Semantic index rebuilt successfully.")
    except Exception as exc:
        return error(f"Reindex failed: {str(exc)}", 500)
