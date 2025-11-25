from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import get_settings
from app.db import Base
from app.db.session import engine
from app.api.v1.endpoints import admin, admin_rules, changes, dashboard

settings = get_settings()

Base.metadata.create_all(bind=engine)

app = FastAPI(title=settings.app_name)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(admin.router, prefix="/api/v1/admin", tags=["admin"])

# ✅ 변경이력/신구법 비교용
app.include_router(changes.router, prefix="/api/v1/changes", tags=["changes"])

# ⭐ 대시보드 통합 API 추가
app.include_router(
    dashboard.router,
    prefix="/api/v1/dashboard",
    tags=["dashboard"]
)

# ⭐ 행정규칙 목록
app.include_router(admin_rules.router, prefix="/api/v1/admin-rules", tags=["admin_rules"])