from fastapi import APIRouter, Depends, HTTPException, status, Header, Response, Request
from sqlalchemy.orm import Session
from ..schemas.user import UserCreate, UserLogin, UserOut, UserForgotPassword, UserUpdatePassword
from ..crud.user import create_user, get_user_by_username, get_user_by_email, get_user_by_phonenumber, update_password, set_reset_token, reset_password_with_token
from ..database import get_db
from ..core.security import verify_password, create_access_token, decode_access_token
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel
from ..models.user import User
from ..core.security import get_password_hash

router = APIRouter()


@router.post(
    "/signup",
    response_model=UserOut,
    responses={
        200: {
            "description": "User created successfully",
            "content": {
                "application/json": {
                    "example": {
                        "id": 1,
                        "username": "alice",
                        "email": "alice@example.com",
                        "phonenumber": "0123456789",
                        "full_name": "Alice",
                        "disabled": False,
                        "is_admin": False
                    }
                }
            }
        },
        400: {"description": "Bad request", "content": {"application/json": {"example": {"detail": "Username already registered"}}}}
    }
)
def signup(user: UserCreate, db: Session = Depends(get_db)):
    # Chỉ cần 1 trong 3 trường username, email, phonenumber
    if not (user.username or user.email or user.phonenumber):
        raise HTTPException(status_code=400, detail="At least one of username, email, or phonenumber must be provided")
    if user.username and get_user_by_username(db, user.username):
        raise HTTPException(status_code=400, detail="Username already registered")
    if user.email and get_user_by_email(db, user.email):
        raise HTTPException(status_code=400, detail="Email already registered")
    if user.phonenumber and get_user_by_phonenumber(db, user.phonenumber):
        raise HTTPException(status_code=400, detail="Phonenumber already registered")
    # Không truyền is_admin từ client
    return create_user(db, user)

@router.post(
    "/login",
    responses={
        200: {
            "description": "Login successful, access token set in cookie",
            "content": {"application/json": {"example": {"detail": "Login successful. Access token set in cookie."}}}
        },
        401: {"description": "Unauthorized", "content": {"application/json": {"example": {"detail": "Incorrect username/email/phonenumber or password"}}}}
    }
)
def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
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
    response = Response()
    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        secure=True,
        samesite="lax",
        max_age=60*30  # 30 phút
    )
    return response

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

@router.post(
    "/change-password",
    responses={
        200: {"description": "Password changed successfully", "content": {"application/json": {"example": {"detail": "Password changed successfully."}}}},
        400: {"description": "Old password is incorrect", "content": {"application/json": {"example": {"detail": "Old password is incorrect. Please try again."}}}}
    }
)
def change_password(data: ChangePasswordRequest, db: Session = Depends(get_db), request: Request = None):
    token = request.cookies.get("access_token")
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
    token = request.cookies.get("access_token")
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
    email: str = None
    phonenumber: str = None
    full_name: str = None

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
    token = request.cookies.get("access_token")
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






