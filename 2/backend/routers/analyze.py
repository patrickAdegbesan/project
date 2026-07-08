import json, time
from urllib.parse import urlparse
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from database import get_db
from models import URLRecord
import predict as predictor

router = APIRouter()


class AnalyzeRequest(BaseModel):
    url: str


@router.post("/analyze")
def analyze_url(req: AnalyzeRequest, db: Session = Depends(get_db)):
    url = req.url.strip()
    if not url:
        raise HTTPException(status_code=422, detail="URL must not be empty")
    if not url.startswith(("http://", "https://")):
        url = "https://" + url

    try:
        t0 = time.time()
        result = predictor.predict(url)
        from routers.admin import record_response_time
        record_response_time(round((time.time() - t0) * 1000, 1))
    except FileNotFoundError as e:
        raise HTTPException(status_code=503, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Prediction error: {e}")

    domain = urlparse(url).hostname or ""

    record = URLRecord(
        url            = url,
        domain         = domain,
        classification = result["classification"],
        risk_score     = result["risk_score"],
        confidence     = result["confidence"],
        features_json  = json.dumps(result["features"]),
        shap_json      = json.dumps(result["shap_features"]),
    )
    db.add(record)
    db.commit()
    db.refresh(record)

    return {
        "url_id":         record.id,
        "url":            url,
        "domain":         domain,
        "classification": result["classification"],
        "risk_score":     result["risk_score"],
        "confidence":     result["confidence"],
        "features":       result["features"],
        "shap_features":  result["shap_features"],
        "created_at":     record.created_at.isoformat(),
    }
