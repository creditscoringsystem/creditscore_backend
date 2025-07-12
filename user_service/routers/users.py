from fastapi import APIRouter, Depends, Request, HTTPException
from sqlalchemy.orm import Session
from schemas.user import UserOut, UserCreate
from crud.crud import get_user_by_username, create_user
from database import get_db
import httpx

router = APIRouter()

AUTH_SERVICE_URL = "http://localhost:8001/auth/verify-token"  # Sửa lại đúng port nếu cần

async def get_current_user(request: Request):
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Not authenticated")
    token = auth_header.split(" ")[1]
    async with httpx.AsyncClient() as client:
        resp = await client.post(AUTH_SERVICE_URL, json={"token": token})
        if resp.status_code != 200:
            raise HTTPException(status_code=401, detail="Invalid token")
        payload = resp.json()
    return payload

@router.get("/users/me")
async def get_me(payload=Depends(get_current_user)):
    return payload
