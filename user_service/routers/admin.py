from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from schemas.user import UserOut, UserCreate
from crud.crud import get_users, get_user_by_username, get_user, delete_user, create_user
from database import get_db
from core.security import decode_access_token
from models.user import User
from typing import List, Optional
from fastapi import Query

router = APIRouter()

def get_current_admin(request: Request, db: Session = Depends(get_db)):
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Not authenticated")
    token = auth_header.split(" ")[1]
    payload = decode_access_token(token)
    if not payload or not payload.get("is_admin"):
        raise HTTPException(status_code=403, detail="Not admin")
    user = get_user_by_username(db, payload.get("sub"))
    if not user or not user.is_admin:
        raise HTTPException(status_code=403, detail="Not admin")
    return user

@router.get("/admin/users", response_model=List[UserOut])
def list_users_admin(admin=Depends(get_current_admin), db: Session = Depends(get_db)):
    return get_users(db)

@router.post("/admin/users", response_model=UserOut)
def create_user_admin(user: UserCreate, admin=Depends(get_current_admin), db: Session = Depends(get_db)):
    if user.username and get_user_by_username(db, user.username):
        raise HTTPException(status_code=400, detail="Username already registered")
    return create_user(db, user)

@router.get("/admin/users/{user_id}", response_model=UserOut)
def get_user_detail_admin(user_id: int, admin=Depends(get_current_admin), db: Session = Depends(get_db)):
    user = get_user(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@router.delete("/admin/users/{user_id}")
def delete_user_admin(user_id: int, admin=Depends(get_current_admin), db: Session = Depends(get_db)):
    user = get_user(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found. Cannot delete.")
    delete_user(db, user)
    return {"detail": f"User '{user.username}' has been deleted successfully."}

@router.get("/admin/summary", response_model=dict)
def admin_summary(admin=Depends(get_current_admin), db: Session = Depends(get_db)):
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
