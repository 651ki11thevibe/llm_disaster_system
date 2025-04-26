from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List
from app.schemas.dedup_log_schema import DedupLogOut

from app.api.deps import get_db, require_admin
from app.utils.full_dedup_engine import find_similar_disaster_infos
from app.utils.merge_engine import merge_duplicate_clusters
from app.models.dedup_log import DedupLog
from app.models.report import Report
from sqlalchemy import func                 # ← 让聚合函数可用
from app.models.disaster_info import DisasterInfo   # ← 用来计数


router = APIRouter()
# 去重 —— 仅管理员
@router.post("/", dependencies=[Depends(require_admin)])
def run_dedup(db: Session = Depends(get_db)):
    pairs = find_similar_disaster_infos(db)
    merged, deleted, details = merge_duplicate_clusters(db, pairs)

    # 写入去重日志
    log = DedupLog(
        duplicates_detected=len(pairs),
        merged_clusters=merged,
        deleted_records=deleted,
    )
    db.add(log)
    orphan_reports = (
        db.query(Report)
        .outerjoin(Report.disaster_infos)
        .group_by(Report.id)
        .having(func.count(DisasterInfo.id) == 0)
        .all()
    )
    for rpt in orphan_reports:
        db.delete(rpt)
        
    db.commit()

    return {
        "duplicates_detected": len(pairs),
        "merged_clusters": merged,
        "deleted_records": deleted,
        "cluster_details": details,
    }

@router.get("/logs", response_model=List[DedupLogOut], dependencies=[Depends(require_admin)])
def get_dedup_logs(db: Session = Depends(get_db)):
    return db.query(DedupLog).order_by(DedupLog.run_at.desc()).all()