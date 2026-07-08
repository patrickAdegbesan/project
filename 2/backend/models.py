from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, Text, ForeignKey
from database import Base


class URLRecord(Base):
    __tablename__ = "url_records"

    id             = Column(Integer, primary_key=True, index=True)
    url            = Column(Text, nullable=False)
    domain         = Column(String(255), index=True)
    classification = Column(String(20), nullable=False)   # "phishing" | "legitimate"
    risk_score     = Column(Integer, nullable=False)       # 0–100
    confidence     = Column(Float, nullable=False)         # 0–100
    features_json  = Column(Text, nullable=False)          # JSON blob
    shap_json      = Column(Text, nullable=False)          # JSON blob (top-5)
    created_at     = Column(DateTime, default=datetime.utcnow)


class FeedbackRecord(Base):
    __tablename__ = "feedback_records"

    id         = Column(Integer, primary_key=True, index=True)
    url_id     = Column(Integer, ForeignKey("url_records.id"), nullable=False)
    url        = Column(Text, nullable=False)
    fb_type    = Column(String(10), nullable=False)        # "fp" | "fn"
    comment    = Column(Text, default="")
    reviewed   = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
