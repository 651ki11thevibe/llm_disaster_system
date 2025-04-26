# app/api/report.py

from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from typing import List
import datetime

from app.api.deps import get_db, require_active_user, require_admin
from app.schemas.report_schema import ReportCreate, ReportOut
from app.models.report import Report
from app.core.llm_service import generate_report_info

router = APIRouter()

# 创建报告 —— 仅已认证用户
@router.post(
    "/",
    response_model=ReportOut,
    dependencies=[Depends(require_active_user)]
)
def create_report(report_in: ReportCreate, db: Session = Depends(get_db)):
    try:
        summary, disaster_infos = generate_report_info(report_in.text)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"模型推理失败: {e}")
    report = Report(
        text=report_in.text,
        summary=summary,
        created_at=datetime.datetime.utcnow(),
        disaster_infos=disaster_infos
    )
    db.add(report)
    db.commit()
    db.refresh(report)
    return report

# （可选）查看单条报告 —— 仅已认证用户
@router.get(
    "/{report_id}",
    response_model=ReportOut,
    dependencies=[Depends(require_active_user)]
)
def get_report(report_id: int, db: Session = Depends(get_db)):
    rpt = db.get(Report, report_id)
    if not rpt:
        raise HTTPException(status_code=404, detail="未找到该报告")
    return rpt

# 更新报告 —— 仅管理员
@router.put(
    "/{report_id}",
    response_model=ReportOut,
    dependencies=[Depends(require_admin)]
)
def update_report(report_id: int, data: ReportCreate, db: Session = Depends(get_db)):
    rpt = db.get(Report, report_id)
    if not rpt:
        raise HTTPException(status_code=404, detail="未找到该报告")
    # 根据需要，你也可以只更新 text，或者全文重新推理
    rpt.text = data.text
    rpt.summary, rpt.disaster_infos = generate_report_info(data.text)
    db.commit()
    db.refresh(rpt)
    return rpt

# 删除报告 —— 仅管理员
@router.delete(
    "/{report_id}",
    dependencies=[Depends(require_admin)]
)
def delete_report(report_id: int, db: Session = Depends(get_db)):
    rpt = db.get(Report, report_id)
    if not rpt:
        raise HTTPException(status_code=404, detail="未找到该报告")
    db.delete(rpt)
    db.commit()
    return {"detail": "删除成功"}
