# app/api/disaster_info.py

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.models.disaster_info import DisasterInfo
from app.schemas.disaster_info_schema import DisasterInfoUpdate, DisasterInfoOut
from app.api.deps import require_admin

router = APIRouter(dependencies=[Depends(require_admin)])

@router.put("/{info_id}", response_model=DisasterInfoOut)
def update_disaster_info(info_id: int, data: DisasterInfoUpdate, db: Session = Depends(get_db)):
    info = db.get(DisasterInfo, info_id)
    if not info:
        raise HTTPException(status_code=404, detail="未找到该灾情元组")
    for field, value in data.dict(exclude_unset=True).items():
        setattr(info, field, value)
    db.commit()
    db.refresh(info)
    return info
