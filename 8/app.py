"""
app.py
Flask web application for the Network Congestion Simulation System.
Provides a browser-based interface for configuring, running, and viewing
simulation results.  Simulation run history is persisted in SQLite.
"""

import base64
import io
import json
import logging
import os
import threading
from datetime import datetime

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from flask import Flask, jsonify, redirect, render_template, request, url_for
from flask_sqlalchemy import SQLAlchemy

# ---------------------------------------------------------------------------
# App / DB setup
# ---------------------------------------------------------------------------

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///simulation_results.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SECRET_KEY"] = "ncs-caleb-2025"

db = SQLAlchemy(app)

logging.basicConfig(level=logging.INFO,
                    format="%(asctime)s  %(levelname)-8s  %(message)s")
logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Database model
# ---------------------------------------------------------------------------

class SimulationRun(db.Model):
    """Stores metadata and JSON-serialised results for each simulation run."""

    id          = db.Column(db.Integer, primary_key=True)
    run_name    = db.Column(db.String(120), nullable=False)
    num_nodes   = db.Column(db.Integer, nullable=False)
    service_rate= db.Column(db.Float, nullable=False)
    buffer_size = db.Column(db.Integer, nullable=False)
    duration    = db.Column(db.Integer, nullable=False)
    num_reps    = db.Column(db.Integer, nullable=False)
    seed        = db.Column(db.Integer, nullable=False)
    load_levels = db.Column(db.String(100), nullable=False)   # JSON list
    results_json= db.Column(db.Text, nullable=True)           # JSON summary
    status      = db.Column(db.String(20), default="pending") # pending/running/done/error
    created_at  = db.Column(db.DateTime, default=datetime.utcnow)
    completed_at= db.Column(db.DateTime, nullable=True)

    def load_results(self):
        if self.results_json:
            return json.loads(self.results_json)
        return None

    def get_load_levels(self):
        return json.loads(self.load_levels)

# ---------------------------------------------------------------------------
# Background simulation runner
# ---------------------------------------------------------------------------

_run_lock = threading.Lock()

def _run_simulation_async(run_id: int):
    """Execute a simulation run in a background thread and persist results."""
    with app.app_context():
        run = SimulationRun.query.get(run_id)
        if run is None:
            return

        run.status = "running"
        db.session.commit()

        try:
            from config import SimConfig
            from experiments import run_experiments, summarise_experiments

            load_levels = tuple(run.get_load_levels())
            cfg = SimConfig(
                service_rate  = run.service_rate,
                num_nodes     = run.num_nodes,
                buffer_size   = run.buffer_size,
                duration      = run.duration,
                num_replications = run.num_reps,
                load_levels   = load_levels,
            )

            raw_df  = run_experiments(cfg, base_seed=run.seed)
            summary = summarise_experiments(raw_df)

            # Serialise to JSON-friendly list of dicts
            results = summary.to_dict(orient="records")
            run.results_json  = json.dumps(results)
            run.status        = "done"
            run.completed_at  = datetime.utcnow()
            db.session.commit()
            logger.info("Run %d completed successfully.", run_id)

        except Exception as exc:
            logger.exception("Run %d failed: %s", run_id, exc)
            run.status = "error"
            run.results_json = json.dumps({"error": str(exc)})
            db.session.commit()

# ---------------------------------------------------------------------------
# Chart generation helper
# ---------------------------------------------------------------------------

def _make_chart(summary_records: list) -> str:
    """
    Generate the 2×2 performance chart from summary records and return it
    as a base-64 encoded PNG string (for embedding directly in HTML).
    """
    loads   = [r["load"] for r in summary_records]
    x       = np.arange(len(loads))
    labels  = [f"{int(l*100)}%" for l in loads]
    colors  = ["#2196F3", "#F44336", "#4CAF50", "#FF9800"]

    fig, axes = plt.subplots(2, 2, figsize=(10, 7))
    fig.suptitle(
        "Simulation Results – Network Performance vs. Traffic Load",
        fontsize=12, fontweight="bold",
    )

    metrics = [
        ("avg_delay_mean",        "avg_delay_std",        "Average Delay (s)",       "Delay (s)"),
        ("loss_ratio_mean",       "loss_ratio_std",       "Packet Loss Ratio",        "Loss Ratio"),
        ("throughput_mean",       "throughput_std",       "Throughput (pkt/s)",       "Throughput"),
        ("avg_queue_length_mean", "avg_queue_length_std", "Avg Queue Length (pkts)", "Queue Length"),
    ]

    for ax, (mk, sk, title, ylabel), color in zip(axes.flatten(), metrics, colors):
        means = [r.get(mk, 0) for r in summary_records]
        stds  = [r.get(sk, 0) or 0 for r in summary_records]
        ax.bar(x, means, yerr=stds, capsize=5, color=color, alpha=0.82,
               edgecolor="black", linewidth=0.6,
               error_kw={"elinewidth": 1.2, "ecolor": "#333"})
        ax.set_title(title)
        ax.set_ylabel(ylabel)
        ax.set_xlabel("Traffic Load")
        ax.set_xticks(x)
        ax.set_xticklabels(labels)
        ax.grid(axis="y", linestyle="--", alpha=0.5)

    fig.tight_layout()
    buf = io.BytesIO()
    fig.savefig(buf, format="png", dpi=130, bbox_inches="tight")
    plt.close(fig)
    buf.seek(0)
    return base64.b64encode(buf.read()).decode("utf-8")

# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------

@app.route("/")
def index():
    """Home / landing page with project overview and recent runs."""
    recent_runs = (
        SimulationRun.query
        .order_by(SimulationRun.created_at.desc())
        .limit(5)
        .all()
    )
    total_runs = SimulationRun.query.count()
    done_runs  = SimulationRun.query.filter_by(status="done").count()
    return render_template(
        "index.html",
        recent_runs=recent_runs,
        total_runs=total_runs,
        done_runs=done_runs,
    )


@app.route("/simulate", methods=["GET", "POST"])
def simulate():
    """Simulation configuration form and run submission."""
    if request.method == "POST":
        try:
            load_levels = [
                float(request.form.get("load_50",  0)),
                float(request.form.get("load_80",  0)),
                float(request.form.get("load_100", 0)),
                float(request.form.get("load_120", 0)),
            ]
            load_levels = [l for l in load_levels if l > 0]
            if not load_levels:
                load_levels = [0.5, 0.8, 1.0, 1.2]

            run = SimulationRun(
                run_name    = request.form.get("run_name", "Unnamed Run"),
                num_nodes   = int(request.form.get("num_nodes", 3)),
                service_rate= float(request.form.get("service_rate", 1.0)),
                buffer_size = int(request.form.get("buffer_size", 50)),
                duration    = int(request.form.get("duration", 500)),
                num_reps    = int(request.form.get("num_reps", 5)),
                seed        = int(request.form.get("seed", 42)),
                load_levels = json.dumps(load_levels),
                status      = "pending",
            )
            db.session.add(run)
            db.session.commit()

            thread = threading.Thread(
                target=_run_simulation_async,
                args=(run.id,),
                daemon=True,
            )
            thread.start()

            return redirect(url_for("results", run_id=run.id))

        except Exception as exc:
            logger.exception("Form submission error: %s", exc)
            return render_template("simulate.html", error=str(exc))

    return render_template("simulate.html")


@app.route("/results/<int:run_id>")
def results(run_id: int):
    """Results page for a specific simulation run."""
    run = SimulationRun.query.get_or_404(run_id)
    chart_b64 = None
    summary_records = None

    if run.status == "done":
        summary_records = run.load_results()
        if summary_records and not isinstance(summary_records, dict):
            chart_b64 = _make_chart(summary_records)

    return render_template(
        "results.html",
        run=run,
        chart_b64=chart_b64,
        summary_records=summary_records,
    )


@app.route("/api/run_status/<int:run_id>")
def run_status(run_id: int):
    """JSON endpoint polled by the results page while a run is in progress."""
    run = SimulationRun.query.get_or_404(run_id)
    return jsonify({"status": run.status, "run_id": run_id})


@app.route("/history")
def history():
    """All past simulation runs."""
    runs = SimulationRun.query.order_by(SimulationRun.created_at.desc()).all()
    return render_template("history.html", runs=runs)


@app.route("/about")
def about():
    """About / project information page."""
    return render_template("about.html")


@app.route("/admin")
def admin():
    """Admin dashboard with aggregate statistics."""
    total   = SimulationRun.query.count()
    done    = SimulationRun.query.filter_by(status="done").count()
    running = SimulationRun.query.filter_by(status="running").count()
    error   = SimulationRun.query.filter_by(status="error").count()
    recent  = SimulationRun.query.order_by(SimulationRun.created_at.desc()).limit(10).all()
    return render_template(
        "admin.html",
        total=total, done=done, running=running, error=error,
        recent=recent,
    )


@app.route("/admin/delete/<int:run_id>", methods=["POST"])
def delete_run(run_id: int):
    """Delete a simulation run record."""
    run = SimulationRun.query.get_or_404(run_id)
    db.session.delete(run)
    db.session.commit()
    return redirect(url_for("admin"))


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True, host="0.0.0.0", port=5000)
