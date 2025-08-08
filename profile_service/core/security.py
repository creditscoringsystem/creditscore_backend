from fastapi import Request, HTTPException, status
import os

AUTH_MODE = os.getenv("AUTH_MODE", "kong").lower()

def get_current_user(request: Request):
    if AUTH_MODE == "dev":
        return {"user_id": request.headers.get("X-Dev-User", "dev_user")}
    user_id = request.headers.get("X-User-Id")
    if not user_id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing user identity (X-User-Id header)")
    return {"user_id": user_id}