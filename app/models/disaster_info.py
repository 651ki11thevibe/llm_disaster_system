#app/models/disaster_info.py
from app.db.base import Base
from sqlalchemy import Column, Integer, String, ForeignKey, Boolean
from sqlalchemy.orm import relationship

class DisasterInfo(Base):
    __tablename__ = "disaster_infos"

    id = Column(Integer, primary_key=True, index=True)
    report_id = Column(Integer, ForeignKey("reports.id", ondelete="CASCADE"))

    time = Column(String(64))
    location = Column(String(128))
    event = Column(String(64))
    level = Column(String(128))

    report_count = Column(Integer, default=1)        # 上报次数（用于展示）
    has_been_checked = Column(Boolean, default=False) # 是否已被参与过比对

    report = relationship("Report", back_populates="disaster_infos")
