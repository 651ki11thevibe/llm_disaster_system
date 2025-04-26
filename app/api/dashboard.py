# app/api/dashboard.py

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime, date, timedelta
from typing import List, Dict

from app.api.deps import get_db, require_active_user
from app.models.report import Report
from app.models.dedup_log import DedupLog

router = APIRouter(tags=["Dashboard"])

@router.get("/metrics")
def get_metrics(db: Session = Depends(get_db), user=Depends(require_active_user)):
    # 1. 总报告数
    total_reports = db.query(func.count(Report.id)).scalar()

    # 2. 今日上报数
    today = date.today()
    today_start = datetime(today.year, today.month, today.day)
    today_reports = db.query(func.count(Report.id)).filter(Report.created_at >= today_start).scalar()

    # 3. 上次去重结果
    last_log = (
        db.query(DedupLog)
          .order_by(DedupLog.run_at.desc())
          .first()
    )
    last_dedup = None
    if last_log:
        last_dedup = {
            "run_at": last_log.run_at.isoformat(),
            "duplicates_detected": last_log.duplicates_detected,
            "merged_clusters": last_log.merged_clusters,
            "deleted_records": last_log.deleted_records,
        }

    # 4. 待去重数 = 自上次去重以来的新报告数
    if last_log:
        pending_dedup = db.query(func.count(Report.id))\
            .filter(Report.created_at > last_log.run_at)\
            .scalar()
    else:
        pending_dedup = total_reports

    # 5. 最近 7 天上报趋势
    trend: List[Dict[str, int]] = []
    for i in range(6, -1, -1):  # 6 天前 到 今天
        d = today - timedelta(days=i)
        start = datetime(d.year, d.month, d.day)
        end = start + timedelta(days=1)
        cnt = db.query(func.count(Report.id)).filter(
            Report.created_at >= start,
            Report.created_at < end
        ).scalar()
        trend.append({"date": d.isoformat(), "count": cnt})

    return {
        "total_reports": total_reports,
        "today_reports": today_reports,
        "pending_dedup": pending_dedup,
        "last_dedup": last_dedup,
        "report_trend": trend,
    }
