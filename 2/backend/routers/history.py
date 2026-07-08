import json
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import or_
from database import get_db
from models import URLRecord

router = APIRouter()


@router.get("/history")
def get_history(
    page:      int   = Query(1, ge=1),
    limit:     int   = Query(20, ge=1, le=100),
    cls:       str   = Query("", description="phishing|legitimate|empty=all"),
    risk_min:  int   = Query(0, ge=0, le=100),
    risk_max:  int   = Query(100, ge=0, le=100),
    search:    str   = Query(""),
    db: Session = Depends(get_db),
):
    q = db.query(URLRecord)

    if cls in ("phishing", "legitimate"):
        q = q.filter(URLRecord.classification == cls)

    if risk_min > 0:
        q = q.filter(URLRecord.risk_score >= risk_min)
    if risk_max < 100:
        q = q.filter(URLRecord.risk_score <= risk_max)

    if search:
        q = q.filter(URLRecord.url.ilike(f"%{search}%"))

    total = q.count()
    records = q.order_by(URLRecord.created_at.desc()) \
               .offset((page - 1) * limit) \
               .limit(limit) \
               .all()

    items = [
        {
            "id":             r.id,
            "url":            r.url,
            "domain":         r.domain,
            "classification": r.classification,
            "risk_score":     r.risk_score,
            "confidence":     r.confidence,
            "shap_features":  json.loads(r.shap_json),
            "created_at":     r.created_at.strftime("%Y-%m-%d %H:%M"),
        }
        for r in records
    ]

    return {
        "total":  total,
        "page":   page,
        "limit":  limit,
        "pages":  max(1, -(-total // limit)),
        "items":  items,
    }
