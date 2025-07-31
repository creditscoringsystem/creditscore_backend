from fastapi import FastAPI
from routers import users, admin, auth
from fastapi.openapi.utils import get_openapi

app = FastAPI(
    title="User Service API",
    description="""
    ## User Service API
    
    Quản lý authentication và core user data.
    
    ### Authentication
    Sử dụng Bearer token cho các protected endpoints.
    
    ### Endpoints
    - **Auth**: Đăng ký, đăng nhập, quản lý password
    - **Users**: Quản lý thông tin user hiện tại
    - **Admin**: Quản lý tất cả users (admin only)
    
    ### Workflow
    1. **Signup** → Tạo tài khoản mới
    2. **Login** → Lấy access token
    3. **Use token** → Truy cập protected endpoints
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
    
    # Thêm security scheme cho Bearer token
    openapi_schema["components"]["securitySchemes"] = {
        "BearerAuth": {
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "JWT",
            "description": "JWT token từ login endpoint"
        }
    }
    
    # Áp dụng security cho protected endpoints
    for path in openapi_schema["paths"]:
        for method in openapi_schema["paths"][path]:
            if method.lower() in ["get", "post", "put", "delete"]:
                # Loại trừ auth endpoints khỏi security requirement
                if not path.startswith("/auth/"):
                    openapi_schema["paths"][path][method]["security"] = [{"BearerAuth": []}]
    
    app.openapi_schema = openapi_schema
    return app.openapi_schema

app.openapi = custom_openapi

app.include_router(auth.router, tags=["auth"])
app.include_router(users.router, tags=["users"])
app.include_router(admin.router, tags=["admin"])

@app.get("/ping")
async def ping():
    """
    Health check endpoint.
    
    **Trả về:**
    - Status message để kiểm tra service hoạt động
    """
    return {"msg": "pong", "service": "user-service"}