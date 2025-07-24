from fastapi import FastAPI
from fastapi.security import HTTPBearer
from routers import survey

# Thêm security scheme cho JWT Bearer token
security = HTTPBearer()

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
app.include_router(survey.router)

# Hướng dẫn chạy thử:
# 1. Chạy: uvicorn survey_service.main:app --reload
# 2. Truy cập docs: http://localhost:8000/docs
# 3. Click nút "Authorize" ở góc trên bên phải để nhập JWT token
