# app/models/dedup_log.py
from sqlalchemy import Column, Integer, DateTime
from datetime import datetime
from app.db.base import Base

class DedupLog(Base):
    __tablename__ = "dedup_log"

    id = Column(Integer, primary_key=True, index=True)
    run_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    duplicates_detected = Column(Integer, nullable=False)
    merged_clusters = Column(Integer, nullable=False)
    deleted_records = Column(Integer, nullable=False)
