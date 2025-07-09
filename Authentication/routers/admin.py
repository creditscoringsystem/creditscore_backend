from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..schemas.user import UserOut
from ..crud.user import get_users, get_user_by_username, delete_user
from ..database import get_db
from ..core.security import decode_access_token
from fastapi import Header
from typing import List

router = APIRouter()

def get_current_admin(db: Session = Depends(get_db), authorization: str = Header(None)):
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Not authenticated")
    token = authorization.split()[1]
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
        raise HTTPException(status_code=404, detail="User not found")
    delete_user(db, user)
    return {"msg": "User deleted"}
