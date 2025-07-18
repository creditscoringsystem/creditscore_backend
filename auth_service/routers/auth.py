from fastapi import APIRouter, Depends, HTTPException, status, Response, Request, Query
from sqlalchemy.orm import Session
from pydantic import BaseModel
from schemas.user import UserCreate, UserLogin, UserOut, UserForgotPassword
from crud import create_user, get_user_by_username, get_user_by_email, get_user_by_phonenumber, get_users, delete_user
from database import get_db
from core.security import verify_password, create_access_token, decode_access_token, get_password_hash
from models.user import User
from typing import List, Optional
import json
import secrets

router = APIRouter()

def set_reset_token(db: Session, user: User) -> str:
    """Generate and set reset token for user"""
    token = secrets.token_urlsafe(32)
    user.reset_token = token
    db.commit()
    return token

@router.post("/users", response_model=UserOut)
def create_user_endpoint(user: UserCreate, db: Session = Depends(get_db)):
    # Đăng ký user mới
    if user.username and get_user_by_username(db, user.username):
        raise HTTPException(status_code=400, detail="Username already registered")
    if user.email and get_user_by_email(db, user.email):
        raise HTTPException(status_code=400, detail="Email already registered")
    if user.phonenumber and get_user_by_phonenumber(db, user.phonenumber):
        raise HTTPException(status_code=400, detail="Phonenumber already registered")
    return create_user(db, user)

@router.post("/login")
def login_for_access_token(form_data: UserLogin, db: Session = Depends(get_db)):
    identifier = form_data.username
    user = (
        get_user_by_username(db, identifier)
        or get_user_by_email(db, identifier)
        or get_user_by_phonenumber(db, identifier)
    )
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username/email/phonenumber or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = create_access_token(data={"sub": user.username, "is_admin": user.is_admin})
    return {"access_token": access_token, "token_type": "bearer"}

@router.post(
    "/logout",
    responses={
        200: {"description": "Logout successful", "content": {"application/json": {"example": {"detail": "Logout successful. You have been signed out."}}}}
    }
)
def logout(response: Response):
    response.delete_cookie("access_token")
    return {"detail": "Logout successful. You have been signed out."}


@router.post(
    "/forgot-password",
    responses={
        200: {"description": "Reset token generated", "content": {"application/json": {"example": {"reset_token": "reset-token-abc123"}}}},
        404: {"description": "User not found", "content": {"application/json": {"example": {"detail": "User not found"}}}}
    }
)
def forgot_password(data: UserForgotPassword, db: Session = Depends(get_db)):
    user = get_user_by_username(db, data.username)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    token = set_reset_token(db, user)
    # Ở đây bạn có thể gửi email hoặc trả về token cho client
    return {"reset_token": token}

class ResetPasswordRequest(BaseModel):
    reset_token: str
    new_password: str

@router.post(
    "/reset-password",
    responses={
        200: {"description": "Password reset successful", "content": {"application/json": {"example": {"detail": "Password reset successful. You can now log in with your new password."}}}},
        400: {"description": "Invalid or expired reset token", "content": {"application/json": {"example": {"detail": "Invalid or expired reset token. Please request a new password reset."}}}}
    }
)
def reset_password_with_token(data: ResetPasswordRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.reset_token == data.reset_token).first()
    if not user:
        raise HTTPException(status_code=400, detail="Invalid or expired reset token. Please request a new password reset.")
    user.hashed_password = get_password_hash(data.new_password)
    user.reset_token = None  # Xóa token sau khi dùng
    db.commit()
    return {"detail": "Password reset successful. You can now log in with your new password."}

class ChangePasswordRequest(BaseModel):
    old_password: str
    new_password: str

def get_token_from_request(request: Request):
    auth_header = request.headers.get("Authorization")
    if auth_header and auth_header.startswith("Bearer "):
        return auth_header.split(" ")[1]
    return None

@router.post(
    "/change-password",
    responses={
        200: {"description": "Password changed successfully", "content": {"application/json": {"example": {"detail": "Password changed successfully."}}}},
        400: {"description": "Old password is incorrect", "content": {"application/json": {"example": {"detail": "Old password is incorrect. Please try again."}}}}
    }
)
def change_password(data: ChangePasswordRequest, db: Session = Depends(get_db), request: Request = None):
    token = get_token_from_request(request)
    if not token:
        raise HTTPException(status_code=401, detail="Not authenticated")
    payload = decode_access_token(token)
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid token")
    user = db.query(User).filter(User.username == payload.get("sub")).first()
    if not user or not verify_password(data.old_password, user.hashed_password):
        raise HTTPException(status_code=400, detail="Old password is incorrect. Please try again.")
    user.hashed_password = get_password_hash(data.new_password)
    db.commit()
    return {"detail": "Password changed successfully."}

class RefreshTokenRequest(BaseModel):
    pass  # Nếu bạn dùng refresh token thực sự, thêm trường ở đây

@router.post(
    "/refresh",
    responses={
        200: {"description": "Token refreshed successfully", "content": {"application/json": {"example": {"detail": "Token refreshed successfully. You are still logged in."}}}},
        401: {"description": "Not authenticated", "content": {"application/json": {"example": {"detail": "Not authenticated"}}}}
    }
)
def refresh_token(request: Request, response: Response):
    token = get_token_from_request(request)
    if not token:
        raise HTTPException(status_code=401, detail="Not authenticated")
    payload = decode_access_token(token)
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid token")
    # Tạo access token mới
    new_token = create_access_token({"sub": payload.get("sub"), "is_admin": payload.get("is_admin")})
    response.set_cookie(
        key="access_token",
        value=new_token,
        httponly=True,
        secure=True,
        samesite="lax",
        max_age=60*30
    )
    return {"detail": "Token refreshed successfully. You are still logged in."}

class UpdateProfileRequest(BaseModel):
    email: Optional[str] = None
    phonenumber: Optional[str] = None
    full_name: Optional[str] = None

@router.post(
    "/update-profile",
    response_model=UserOut,
    responses={
        200: {
            "description": "Profile updated successfully",
            "content": {
                "application/json": {
                    "example": {
                        "id": 1,
                        "username": "alice",
                        "email": "newalice@example.com",
                        "phonenumber": "0987654321",
                        "full_name": "Alice Updated",
                        "disabled": False,
                        "is_admin": False
                    }
                }
            }
        },
        404: {"description": "User not found", "content": {"application/json": {"example": {"detail": "User not found"}}}}
    }
)
def update_profile(data: UpdateProfileRequest, db: Session = Depends(get_db), request: Request = None):
    token = get_token_from_request(request)
    if not token:
        raise HTTPException(status_code=401, detail="Not authenticated")
    payload = decode_access_token(token)
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid token")
    user = db.query(User).filter(User.username == payload.get("sub")).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if data.email is not None:
        user.email = data.email
    if data.phonenumber is not None:
        user.phonenumber = data.phonenumber
    if data.full_name is not None:
        user.full_name = data.full_name
    db.commit()
    db.refresh(user)
    return user

@router.post("/verify-token")
async def verify_token(request: Request):
    data = await request.json()
    token = data.get("token")
    payload = decode_access_token(token)
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid token")
    return payload

@router.get("/users", response_model=List[UserOut])
def list_users(
    query: Optional[str] = Query(None, description="Search by username, email, or phone"),
    is_admin: Optional[bool] = Query(None, description="Filter by admin status"),
    disabled: Optional[bool] = Query(None, description="Filter by active/inactive status"),
    db: Session = Depends(get_db)
):
    users = get_users(db)
    if query:
        users = [
            user for user in users
            if (user.username and query.lower() in user.username.lower()) or
               (user.email and query.lower() in user.email.lower()) or
               (user.phonenumber and query.lower() in user.phonenumber.lower())
        ]
    if is_admin is not None:
        users = [user for user in users if user.is_admin == is_admin]
    if disabled is not None:
        users = [user for user in users if user.disabled == disabled]
    return users

@router.get("/users/{user_id}", response_model=UserOut)
def get_user_detail(user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@router.put("/users/{user_id}", response_model=UserOut)
def update_user(user_id: int, user_update: UserCreate, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    user.username = user_update.username
    user.email = user_update.email
    user.phonenumber = user_update.phonenumber
    user.full_name = user_update.full_name
    user.disabled = user_update.disabled
    db.commit()
    db.refresh(user)
    return user

@router.patch("/users/{user_id}", response_model=UserOut)
def patch_user(user_id: int, user_update: dict, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    for key, value in user_update.items():
        if hasattr(user, key):
            setattr(user, key, value)
    db.commit()
    db.refresh(user)
    return user

@router.delete("/users/{user_id}")
def delete_user_endpoint(user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    delete_user(db, user)
    return {"detail": f"User '{user.username}' has been deleted successfully."}

@router.get("/summary")
def user_summary(db: Session = Depends(get_db)):
    from sqlalchemy import func
    from models.user import User
    from datetime import date
    total_users = db.query(func.count()).select_from(User).scalar()
    active_users = db.query(func.count()).select_from(User).filter_by(disabled=False).scalar()
    inactive_users = db.query(func.count()).select_from(User).filter_by(disabled=True).scalar()
    admin_users = db.query(func.count()).select_from(User).filter_by(is_admin=True).scalar()
    today = date.today()
    new_users_today = db.query(func.count()).select_from(User).filter(
        func.date(User.created_at) == today
    ).scalar()
    return {
        "total_users": total_users,
        "active_users": active_users,
        "inactive_users": inactive_users,
        "admin_users": admin_users,
        "new_users_today": new_users_today
    }






