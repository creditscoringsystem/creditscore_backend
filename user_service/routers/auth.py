from fastapi import APIRouter, Depends, HTTPException, status, Response, Request
from sqlalchemy.orm import Session
from schemas.user import UserLogin, UserOut, UserForgotPassword, UserUpdatePassword, UserCreate
from crud.crud import get_user_by_email, update_password, set_reset_token, reset_password_with_token, create_user
from database import get_db
from core.security import verify_password, create_access_token, decode_access_token, get_password_hash
from models.user import User
from typing import Optional
import secrets

router = APIRouter()

@router.post(
    "/auth/signup",
    response_model=UserOut,
    status_code=status.HTTP_201_CREATED,
    summary="Đăng ký tài khoản mới",
    description=(
        "Mục đích: Tạo tài khoản người dùng mới.\n\n"
        "Yêu cầu: Email duy nhất, password tối thiểu 6 ký tự.\n\n"
        "Phản hồi: 201 trả về thông tin user (không gồm password)."
    ),
    responses={
        201: {"description": "Tạo tài khoản thành công"},
        400: {"description": "Email đã tồn tại"},
    },
)
def signup(user_data: UserCreate, db: Session = Depends(get_db)):
    # Kiểm tra email đã tồn tại
    if get_user_by_email(db, user_data.email):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email đã tồn tại"
        )
    
    # Tạo user mới
    user = create_user(db, user_data)
    
    return user

@router.post(
    "/auth/login",
    summary="Đăng nhập và nhận access token",
    description=(
        "Mục đích: Xác thực bằng email/password và trả về JWT.\n\n"
        "Phản hồi: 200 trả về access_token; 401 nếu thông tin không đúng."
    ),
    responses={
        200: {"description": "Đăng nhập thành công"},
        401: {"description": "Sai tài khoản hoặc mật khẩu"},
    },
)
def login_for_access_token(form_data: UserLogin, db: Session = Depends(get_db)):
    user = get_user_by_email(db, form_data.email)
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Sai tài khoản hoặc mật khẩu",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = create_access_token(data={"sub": str(user.id), "email": user.email, "is_admin": user.is_admin})
    return {"access_token": access_token, "token_type": "bearer"}

@router.post(
    "/auth/verify-token",
    summary="Xác thực token",
    description=(
        "Mục đích: Kiểm tra JWT hợp lệ và trả payload.\n\n"
        "Phản hồi: 200 nếu hợp lệ; 401 nếu không hợp lệ."
    ),
    responses={
        200: {"description": "Token hợp lệ"},
        401: {"description": "Token không hợp lệ"},
    },
)
async def verify_token(request: Request):
    data = await request.json()
    token = data.get("token")
    payload = decode_access_token(token)
    if not payload:
        raise HTTPException(status_code=401, detail="Token không hợp lệ")
    return payload

@router.post(
    "/auth/forgot-password",
    summary="Yêu cầu đặt lại mật khẩu",
    description=(
        "Mục đích: Tạo reset_token gửi cho người dùng.\n\n"
        "Phản hồi: 200 trả về reset_token; 404 nếu email không tồn tại."
    ),
    responses={
        200: {"description": "Tạo reset_token thành công"},
        404: {"description": "Không tìm thấy user"},
    },
)
def forgot_password(data: UserForgotPassword, db: Session = Depends(get_db)):
    user = get_user_by_email(db, data.email)
    if not user:
        raise HTTPException(status_code=404, detail="Không tìm thấy user")
    token = set_reset_token(db, user)
    return {"reset_token": token}

@router.post(
    "/auth/reset-password",
    summary="Đặt lại mật khẩu bằng token",
    description=(
        "Mục đích: Đổi mật khẩu mới bằng reset_token hợp lệ.\n\n"
        "Phản hồi: 200 nếu thành công; 400 nếu token không hợp lệ/hết hạn."
    ),
    responses={
        200: {"description": "Đặt lại mật khẩu thành công"},
        400: {"description": "Token không hợp lệ hoặc hết hạn"},
    },
)
def reset_password_with_token(data: dict, db: Session = Depends(get_db)):
    token = data.get("reset_token")
    new_password = data.get("new_password")
    user = db.query(User).filter(User.reset_token == token).first()
    if not user:
        raise HTTPException(status_code=400, detail="Token không hợp lệ hoặc hết hạn")
    user.hashed_password = get_password_hash(new_password)
    user.reset_token = None
    db.commit()
    return {"detail": "Đặt lại mật khẩu thành công"}

@router.post(
    "/auth/change-password",
    summary="Đổi mật khẩu (đăng nhập)",
    description=(
        "Mục đích: Người dùng đã đăng nhập đổi mật khẩu.\n\n"
        "Yêu cầu: Bearer token hợp lệ.\n\n"
        "Phản hồi: 200 nếu thành công; 400 nếu mật khẩu cũ sai; 401 nếu không xác thực."
    ),
    responses={
        200: {"description": "Đổi mật khẩu thành công"},
        400: {"description": "Mật khẩu cũ không đúng"},
        401: {"description": "Không xác thực"},
    },
)
def change_password(data: UserUpdatePassword, db: Session = Depends(get_db), request: Request = None):
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Không xác thực")
    token = auth_header.split(" ")[1]
    payload = decode_access_token(token)
    if not payload:
        raise HTTPException(status_code=401, detail="Không xác thực")
    user = db.query(User).filter(User.id == int(payload.get("sub"))).first()
    if not user or not verify_password(data.old_password, user.hashed_password):
        raise HTTPException(status_code=400, detail="Old password is incorrect. Please try again.")
    user.hashed_password = get_password_hash(data.new_password)
    db.commit()
    return {"detail": "Password changed successfully."} 