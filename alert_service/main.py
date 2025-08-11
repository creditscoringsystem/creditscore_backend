from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
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

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(alerts_router)


@app.get("/health")
def health() -> dict:
    return {"status": "ok", "service": "alert_service"}


