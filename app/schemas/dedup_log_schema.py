#app/schemas/deduo_log_schema.py
from pydantic import BaseModel

class DedupLogOut(BaseModel):
    run_at: str
    duplicates_detected: int
    merged_clusters: int
    deleted_records: int

    class Config:
        from_attributes = True
