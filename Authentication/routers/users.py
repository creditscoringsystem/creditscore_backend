from fastapi import APIRouter, Depends, Request, HTTPException
from sqlalchemy.orm import Session
from ..schemas.user import UserOut
from ..crud.user import get_user_by_username
from ..database import get_db
from ..core.security import decode_access_token

router = APIRouter()

def get_current_user(request: Request, db: Session = Depends(get_db)):
    token = request.cookies.get("access_token")
    if not token:
        raise HTTPException(status_code=401, detail="Not authenticated")
    if token.startswith("Bearer "):
        token = token.split(" ")[1]
    payload = decode_access_token(token)
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid token")
    user = get_user_by_username(db, payload.get("sub"))
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    return user

@router.get("/users/me", response_model=UserOut)
def get_me(user=Depends(get_current_user)):
    return user
