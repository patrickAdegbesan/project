#!/usr/bin/env python3
"""
SentinelIQ — Flask backend.

Serves the dashboard (index.html + vendor assets) and a JSON API backed
by the trained model (model/model.pkl) and a local SQLite database of
scored transactions. Everything runs locally — no network access needed.

  POST /api/predict        score a single transaction
  POST /api/batch          generate & score a batch of transactions
  GET  /api/transactions   recent scored transactions
  GET  /api/stats          dashboard statistics (from the database)
  GET  /api/model          training metrics of the current model
  POST /api/retrain        retrain the model and reload it

Run:  python app.py   (then open http://127.0.0.1:5004)
"""

import os
import sqlite3
import threading
from datetime import datetime, timedelta, timezone

import joblib
import numpy as np
from flask import Flask, g, jsonify, request, send_from_directory

from datagen import FEATURES, generate

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "sentineliq.db")
MODEL_PATH = os.path.join(BASE_DIR, "model", "model.pkl")
METRICS_PATH = os.path.join(BASE_DIR, "model", "metrics.json")
THRESHOLD = 0.5

app = Flask(__name__, static_folder=None)

_model = None
_model_lock = threading.Lock()


def get_model():
    global _model
    with _model_lock:
        if _model is None:
            if not os.path.exists(MODEL_PATH):
                raise FileNotFoundError(
                    "model/model.pkl not found — run `python train.py` first")
            _model = joblib.load(MODEL_PATH)
        return _model


# ---------------------------------------------------------------------------
# Database
# ---------------------------------------------------------------------------

def get_db():
    if "db" not in g:
        g.db = sqlite3.connect(DB_PATH)
        g.db.row_factory = sqlite3.Row
    return g.db


@app.teardown_appcontext
def close_db(_exc):
    db = g.pop("db", None)
    if db is not None:
        db.close()


def init_db():
    with sqlite3.connect(DB_PATH) as db:
        db.execute("""
            CREATE TABLE IF NOT EXISTS transactions (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                created_at  TEXT NOT NULL,
                amount      REAL NOT NULL,
                hour        INTEGER NOT NULL,
                category    TEXT NOT NULL DEFAULT 'Manual entry',
                v1 REAL, v2 REAL, v3 REAL, v4 REAL, v14 REAL, v17 REAL,
                probability REAL NOT NULL,
                verdict     TEXT NOT NULL,
                source      TEXT NOT NULL DEFAULT 'api'
            )""")


def score_rows(X):
    """X: (n, 8) in FEATURES order -> fraud probabilities."""
    model = get_model()
    return model.predict_proba(np.asarray(X, dtype=float))[:, 1]


def verdict_for(p):
    if p >= 0.9:
        return "block"
    if p >= THRESHOLD:
        return "review"
    return "approve"


def top_factors(features_row):
    """Per-transaction factor contributions for the logistic model."""
    model = get_model()
    scaler = model.named_steps["scaler"]
    clf = model.named_steps["clf"]
    x = np.asarray(features_row, dtype=float).reshape(1, -1)
    z = (x - scaler.mean_) / scaler.scale_
    contrib = (z[0] * clf.coef_[0])
    order = np.argsort(-np.abs(contrib))
    return [{"feature": FEATURES[i],
             "value": round(float(x[0][i]), 4),
             "impact": round(float(contrib[i]), 4)}
            for i in order[:6]]


def insert_tx(db, row, prob, category, source):
    now = datetime.now(timezone.utc).isoformat()
    db.execute(
        """INSERT INTO transactions
           (created_at, amount, hour, category, v1, v2, v3, v4, v14, v17,
            probability, verdict, source)
           VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)""",
        (now, float(row[6]), int(row[7]) % 24, category,
         *[float(row[i]) for i in range(6)],
         round(float(prob), 6), verdict_for(prob), source))


# ---------------------------------------------------------------------------
# API
# ---------------------------------------------------------------------------

@app.post("/api/predict")
def api_predict():
    body = request.get_json(silent=True) or {}
    try:
        row = [float(body.get(f, 0) or 0) for f in FEATURES]
    except (TypeError, ValueError):
        return jsonify({"error": "all fields must be numeric"}), 422
    if row[6] < 0:
        return jsonify({"error": "amount must be >= 0"}), 422

    prob = float(score_rows([row])[0])
    db = get_db()
    insert_tx(db, row, prob, body.get("category", "Manual entry"), "predictor")
    db.commit()
    tx_id = db.execute("SELECT last_insert_rowid() AS id").fetchone()["id"]

    return jsonify({
        "id": tx_id,
        "probability": round(prob, 4),
        "verdict": verdict_for(prob),
        "threshold": THRESHOLD,
        "top_factors": top_factors(row),
    })


@app.post("/api/batch")
def api_batch():
    body = request.get_json(silent=True) or {}
    n = max(1, min(int(body.get("n", 200)), 5000))
    X, _y, meta = generate(n=n, fraud_rate=float(body.get("fraud_rate", 0.05)),
                           seed=body.get("seed"))
    probs = score_rows(X)

    db = get_db()
    for i in range(n):
        insert_tx(db, X[i], probs[i], str(meta["category"][i]), "batch")
    db.commit()

    rows = db.execute(
        "SELECT * FROM transactions ORDER BY id DESC LIMIT ?", (n,)).fetchall()
    out = [dict(r) for r in rows][::-1]
    flagged = sum(1 for r in out if r["verdict"] != "approve")
    return jsonify({"scored": n, "flagged": flagged, "rows": out[:200]})


@app.get("/api/transactions")
def api_transactions():
    limit = max(1, min(int(request.args.get("limit", 50)), 500))
    verdict = request.args.get("verdict")
    q = "SELECT * FROM transactions"
    params = []
    if verdict:
        q += " WHERE verdict = ?"
        params.append(verdict)
    q += " ORDER BY id DESC LIMIT ?"
    params.append(limit)
    rows = get_db().execute(q, params).fetchall()
    return jsonify({"transactions": [dict(r) for r in rows]})


@app.get("/api/stats")
def api_stats():
    db = get_db()
    total = db.execute("SELECT COUNT(*) c FROM transactions").fetchone()["c"]
    flagged = db.execute(
        "SELECT COUNT(*) c FROM transactions WHERE verdict != 'approve'"
    ).fetchone()["c"]
    blocked_amount = db.execute(
        "SELECT COALESCE(SUM(amount),0) s FROM transactions WHERE verdict='block'"
    ).fetchone()["s"]

    # last 30 days daily trend
    start = (datetime.now(timezone.utc) - timedelta(days=29)).date()
    daily = db.execute("""
        SELECT substr(created_at, 1, 10) d,
               SUM(CASE WHEN verdict != 'approve' THEN 1 ELSE 0 END) fraud,
               SUM(CASE WHEN verdict = 'approve' THEN 1 ELSE 0 END) legit
        FROM transactions WHERE substr(created_at, 1, 10) >= ?
        GROUP BY d ORDER BY d""", (start.isoformat(),)).fetchall()

    hourly = db.execute("""
        SELECT hour, COUNT(*) c FROM transactions
        WHERE verdict != 'approve' GROUP BY hour""").fetchall()
    hours = [0] * 24
    for r in hourly:
        hours[int(r["hour"]) % 24] = r["c"]

    cats = db.execute("""
        SELECT category, COUNT(*) c FROM transactions
        WHERE verdict != 'approve' GROUP BY category ORDER BY c DESC""").fetchall()

    return jsonify({
        "total_transactions": total,
        "flagged": flagged,
        "flag_rate": round(flagged / total * 100, 2) if total else 0.0,
        "blocked_amount": round(blocked_amount, 2),
        "daily": [dict(r) for r in daily],
        "hourly_fraud": hours,
        "categories": [dict(r) for r in cats],
    })


@app.get("/api/model")
def api_model():
    if not os.path.exists(METRICS_PATH):
        return jsonify({"error": "model not trained yet — run train.py"}), 404
    import json
    with open(METRICS_PATH) as f:
        return jsonify(json.load(f))


@app.post("/api/retrain")
def api_retrain():
    global _model
    from train import train as retrain
    body = request.get_json(silent=True) or {}
    metrics = retrain(n=int(body.get("n", 40000)), seed=body.get("seed", 42))
    with _model_lock:
        _model = None          # force reload on next prediction
    return jsonify(metrics)


# ---------------------------------------------------------------------------
# Frontend
# ---------------------------------------------------------------------------

@app.get("/")
def index():
    return send_from_directory(BASE_DIR, "index.html")


@app.get("/vendor/<path:name>")
def vendor(name):
    return send_from_directory(os.path.join(BASE_DIR, "vendor"), name)


@app.get("/favicon.ico")
def favicon():
    return "", 204


init_db()

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5004, debug=False)
