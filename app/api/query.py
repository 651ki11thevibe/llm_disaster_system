# app/api/query.py

from fastapi import APIRouter, Depends, HTTPException, Query
from starlette.responses import StreamingResponse
from sqlalchemy.orm import Session
from typing import List
from io import BytesIO
import pandas as pd
from sqlalchemy.orm import joinedload
from app.models.disaster_info import DisasterInfo
from sqlalchemy import or_
from app.api.deps import get_db, require_active_user
from app.models.report import Report
from app.schemas.report_schema import ReportOut, ReportListOut

router = APIRouter()

# 查询所有报告,有参时启动关键词搜索 —— 仅已认证用户
@router.get("/", response_model= ReportListOut , dependencies=[Depends(require_active_user)])
def list_reports(
    q: str = None, 
    page: int = Query(1, ge=1), 
    page_size: int = Query(10, ge=1), 
    db: Session = Depends(get_db)
):
    query = db.query(Report).options(joinedload(Report.disaster_infos))
    
    if q:
        query = query.join(Report.disaster_infos).filter(
            or_(
                Report.summary.contains(q),
                DisasterInfo.time.contains(q),
                DisasterInfo.location.contains(q),
                DisasterInfo.event.contains(q),
                DisasterInfo.level.contains(q),
            )
        ).distinct()
    
    total = query.count()  # 总数

    reports = query.order_by(Report.id.desc())\
                   .offset((page - 1) * page_size)\
                   .limit(page_size)\
                   .all()

    return {
        "items": reports,
        "total": total
    }

#导出excel —— 仅已认证用户
@router.get("/export_excel")
def export_reports_excel(
    q: str = None,
    db: Session = Depends(get_db),
    user=Depends(require_active_user)
):
    query = db.query(Report).options(joinedload(Report.disaster_infos))

    if q:
        from sqlalchemy import or_
        from app.models.disaster_info import DisasterInfo
        query = query.join(Report.disaster_infos).filter(
            or_(
                Report.summary.contains(q),
                DisasterInfo.time.contains(q),
                DisasterInfo.location.contains(q),
                DisasterInfo.event.contains(q),
                DisasterInfo.level.contains(q),
            )
        ).distinct()

    reports = query.all()

    # 数据准备
    data = []
    for rpt in reports:
        for info in rpt.disaster_infos:
            data.append({
                "报告ID": rpt.id,
                "摘要": rpt.summary,
                "上报时间": rpt.created_at.strftime("%Y-%m-%d %H:%M:%S"),
                "时间": info.time,
                "地点": info.location,
                "灾害类型": info.event,
                "受灾程度": info.level,
                "上报次数": info.report_count,
            })

    df = pd.DataFrame(data)

    output = BytesIO()
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name="灾情报告")

    output.seek(0)
    return StreamingResponse(
        output,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": "attachment; filename=report_export.xlsx"}
    )

# （可选）查询单条报告 —— 仅已认证用户
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

