from fastapi import FastAPI
from routers.scores import router as scores_router


app = FastAPI(
    title="Score Service API",
    description=(
        "Service quản lý điểm: tính và lưu điểm hiện tại, lịch sử, và mô phỏng What-If.\n"
        "- POST /scores/{user_id}/calculate: gọi ML để tính và LƯU\n"
        "- GET  /scores/{user_id}: lấy điểm hiện tại\n"
        "- GET  /scores/{user_id}/history: lịch sử điểm\n"
        "- POST /scores/{user_id}/simulate: mô phỏng, KHÔNG lưu"
    ),
    version="1.0.0",
)


app.include_router(scores_router, prefix="/api/v1")


@app.get("/")
def root() -> dict:
    return {"status": "ok", "service": "score_service"}

@app.get("/api/v1/score-health")
def score_health() -> dict:
    return {"status": "ok", "service": "score_service"}


