from fastapi import FastAPI
from fastapi.openapi.utils import get_openapi
from routers import profile, security, preferences, consent
from models.base import Base
from database import engine

app = FastAPI(
    title="Profile Service API",
    description="""
    ## Profile Service API
    
    Quản lý thông tin hồ sơ cá nhân, bảo mật, tùy chọn và đồng ý của người dùng.
    
    ### Authentication
    Tất cả endpoints yêu cầu header `X-User-Id` để xác thực người dùng.
    
    ### Endpoints
    - **Profile**: Quản lý thông tin cá nhân
    - **Security**: Quản lý bảo mật và thiết bị
    - **Preferences**: Quản lý tùy chọn người dùng
    - **Consent**: Quản lý đồng ý và quyền riêng tư
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

def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    
    openapi_schema = get_openapi(
        title=app.title,
        version=app.version,
        description=app.description,
        routes=app.routes,
    )
    
    # Thêm security scheme cho X-User-Id header
    openapi_schema["components"]["securitySchemes"] = {
        "X-User-Id": {
            "type": "apiKey",
            "in": "header",
            "name": "X-User-Id",
            "description": "User ID để xác thực người dùng"
        }
    }
    
    # Áp dụng security cho tất cả endpoints
    for path in openapi_schema["paths"]:
        for method in openapi_schema["paths"][path]:
            if method.lower() in ["get", "post", "put", "delete"]:
                openapi_schema["paths"][path][method]["security"] = [{"X-User-Id": []}]
    
    app.openapi_schema = openapi_schema
    return app.openapi_schema

app.openapi = custom_openapi

app.include_router(profile.router)
app.include_router(security.router)
app.include_router(preferences.router)
app.include_router(consent.router)

Base.metadata.create_all(bind=engine)
