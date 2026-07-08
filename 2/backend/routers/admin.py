import os, json, time
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from database import get_db
from models import URLRecord, FeedbackRecord

router = APIRouter()

MODEL_DIR = os.path.join(os.path.dirname(__file__), "../../model")
_request_times = []   # rolling list of response times (ms), capped at 200


def record_response_time(ms: float):
    _request_times.append(ms)
    if len(_request_times) > 200:
        _request_times.pop(0)


@router.get("/admin/stats")
def admin_stats(db: Session = Depends(get_db)):
    t0 = time.time()

    total     = db.query(URLRecord).count()
    phishing  = db.query(URLRecord).filter(URLRecord.classification == "phishing").count()
    legit     = db.query(URLRecord).filter(URLRecord.classification == "legitimate").count()
    avg_risk  = db.query(func.avg(URLRecord.risk_score)).scalar() or 0
    fb_pending = db.query(FeedbackRecord).filter(FeedbackRecord.reviewed == False).count()  # noqa: E712

    # Today's activity
    today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
    today_total   = db.query(URLRecord).filter(URLRecord.created_at >= today_start).count()
    today_phishing = db.query(URLRecord).filter(
        URLRecord.classification == "phishing",
        URLRecord.created_at >= today_start,
    ).count()

    # Daily counts for last 7 days
    daily = []
    for i in range(6, -1, -1):
        day_start = today_start - timedelta(days=i)
        day_end   = day_start + timedelta(days=1)
        ph = db.query(URLRecord).filter(
            URLRecord.classification == "phishing",
            URLRecord.created_at >= day_start, URLRecord.created_at < day_end,
        ).count()
        lg = db.query(URLRecord).filter(
            URLRecord.classification == "legitimate",
            URLRecord.created_at >= day_start, URLRecord.created_at < day_end,
        ).count()
        daily.append({"date": day_start.strftime("%b %d"), "phishing": ph, "legitimate": lg})

    # Top 5 phishing domains
    top_domains = (
        db.query(URLRecord.domain, func.count(URLRecord.id).label("cnt"))
        .filter(URLRecord.classification == "phishing")
        .group_by(URLRecord.domain)
        .order_by(func.count(URLRecord.id).desc())
        .limit(5)
        .all()
    )

    avg_resp = round(sum(_request_times) / len(_request_times), 1) if _request_times else 0
    phishing_rate = round(phishing / total * 100, 1) if total > 0 else 0

    elapsed = round((time.time() - t0) * 1000, 1)
    record_response_time(elapsed)

    return {
        "total_analyzed":       total,
        "phishing_count":       phishing,
        "legitimate_count":     legit,
        "avg_risk_score":       round(float(avg_risk), 1),
        "feedback_pending":     fb_pending,
        "today_total":          today_total,
        "today_phishing":       today_phishing,
        "phishing_rate":        phishing_rate,
        "avg_response_ms":      avg_resp,
        "daily_counts":         daily,
        "top_phishing_domains": [{"domain": d, "count": c} for d, c in top_domains],
    }


@router.get("/admin/model-metrics")
def model_metrics():
    path = os.path.join(MODEL_DIR, "metrics.json")
    if not os.path.exists(path):
        return {"error": "Model not trained yet. Run: python3 train.py"}
    with open(path) as f:
        return json.load(f)
