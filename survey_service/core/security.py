from fastapi import Depends, HTTPException, status, Request
import os

# Hàm lấy user từ Kong headers (Kong đã xử lý authentication)
def get_current_user(request: Request):
    user_id = request.headers.get("X-Consumer-Username")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, 
            detail="Authentication required - Kong should provide user info"
        )
    # Nếu user_id là admin_user thì role là admin
    role = "admin" if user_id == "admin_user" else "user"
    return {"user_id": user_id, "role": role}

# Hàm kiểm tra quyền admin
def require_admin(user = Depends(get_current_user)):
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
