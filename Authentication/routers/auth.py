from fastapi import APIRouter, Depends, HTTPException, status, Header, Response
from sqlalchemy.orm import Session
from schemas.user import UserCreate, UserLogin, UserOut, UserForgotPassword, UserUpdatePassword
from crud.user import create_user, get_user_by_username, get_user_by_email, get_user_by_phonenumber, update_password, set_reset_token, reset_password_with_token
from database import get_db
from core.security import verify_password, create_access_token, decode_access_token
from fastapi.security import OAuth2PasswordRequestForm

router = APIRouter()

def get_current_username(authorization: str = Header(None)):
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Not authenticated")
    token = authorization.split()[1]
    payload = decode_access_token(token)
    if not payload or not payload.get("sub"):
        raise HTTPException(status_code=401, detail="Invalid token")
    return payload["sub"]

@router.post("/signup", response_model=UserOut)
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

@router.post("/login")
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


@router.post("/forgot-password")
def forgot_password(data: UserForgotPassword, db: Session = Depends(get_db)):
    user = get_user_by_username(db, data.username)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    token = set_reset_token(db, user)
    # Ở đây bạn có thể gửi email hoặc trả về token cho client
    return {"reset_token": token}

@router.post("/reset-password")
def reset_password(token: str, new_password: str, db: Session = Depends(get_db)):
    user = reset_password_with_token(db, token, new_password)
    if not user:
        raise HTTPException(status_code=400, detail="Invalid or expired token")
    return {"msg": "Password reset successful"}




