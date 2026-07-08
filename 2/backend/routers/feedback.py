from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from database import get_db
from models import FeedbackRecord, URLRecord

router = APIRouter()


class FeedbackRequest(BaseModel):
    url_id:  int
    fb_type: str    # "fp" | "fn"
    comment: str = ""


@router.post("/feedback")
def submit_feedback(req: FeedbackRequest, db: Session = Depends(get_db)):
    if req.fb_type not in ("fp", "fn"):
        raise HTTPException(status_code=422, detail="fb_type must be 'fp' or 'fn'")

    record = db.query(URLRecord).filter(URLRecord.id == req.url_id).first()
    if not record:
        raise HTTPException(status_code=404, detail="URL record not found")

    fb = FeedbackRecord(
        url_id  = req.url_id,
        url     = record.url,
        fb_type = req.fb_type,
        comment = req.comment,
    )
    db.add(fb)
    db.commit()
    return {"status": "ok", "message": "Feedback submitted — thank you!"}


@router.get("/feedback")
def list_feedback(reviewed: bool = False, db: Session = Depends(get_db)):
    items = (
        db.query(FeedbackRecord)
        .filter(FeedbackRecord.reviewed == reviewed)
        .order_by(FeedbackRecord.created_at.desc())
        .limit(50)
        .all()
    )
    return [
        {
            "id":       f.id,
            "url_id":   f.url_id,
            "url":      f.url,
            "fb_type":  f.fb_type,
            "comment":  f.comment,
            "reviewed": f.reviewed,
            "created_at": f.created_at.strftime("%Y-%m-%d %H:%M"),
        }
        for f in items
    ]


@router.patch("/feedback/{fb_id}/review")
def mark_reviewed(fb_id: int, db: Session = Depends(get_db)):
    fb = db.query(FeedbackRecord).filter(FeedbackRecord.id == fb_id).first()
    if not fb:
        raise HTTPException(status_code=404, detail="Feedback not found")
    fb.reviewed = True
    db.commit()
    return {"status": "ok"}
