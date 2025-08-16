from fastapi import FastAPI
from routers import survey

app = FastAPI(
    title="Survey Service API",
    description="API for managing survey questions and answers",
    version="1.0.0",
    openapi_tags=[
        {
            "name": "survey",
            "description": "Survey operations"
        }
    ]
)

# Đăng ký router cho survey_service
app.include_router(survey.router, prefix="/api/v1")

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
