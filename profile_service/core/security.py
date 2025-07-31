from fastapi import Request, HTTPException, status

def get_current_user(request: Request):
    user_id = request.headers.get("X-User-Id")
    if not user_id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing user identity (X-User-Id header)")
    return {"user_id": user_id} 