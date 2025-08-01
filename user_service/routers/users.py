from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.orm import Session
from schemas.user import UserOut, UserCreate, UserUpdatePassword, UserForgotPassword
from crud.crud import get_user_by_username, create_user, get_users, get_user, delete_user
from database import get_db
from core.security import decode_access_token
from models.user import User
from typing import List, Optional

router = APIRouter()

@router.get("/users/me", response_model=UserOut)
def get_me(request: Request, db: Session = Depends(get_db)):
    """
    Lấy thông tin user hiện tại.
    
    **Yêu cầu:**
    - Bearer token trong Authorization header
    
    **Trả về:**
    - Thông tin user hiện tại
    """
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, 
            detail="Not authenticated"
        )
    token = auth_header.split(" ")[1]
    payload = decode_access_token(token)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, 
            detail="Invalid token"
        )
    user = get_user_by_username(db, payload.get("sub"))
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="User not found"
        )
    return user

@router.put("/users/me", response_model=UserOut)
def update_me(
    request: Request, 
    user_update: UserCreate, 
    db: Session = Depends(get_db)
):
    """
    Cập nhật thông tin user hiện tại.
    
    **Yêu cầu:**
    - Bearer token trong Authorization header
    
    **Lưu ý:**
    - Chỉ cập nhật username (nếu chưa tồn tại)
    - Không thể cập nhật password qua endpoint này
    """
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, 
            detail="Not authenticated"
        )
    token = auth_header.split(" ")[1]
    payload = decode_access_token(token)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, 
            detail="Invalid token"
        )
    
    current_user = get_user_by_username(db, payload.get("sub"))
    if not current_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="User not found"
        )
    
    # Kiểm tra username mới có tồn tại không
    if user_update.username != current_user.username:
        existing_user = get_user_by_username(db, user_update.username)
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already exists"
            )
        current_user.username = user_update.username
    
    db.commit()
    db.refresh(current_user)
    return current_user

@router.delete("/users/me")
def delete_me(request: Request, db: Session = Depends(get_db)):
    """
    Xóa tài khoản user hiện tại.
    
    **Yêu cầu:**
    - Bearer token trong Authorization header
    
    **Lưu ý:**
    - Hành động này không thể hoàn tác
    """
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, 
            detail="Not authenticated"
        )
    token = auth_header.split(" ")[1]
    payload = decode_access_token(token)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, 
            detail="Invalid token"
        )
    
    current_user = get_user_by_username(db, payload.get("sub"))
    if not current_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="User not found"
        )
    
    delete_user(db, current_user)
    return {"detail": "Your account has been deleted successfully."}
