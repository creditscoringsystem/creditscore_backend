from fastapi import Depends, HTTPException, status, Request
from jose import jwt, JWTError
import os

# Chế độ xác thực:
# - kong: lấy từ header do Kong set (X-Consumer-Username / X-User-Id)
# - jwt: decode trực tiếp Authorization: Bearer <token>
# - dev: cho phép bypass với header X-Dev-User (chỉ dùng local/dev)
AUTH_MODE = os.getenv("AUTH_MODE", "dev").lower()
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM", "HS256")

def get_current_user(request: Request):
    if AUTH_MODE == "kong":
        user_id = request.headers.get("X-Consumer-Username") or request.headers.get("X-User-Id")
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Authentication required - provided by Kong",
            )
        role = "admin" if user_id == "admin_user" else "user"
        return {"user_id": user_id, "role": role}

    if AUTH_MODE == "jwt":
        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.lower().startswith("bearer "):
            raise HTTPException(status_code=401, detail="Missing Bearer token")
        token = auth_header.split(" ", 1)[1]
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        except JWTError:
            raise HTTPException(status_code=401, detail="Invalid token")
        user_id = payload.get("user_id") or payload.get("sub")
        if not user_id:
            raise HTTPException(status_code=401, detail="Invalid token payload")
        role = payload.get("role", "user")
        return {"user_id": user_id, "role": role}

    # DEV mode
    dev_user = request.headers.get("X-Dev-User", "dev_user")
    role = "admin" if dev_user == "admin_user" else "user"
    return {"user_id": dev_user, "role": role}

# Hàm kiểm tra quyền admin
def require_admin(user = Depends(get_current_user)):
    # Bypass admin check trong DEV mode cho mục đích thử nghiệm Swagger
    if AUTH_MODE == "dev":
        return {"user_id": "admin_user", "role": "admin"}
    if user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Admin privileges required")
    return user

# Hàm lấy API key từ Kong (nếu dùng key-auth plugin)
def get_api_key(request: Request):
    api_key = request.headers.get("X-API-Key")
    if not api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="API Key required"
        )
    return api_key
