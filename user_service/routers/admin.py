from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.orm import Session
from schemas.user import UserOut, UserCreate
from crud.crud import get_users, get_user, delete_user, create_user, get_user_by_email
from database import get_db
from core.security import decode_access_token
from models.user import User
from typing import List, Optional
from fastapi import Query

router = APIRouter()

def get_current_admin(request: Request, db: Session = Depends(get_db)):
    """
    Dependency để kiểm tra admin authentication.
    
    **Yêu cầu:**
    - Bearer token trong Authorization header
    - User phải có quyền admin
    """
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, 
            detail="Not authenticated"
        )
    token = auth_header.split(" ")[1]
    payload = decode_access_token(token)
    if not payload or not payload.get("is_admin"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, 
            detail="Not admin"
        )
    user = db.query(User).filter(User.id == int(payload.get("sub"))).first()
    if not user or not user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, 
            detail="Not admin"
        )
    return user

@router.get(
    "/admin/users",
    response_model=List[UserOut],
    summary="(Admin) Lấy danh sách tất cả users",
    description=(
        "Mục đích: Dành cho admin xem toàn bộ users.\n\n"
        "Yêu cầu: Bearer token với quyền admin.\n\n"
        "Phản hồi: 200 trả về danh sách users."
    ),
    responses={
        200: {"description": "Danh sách users"},
        401: {"description": "Không xác thực"},
        403: {"description": "Không có quyền admin"},
    },
)
def list_users_admin(
    admin=Depends(get_current_admin), 
    db: Session = Depends(get_db)
):
    """
    Lấy danh sách tất cả users (Admin only).
    
    **Yêu cầu:**
    - Bearer token với quyền admin
    
    **Trả về:**
    - Danh sách tất cả users trong hệ thống
    """
    return get_users(db)

@router.post(
    "/admin/users",
    response_model=UserOut,
    status_code=status.HTTP_201_CREATED,
    summary="(Admin) Tạo user mới",
    description=(
        "Mục đích: Admin tạo tài khoản user.\n\n"
        "Yêu cầu: Bearer token admin; email duy nhất.\n\n"
        "Phản hồi: 201 nếu tạo thành công; 400 nếu email tồn tại."
    ),
    responses={
        201: {"description": "Tạo user thành công"},
        400: {"description": "Email đã tồn tại"},
        401: {"description": "Không xác thực"},
        403: {"description": "Không có quyền admin"},
    },
)
def create_user_admin(
    user: UserCreate, 
    admin=Depends(get_current_admin), 
    db: Session = Depends(get_db)
):
    """
    Tạo user mới (Admin only).
    
    **Yêu cầu:**
    - Bearer token với quyền admin
    
    **Lưu ý:**
    - Email phải duy nhất
    - Password tối thiểu 6 ký tự
    """
    if get_user_by_email(db, user.email):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="Email already registered"
        )
    return create_user(db, user)

@router.get(
    "/admin/users/{user_id}",
    response_model=UserOut,
    summary="(Admin) Xem chi tiết user",
    description=(
        "Mục đích: Lấy thông tin chi tiết của một user theo ID.\n\n"
        "Yêu cầu: Bearer token admin.\n\n"
        "Phản hồi: 200 nếu tồn tại; 404 nếu không tìm thấy."
    ),
    responses={
        200: {"description": "Chi tiết user"},
        401: {"description": "Không xác thực"},
        403: {"description": "Không có quyền admin"},
        404: {"description": "Không tìm thấy user"},
    },
)
def get_user_detail_admin(
    user_id: int, 
    admin=Depends(get_current_admin), 
    db: Session = Depends(get_db)
):
    """
    Lấy thông tin chi tiết user theo ID (Admin only).
    
    **Yêu cầu:**
    - Bearer token với quyền admin
    - user_id phải tồn tại
    
    **Tham số:**
    - user_id: ID của user cần xem
    """
    user = get_user(db, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="User not found"
        )
    return user

@router.put(
    "/admin/users/{user_id}",
    response_model=UserOut,
    summary="(Admin) Cập nhật user",
    description=(
        "Mục đích: Cập nhật thông tin user theo ID.\n\n"
        "Yêu cầu: Bearer token admin; user phải tồn tại.\n\n"
        "Phản hồi: 200 nếu thành công; 404 nếu không tìm thấy."
    ),
    responses={
        200: {"description": "Cập nhật user thành công"},
        401: {"description": "Không xác thực"},
        403: {"description": "Không có quyền admin"},
        404: {"description": "Không tìm thấy user"},
    },
)
def update_user_admin(
    user_id: int,
    user_update: UserCreate,
    admin=Depends(get_current_admin), 
    db: Session = Depends(get_db)
):
    """
    Cập nhật thông tin user theo ID (Admin only).
    
    **Yêu cầu:**
    - Bearer token với quyền admin
    - user_id phải tồn tại
    
    **Tham số:**
    - user_id: ID của user cần cập nhật
    """
    user = get_user(db, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="User not found"
        )
    
    # Demo: không cho phép đổi email tại endpoint này (giữ nguyên)
    
    db.commit()
    db.refresh(user)
    return user

@router.delete(
    "/admin/users/{user_id}",
    summary="(Admin) Xóa user",
    description=(
        "Mục đích: Xóa user theo ID.\n\n"
        "Yêu cầu: Bearer token admin; user phải tồn tại.\n\n"
        "Phản hồi: 200 nếu xóa thành công; 404 nếu không tìm thấy."
    ),
    responses={
        200: {"description": "Xóa user thành công"},
        401: {"description": "Không xác thực"},
        403: {"description": "Không có quyền admin"},
        404: {"description": "Không tìm thấy user"},
    },
)
def delete_user_admin(
    user_id: int, 
    admin=Depends(get_current_admin), 
    db: Session = Depends(get_db)
):
    """
    Xóa user theo ID (Admin only).
    
    **Yêu cầu:**
    - Bearer token với quyền admin
    - user_id phải tồn tại
    
    **Tham số:**
    - user_id: ID của user cần xóa
    
    **Lưu ý:**
    - Hành động này không thể hoàn tác
    """
    user = get_user(db, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="User not found. Cannot delete."
        )
    delete_user(db, user)
    return {"detail": f"User '{user.email}' has been deleted successfully."}

@router.get(
    "/admin/summary",
    response_model=dict,
    summary="(Admin) Thống kê tổng quan hệ thống",
    description=(
        "Mục đích: Trả về số liệu tổng quan về users trong hệ thống.\n\n"
        "Yêu cầu: Bearer token admin.\n\n"
        "Phản hồi: 200 trả về các chỉ số thống kê."
    ),
    responses={
        200: {"description": "Thống kê tổng quan"},
        401: {"description": "Không xác thực"},
        403: {"description": "Không có quyền admin"},
    },
)
def admin_summary(
    admin=Depends(get_current_admin), 
    db: Session = Depends(get_db)
):
    """
    Lấy thống kê tổng quan hệ thống (Admin only).
    
    **Yêu cầu:**
    - Bearer token với quyền admin
    
    **Trả về:**
    - Thống kê tổng quan về users trong hệ thống
    """
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
