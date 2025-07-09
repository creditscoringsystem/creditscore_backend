from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from ..schemas.user import UserOut
from ..crud.user import get_users, get_user_by_username, delete_user
from ..database import get_db
from ..core.security import decode_access_token
from typing import List, Optional
from fastapi import Query

router = APIRouter()

def get_current_admin(request: Request, db: Session = Depends(get_db)):
    token = request.cookies.get("access_token")
    if not token:
        raise HTTPException(status_code=401, detail="Not authenticated")
    # Nếu token có tiền tố "Bearer ", cắt bỏ
    if token.startswith("Bearer "):
        token = token.split(" ")[1]
    payload = decode_access_token(token)
    if not payload or not payload.get("is_admin"):
        raise HTTPException(status_code=403, detail="Not admin")
    user = get_user_by_username(db, payload.get("sub"))
    if not user or not user.is_admin:
        raise HTTPException(status_code=403, detail="Not admin")
    return user

@router.get("/admin/users", response_model=List[UserOut])
def list_users_admin(admin=Depends(get_current_admin)):
    db = admin.__dict__.get('_sa_instance_state').session
    users = db.query(admin.__class__).all()
    return [UserOut.from_orm(u) for u in users]

@router.delete("/admin/users/{username}")
def delete_user_admin(username: str, db: Session = Depends(get_db), admin=Depends(get_current_admin)):
    user = get_user_by_username(db, username)
    if not user:
        raise HTTPException(status_code=404, detail="User not found. Cannot delete.")
    delete_user(db, user)
    return {"detail": f"User '{username}' has been deleted successfully by admin."}

@router.post("/admin/users/{username}/toggle-active", tags=["admin"], responses={
    200: {
        "description": "Toggle user active/inactive status",
        "content": {"application/json": {"example": {
            "username": "alice",
            "disabled": True,
            "detail": "User 'alice' has been locked (inactive)."
        }}}
    },
    404: {"description": "User not found", "content": {"application/json": {"example": {"detail": "User not found"}}}}
})
def toggle_user_active(username: str, db: Session = Depends(get_db), admin=Depends(get_current_admin)):
    user = get_user_by_username(db, username)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    user.disabled = not user.disabled
    db.commit()
    status = "locked (inactive)" if user.disabled else "unlocked (active)"
    return {
        "username": user.username,
        "disabled": user.disabled,
        "detail": f"User '{user.username}' has been {status}."
    }

@router.get("/admin/summary", tags=["admin"], response_model=dict, responses={
    200: {
        "description": "Admin dashboard summary",
        "content": {"application/json": {"example": {
            "total_users": 100,
            "active_users": 90,
            "inactive_users": 10,
            "admin_users": 2,
            "new_users_today": 5
        }}}
    }
})
def admin_summary(db: Session = Depends(get_db), admin=Depends(get_current_admin)):
    from sqlalchemy import func
    total_users = db.query(func.count()).select_from(admin.__class__).scalar()
    active_users = db.query(func.count()).select_from(admin.__class__).filter_by(disabled=False).scalar()
    inactive_users = db.query(func.count()).select_from(admin.__class__).filter_by(disabled=True).scalar()
    admin_users = db.query(func.count()).select_from(admin.__class__).filter_by(is_admin=True).scalar()
    from datetime import date
    today = date.today()
    new_users_today = db.query(func.count()).select_from(admin.__class__).filter(
        func.date(admin.__class__.created_at) == today
    ).scalar()
    return {
        "total_users": total_users,
        "active_users": active_users,
        "inactive_users": inactive_users,
        "admin_users": admin_users,
        "new_users_today": new_users_today
    }

@router.get("/admin/users/search", tags=["admin"], response_model=List[UserOut], responses={
    200: {
        "description": "Search and filter users",
        "content": {"application/json": {"example": [
            {
                "id": 1,
                "username": "alice",
                "email": "alice@example.com",
                "phonenumber": "0123456789",
                "full_name": "Alice",
                "disabled": False,
                "is_admin": False
            }
        ]}}
    }
})
def search_users(
    query: Optional[str] = Query(None, description="Search by username, email, or phone"),
    is_admin: Optional[bool] = Query(None, description="Filter by admin status"),
    disabled: Optional[bool] = Query(None, description="Filter by active/inactive status"),
    db: Session = Depends(get_db),
    admin=Depends(get_current_admin)
):
    q = db.query(admin.__class__)
    if query:
        q = q.filter(
            (admin.__class__.username.ilike(f"%{query}%")) |
            (admin.__class__.email.ilike(f"%{query}%")) |
            (admin.__class__.phonenumber.ilike(f"%{query}%"))
        )
    if is_admin is not None:
        q = q.filter(admin.__class__.is_admin == is_admin)
    if disabled is not None:
        q = q.filter(admin.__class__.disabled == disabled)
    users = q.all()
    return [UserOut.from_orm(u) for u in users]
