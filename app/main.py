# app/main.py

import uvicorn
from fastapi import FastAPI
from dotenv import load_dotenv
from fastapi.middleware.cors import CORSMiddleware

from app.db.session import init_db
from app.api import auth, report, query, dedup, dashboard, disaster_info, user

load_dotenv()
app = FastAPI(title="灾情信息处理系统", version="1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
@app.on_event("startup")
def on_startup():
    init_db()

# 路由注册
app.include_router(auth.router, prefix="/auth", tags=["Auth"])
app.include_router(report.router, prefix="/report", tags=["Report"])
app.include_router(query.router,  prefix="/reports", tags=["Reports"])
app.include_router(dedup.router,  prefix="/dedup",   tags=["Deduplication"])
app.include_router(dashboard.router, prefix="/dashboard", tags=["Dashboard"])
app.include_router(disaster_info.router, prefix="/disaster-info", tags=["DisasterInfo"])
app.include_router(user.router, prefix="/user", tags=["user"])

if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=8080, reload=True)
