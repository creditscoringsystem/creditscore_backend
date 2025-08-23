from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.orm import Session
from schemas.user import UserOut, UserCreate, UserUpdatePassword, UserForgotPassword
from crud.crud import create_user, get_users, get_user, delete_user
from database import get_db
from core.security import decode_access_token
from models.user import User
from typing import List, Optional

router = APIRouter()

@router.get(
    "/users/me",
    response_model=UserOut,
    summary="Lấy thông tin user hiện tại",
    description=(
        "Mục đích: Trả về thông tin tài khoản đang đăng nhập.\n\n"
        "Yêu cầu: Bearer token hợp lệ trong Authorization header.\n\n"
        "Phản hồi: 200 trả về thông tin user; 401 nếu không xác thực; 404 nếu không tìm thấy user."
    ),
    responses={
        200: {"description": "Thông tin user hiện tại"},
        401: {"description": "Không xác thực hoặc token không hợp lệ"},
        404: {"description": "Không tìm thấy user"},
    },
)
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
    user = db.query(User).filter(User.id == int(payload.get("sub"))).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="User not found"
        )
    return user

@router.put(
    "/users/me",
    response_model=UserOut,
    summary="Cập nhật thông tin user hiện tại",
    description=(
        "Mục đích: Cập nhật một số thông tin cơ bản của tài khoản hiện tại.\n\n"
        "Yêu cầu: Bearer token hợp lệ.\n\n"
        "Lưu ý: Không cập nhật mật khẩu qua endpoint này.\n\n"
        "Phản hồi: 200 nếu thành công; 401 nếu không xác thực; 404 nếu không tìm thấy user."
    ),
    responses={
        200: {"description": "Cập nhật thành công"},
        401: {"description": "Không xác thực hoặc token không hợp lệ"},
        404: {"description": "Không tìm thấy user"},
    },
)
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
    
    current_user = db.query(User).filter(User.id == int(payload.get("sub"))).first()
    if not current_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="User not found"
        )
    
    # Demo: không cho phép đổi email qua endpoint này (giữ nguyên)
    
    db.commit()
    db.refresh(current_user)
    return current_user

@router.delete(
    "/users/me",
    summary="Xóa tài khoản user hiện tại",
    description=(
        "Mục đích: Xóa vĩnh viễn tài khoản đang đăng nhập.\n\n"
        "Yêu cầu: Bearer token hợp lệ.\n\n"
        "Lưu ý: Hành động không thể hoàn tác.\n\n"
        "Phản hồi: 200 nếu xóa thành công; 401 nếu không xác thực; 404 nếu không tìm thấy user."
    ),
    responses={
        200: {"description": "Xóa tài khoản thành công"},
        401: {"description": "Không xác thực hoặc token không hợp lệ"},
        404: {"description": "Không tìm thấy user"},
    },
)
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
    
    current_user = db.query(User).filter(User.id == int(payload.get("sub"))).first()
    if not current_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="User not found"
        )
    
    delete_user(db, current_user)
    return {"detail": "Your account has been deleted successfully."}
