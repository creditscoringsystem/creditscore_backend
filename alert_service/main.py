from fastapi import FastAPI
import textwrap
from routers.alerts import router as alerts_router
from database import init_db


app = FastAPI(
    title="Alert Service API",
    description=textwrap.dedent("""
    Service quản lý alerts & tips theo điểm tín dụng.
    
    - GET  /alerts/{user_id}: danh sách alerts/tips
    - POST /alerts/on-score-updated: tạo alerts khi điểm thay đổi
    - POST /alerts/{alert_id}/read: đánh dấu đã đọc
    """),
    version="1.0.0",
)

app.include_router(alerts_router, prefix="/api/v1")

@app.on_event("startup")
def on_startup():
    # Khởi tạo DB với cơ chế retry
    init_db()


@app.get("/")
def root() -> dict:
    return {"status": "ok", "service": "alert_service"}


@app.get("/api/v1/alert-health")
def alert_health() -> dict:
    return {"status": "ok", "service": "alert_service"}


