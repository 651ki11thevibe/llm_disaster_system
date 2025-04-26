#app/schemas/disaster_info_schema.py
from pydantic import BaseModel
from typing import Optional

# 请求时使用的更新类
class DisasterInfoUpdate(BaseModel):
    time: Optional[str]
    location: Optional[str]
    event: Optional[str]
    level: Optional[str]


# 返回给前端的完整四元组信息
class DisasterInfoOut(BaseModel):
    id: int 
    time: str
    location: str
    event: str
    level: str
    report_count: int  # 上报次数
    has_been_checked:  bool

    class Config:
        from_attributes = True