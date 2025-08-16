from fastapi import FastAPI
from routers.alerts import router as alerts_router


app = FastAPI(
    title="Alert Service API",
    description=(
        "Alerts & Tips cho Dashboard theo điểm tín dụng.\n"
        "- GET  /alerts/{user_id}: danh sách alerts/tips\n"
        "- POST /alerts/on-score-updated: tạo alerts khi điểm thay đổi\n"
        "- POST /alerts/{alert_id}/read: đánh dấu đã đọc"
    ),
    version="1.0.0",
)

app.include_router(alerts_router, prefix="/api/v1")


@app.get("/")
def root() -> dict:
    return {"status": "ok", "service": "alert_service"}


@app.get("/api/v1/alert-health")
def alert_health() -> dict:
    return {"status": "ok", "service": "alert_service"}


