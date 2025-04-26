# app/schemas/report_schema.py
from pydantic import BaseModel
from datetime import datetime
from app.schemas.disaster_info_schema import DisasterInfoOut
from typing import List

class ReportCreate(BaseModel):
    text: str  # 用户上报的长文本


class ReportOut(BaseModel):
    id: int
    text: str
    summary: str
    disaster_infos: list[DisasterInfoOut] 
    created_at: datetime

    class Config:
        from_attributes = True

class ReportListOut(BaseModel):
    items: List[ReportOut]
    total: int
    
    class Config:
        from_attributes = True