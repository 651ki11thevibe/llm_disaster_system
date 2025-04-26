# app/models/report.py
from app.db.base import Base
from sqlalchemy import Column, Integer, String, DateTime, Text
from sqlalchemy.orm import relationship 


class Report(Base):
    __tablename__ = "reports"

    id = Column(Integer, primary_key=True, index=True)
    text = Column(Text, nullable=False)       # 用户原始上报文本
    summary = Column(Text, nullable=False)    # 模型生成的摘要
    created_at = Column(DateTime, nullable=False)

    # 关系字段：四元组
    disaster_infos = relationship(
        "DisasterInfo",
        back_populates="report",
        cascade="all, delete",
    )