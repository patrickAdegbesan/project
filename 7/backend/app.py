"""
app.py — Flask application entry point
Student Study Planner and Time Management System

Author      : Nwachukwu Chibuzor Benjamin
Matric No.  : 22/9799
Department  : Computer Science, Caleb University, Lagos
"""

import os
import sys

# Allow imports from the backend directory itself
sys.path.insert(0, os.path.dirname(__file__))

from flask import Flask, jsonify
from flask_cors import CORS
from config import active_config as cfg

# Blueprints
from routes.auth_routes      import auth_bp
from routes.task_routes      import task_bp
from routes.schedule_routes  import schedule_bp
from routes.analytics_routes import analytics_bp
from routes.admin_routes     import admin_bp

# Initialise database tables on first run
from models.user     import get_db, init_users_table
from models.task     import init_tasks_table
from models.schedule import init_schedule_table
from models.progress import init_progress_tables
from services.reminder_service import init_reminders_table


def create_app():
    app = Flask(__name__)
    app.config.from_object(cfg)

    # ------------------------------------------------------------------
    # CORS — allow the frontend served from any local origin
    # ------------------------------------------------------------------
    CORS(
        app,
        resources={r"/api/*": {"origins": cfg.CORS_ORIGINS}},
        supports_credentials=True,
    )

    # ------------------------------------------------------------------
    # Register blueprints
    # ------------------------------------------------------------------
    app.register_blueprint(auth_bp)
    app.register_blueprint(task_bp)
    app.register_blueprint(schedule_bp)
    app.register_blueprint(analytics_bp)
    app.register_blueprint(admin_bp)

    # ------------------------------------------------------------------
    # Initialise all database tables
    # ------------------------------------------------------------------
    os.makedirs(os.path.dirname(cfg.DB_PATH), exist_ok=True)
    with get_db() as conn:
        init_users_table(conn)
        init_tasks_table(conn)
        init_schedule_table(conn)
        init_progress_tables(conn)
        init_reminders_table(conn)

    # ------------------------------------------------------------------
    # Global error handlers
    # ------------------------------------------------------------------
    @app.errorhandler(404)
    def not_found(e):
        return jsonify({"success": False, "error": "Endpoint not found."}), 404

    @app.errorhandler(405)
    def method_not_allowed(e):
        return jsonify({"success": False, "error": "Method not allowed."}), 405

    @app.errorhandler(500)
    def internal_error(e):
        return jsonify({"success": False, "error": "An internal server error occurred."}), 500

    # ------------------------------------------------------------------
    # Health-check
    # ------------------------------------------------------------------
    @app.route("/api/health", methods=["GET"])
    def health():
        return jsonify({"status": "ok", "project": "Study Planner API"})

    return app


if __name__ == "__main__":
    application = create_app()
    port = int(os.environ.get("PORT", 5000))
    application.run(host="0.0.0.0", port=port, debug=cfg.DEBUG)
