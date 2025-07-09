from fastapi import APIRouter, Depends, Header
from sqlalchemy.orm import Session
from ..schemas.user import UserOut
from ..crud.user import get_user_by_username
from ..database import get_db
from ..core.security import decode_access_token

router = APIRouter()

def get_current_user(db: Session = Depends(get_db), authorization: str = Header(None)):
    if not authorization or not authorization.startswith("Bearer "):
        return None
    token = authorization.split()[1]
    payload = decode_access_token(token)
    if not payload:
        return None
    user = get_user_by_username(db, payload.get("sub"))
    return user

@router.get("/users/me", response_model=UserOut)
def get_me(db: Session = Depends(get_db), user=Depends(get_current_user)):
    if not user:
        return {"msg": "Not authenticated"}
    return user
