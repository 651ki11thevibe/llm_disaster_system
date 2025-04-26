# app/db/session.py
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.db.base import Base
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DB_URL", "sqlite:///./test.db")

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 用于 FastAPI 依赖注入，确保每次请求获得一个数据库会话
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# 运行一次创建所有表（可在入口调用）
def init_db():
    # 确保所有模型都被加载，才会显示在 metadata 中
    from app.models.user import User
    from app.models.report import Report
    from app.models.disaster_info import DisasterInfo
    from app.models.dedup_log import DedupLog

    Base.metadata.create_all(bind=engine)
