from fastapi import APIRouter, Depends, HTTPException, status, Response, Request
from sqlalchemy.orm import Session
from schemas.user import UserLogin, UserOut, UserForgotPassword, UserUpdatePassword, UserCreate
from crud.crud import get_user_by_username, update_password, set_reset_token, reset_password_with_token, create_user
from database import get_db
from core.security import verify_password, create_access_token, decode_access_token, get_password_hash
from models.user import User
from typing import Optional
import secrets

router = APIRouter()

@router.post("/auth/signup", response_model=UserOut, status_code=status.HTTP_201_CREATED)
def signup(user_data: UserCreate, db: Session = Depends(get_db)):
    """
    Đăng ký tài khoản mới.
    
    **Yêu cầu:**
    - Username bắt buộc và duy nhất
    - Password bắt buộc (tối thiểu 6 ký tự)
    
    **Trả về:**
    - Thông tin user đã tạo (không bao gồm password)
    - user_id để sử dụng cho Profile Service
    """
    # Kiểm tra username đã tồn tại
    if get_user_by_username(db, user_data.username):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered"
        )
    
    # Tạo user mới
    user = create_user(db, user_data)
    
    return user

@router.post("/auth/login")
def login_for_access_token(form_data: UserLogin, db: Session = Depends(get_db)):
    """
    Đăng nhập bằng username và password.
    """
    user = get_user_by_username(db, form_data.username)
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = create_access_token(data={"sub": user.username, "is_admin": user.is_admin})
    return {"access_token": access_token, "token_type": "bearer"}

@router.post("/auth/verify-token")
async def verify_token(request: Request):
    data = await request.json()
    token = data.get("token")
    payload = decode_access_token(token)
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid token")
    return payload

@router.post("/auth/forgot-password")
def forgot_password(data: UserForgotPassword, db: Session = Depends(get_db)):
    user = get_user_by_username(db, data.username)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    token = set_reset_token(db, user)
    return {"reset_token": token}

@router.post("/auth/reset-password")
def reset_password_with_token(data: dict, db: Session = Depends(get_db)):
    token = data.get("reset_token")
    new_password = data.get("new_password")
    user = db.query(User).filter(User.reset_token == token).first()
    if not user:
        raise HTTPException(status_code=400, detail="Invalid or expired reset token. Please request a new password reset.")
    user.hashed_password = get_password_hash(new_password)
    user.reset_token = None
    db.commit()
    return {"detail": "Password reset successful. You can now log in with your new password."}

@router.post("/auth/change-password")
def change_password(data: UserUpdatePassword, db: Session = Depends(get_db), request: Request = None):
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Not authenticated")
    token = auth_header.split(" ")[1]
    payload = decode_access_token(token)
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid token")
    user = db.query(User).filter(User.username == payload.get("sub")).first()
    if not user or not verify_password(data.old_password, user.hashed_password):
        raise HTTPException(status_code=400, detail="Old password is incorrect. Please try again.")
    user.hashed_password = get_password_hash(data.new_password)
    db.commit()
    return {"detail": "Password changed successfully."} 