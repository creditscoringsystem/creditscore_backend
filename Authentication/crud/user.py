from sqlalchemy.orm import Session
from ..models.user import User
from ..schemas.user import UserCreate, UserUpdatePassword
from ..core.security import get_password_hash, verify_password
import secrets
from typing import List

def create_user(db: Session, user: UserCreate):
    # Kiểm tra số lượng user trong DB
    user_count = db.query(User).count()
    is_admin = user_count == 0  # User đầu tiên là admin
    db_user = User(
        username=user.username,
        email=user.email,
        phonenumber=user.phonenumber,
        full_name=user.full_name,
        hashed_password=get_password_hash(user.password),
        disabled=user.disabled,
        is_admin=is_admin
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def get_user_by_username(db: Session, username: str):
    return db.query(User).filter(User.username == username).first()

def get_user_by_email(db: Session, email: str):
    return db.query(User).filter(User.email == email).first()

def get_user_by_phonenumber(db: Session, phonenumber: str):
    return db.query(User).filter(User.phonenumber == phonenumber).first()

def get_user(db: Session, user_id: int):
    return db.query(User).filter(User.id == user_id).first()

def get_users(db: Session) -> List[User]:
    return db.query(User).all()

def update_password(db: Session, user: User, new_password: str):
    user.hashed_password = get_password_hash(new_password)
    db.commit()
    db.refresh(user)
    return user

def set_reset_token(db: Session, user: User):
    token = secrets.token_urlsafe(32)
    user.reset_token = token
    db.commit()
    db.refresh(user)
    return token

def reset_password_with_token(db: Session, token: str, new_password: str):
    user = db.query(User).filter(User.reset_token == token).first()
    if user:
        user.hashed_password = get_password_hash(new_password)
        user.reset_token = None
        db.commit()
        db.refresh(user)
        return user
    return None

def delete_user(db: Session, user: User):
    db.delete(user)
    db.commit()
