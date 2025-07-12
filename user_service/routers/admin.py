from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from schemas.user import UserOut
from crud.crud import get_users, get_user_by_username, delete_user
from database import get_db
from typing import List, Optional
from fastapi import Query
import httpx
from models.user import User

router = APIRouter()

AUTH_VERIFY_URL = "http://localhost:8001/auth/verify-token"  # Sửa lại đúng port nếu cần
AUTH_USERS_URL = "http://localhost:8001/auth/users"
AUTH_SUMMARY_URL = "http://localhost:8001/auth/summary"

async def get_current_admin(request: Request):
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Not authenticated")
    token = auth_header.split(" ")[1]
    async with httpx.AsyncClient() as client:
        resp = await client.post(AUTH_VERIFY_URL, json={"token": token})
        if resp.status_code != 200:
            raise HTTPException(status_code=401, detail="Invalid token")
        payload = resp.json()
    if not payload.get("is_admin"):
        raise HTTPException(status_code=403, detail="Not admin")
    return payload

@router.get("/admin/users")
async def list_users_admin(admin=Depends(get_current_admin)):
    async with httpx.AsyncClient() as client:
        resp = await client.get(AUTH_USERS_URL)
        if resp.status_code != 200:
            raise HTTPException(status_code=resp.status_code, detail="Cannot fetch users from auth_service")
        users = resp.json()
    return users

@router.delete("/admin/users/{username}")
async def delete_user_admin(username: str, admin=Depends(get_current_admin)):
    # Gọi API sang auth_service để xóa user
    async with httpx.AsyncClient() as client:
        resp = await client.delete(f"{AUTH_USERS_URL}/{username}")
        if resp.status_code == 404:
            raise HTTPException(status_code=404, detail="User not found. Cannot delete.")
        elif resp.status_code != 200:
            raise HTTPException(status_code=resp.status_code, detail="Cannot delete user from auth_service")
        result = resp.json()
    return result

@router.post("/admin/users/{username}/toggle-active", tags=["admin"], responses={
    200: {
        "description": "Toggle user active/inactive status",
        "content": {"application/json": {"example": {
            "username": "alice",
            "disabled": True,
            "detail": "User 'alice' has been locked (inactive)."
        }}}
    },
    404: {"description": "User not found", "content": {"application/json": {"example": {"detail": "User not found"}}}}
})
async def toggle_user_active(username: str, admin=Depends(get_current_admin)):
    # Gọi API sang auth_service để toggle user status
    async with httpx.AsyncClient() as client:
        resp = await client.post(f"{AUTH_USERS_URL}/{username}/toggle-active")
        if resp.status_code == 404:
            raise HTTPException(status_code=404, detail="User not found")
        elif resp.status_code != 200:
            raise HTTPException(status_code=resp.status_code, detail="Cannot toggle user status from auth_service")
        result = resp.json()
    return result

@router.get("/admin/summary", tags=["admin"], response_model=dict)
async def admin_summary(admin=Depends(get_current_admin)):
    async with httpx.AsyncClient() as client:
        resp = await client.get(AUTH_SUMMARY_URL)
        if resp.status_code != 200:
            raise HTTPException(status_code=resp.status_code, detail="Cannot fetch summary from auth_service")
        summary = resp.json()
    return summary

@router.get("/admin/users/search", tags=["admin"], response_model=List[UserOut], responses={
    200: {
        "description": "Search and filter users",
        "content": {"application/json": {"example": [
            {
                "id": 1,
                "username": "alice",
                "email": "alice@example.com",
                "phonenumber": "0123456789",
                "full_name": "Alice",
                "disabled": False,
                "is_admin": False
            }
        ]}}
    }
})
async def search_users(
    query: Optional[str] = Query(None, description="Search by username, email, or phone"),
    is_admin: Optional[bool] = Query(None, description="Filter by admin status"),
    disabled: Optional[bool] = Query(None, description="Filter by active/inactive status"),
    admin=Depends(get_current_admin)
):
    params = {}
    if query:
        params["query"] = query
    if is_admin is not None:
        params["is_admin"] = is_admin
    if disabled is not None:
        params["disabled"] = disabled

    async with httpx.AsyncClient() as client:
        resp = await client.get(AUTH_USERS_URL, params=params)
        if resp.status_code != 200:
            raise HTTPException(status_code=resp.status_code, detail="Cannot fetch users from auth_service")
        users = resp.json()
    return users
