from fastapi import FastAPI
import textwrap
from routers import survey
from database import init_db

app = FastAPI(
    title="Survey Service API",
    description=textwrap.dedent("""
    Service quản lý khảo sát: câu hỏi và câu trả lời phục vụ tính điểm tín dụng.
    
    - GET  /survey/questions: danh sách câu hỏi
    - POST /survey/submit: nộp câu trả lời
    - GET  /survey/answers/{user_id}: câu trả lời theo user
    - POST /survey/admin/import-questions: import bộ câu hỏi (admin)
    """),
    version="1.0.0",
    openapi_tags=[
        {
            "name": "survey",
            "description": "Các thao tác với khảo sát"
        }
    ]
)

# Đăng ký router cho survey_service
app.include_router(survey.router, prefix="/api/v1")

@app.on_event("startup")
def on_startup():
    init_db()

@app.get("/")
def root():
    return {"status": "ok", "service": "survey_service"}

@app.get("/health")
def health():
    return {"status": "ok", "service": "survey_service"}

@app.get("/api/v1/survey-health")
def survey_health():
    return {"status": "ok", "service": "survey_service"}

# Hướng dẫn chạy thử:
# 1. Chạy: uvicorn survey_service.main:app --reload
# 2. Truy cập docs: http://localhost:8000/docs
# 3. Click nút "Authorize" ở góc trên bên phải để nhập JWT token
