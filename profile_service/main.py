from fastapi import FastAPI
import os
from fastapi.openapi.utils import get_openapi
from routers import profile, preferences
from models.base import Base
from database import engine

app = FastAPI(
    title="Profile Service API",
    description="""
    ## Profile Service API
    
    Quản lý thông tin hồ sơ cá nhân và tùy chọn của người dùng.
    
    ### Authentication
    Tất cả endpoints yêu cầu header `X-User-Id` để xác thực người dùng.
    
    ### Endpoints
    - **Profile**: Quản lý thông tin cá nhân
    - **Preferences**: Quản lý theme và language
    """,
    version="1.0.0",
    contact={
        "name": "Credit Score Backend Team",
        "email": "support@creditscore.com",
    },
    license_info={
        "name": "MIT",
        "url": "https://opensource.org/licenses/MIT",
    },
)

@app.get("/")
def root():
    return {"status": "healthy", "service": "profile_service"}

@app.get(
    "/health",
    summary="Health Check",
    description="Kiểm tra trạng thái hoạt động của service",
    responses={
        200: {
            "description": "Service đang hoạt động bình thường",
            "content": {
                "application/json": {
                    "example": {
                        "status": "healthy",
                        "service": "profile_service",
                        "version": "1.0.0"
                    }
                }
            }
        }
    }
)
def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "profile_service", 
        "version": "1.0.0"
    }

def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    
    openapi_schema = get_openapi(
        title=app.title,
        version=app.version,
        description=app.description,
        routes=app.routes,
    )
    
    # Chỉ áp dụng security scheme ngoài DEV mode
    if os.getenv("AUTH_MODE", "kong").lower() != "dev":
        openapi_schema["components"]["securitySchemes"] = {
            "X-User-Id": {
                "type": "apiKey",
                "in": "header",
                "name": "X-User-Id",
                "description": "User ID để xác thực người dùng"
            }
        }
        for path in openapi_schema["paths"]:
            for method in openapi_schema["paths"][path]:
                if method.lower() in ["get", "post", "put", "delete"]:
                    openapi_schema["paths"][path][method]["security"] = [{"X-User-Id": []}]
    
    app.openapi_schema = openapi_schema
    return app.openapi_schema

app.openapi = custom_openapi

app.include_router(profile.router, prefix="/api/v1")
app.include_router(preferences.router, prefix="/api/v1")

Base.metadata.create_all(bind=engine)

@app.get("/api/v1/profile-health")
def profile_health():
    return {"status": "healthy", "service": "profile_service"}
