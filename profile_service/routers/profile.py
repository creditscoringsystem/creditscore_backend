from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from schemas.profile import ProfileOut, ProfileUpdate
from crud import crud
from database import SessionLocal
from core.security import get_current_user

router = APIRouter(prefix="/profile", tags=["profile"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/me", response_model=ProfileOut)
def get_my_profile(db: Session = Depends(get_db), user=Depends(get_current_user)):
    profile = crud.get_profile_by_user_id(db, user["user_id"])
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")
    return profile

@router.put("/me", response_model=ProfileOut)
def update_my_profile(payload: ProfileUpdate, db: Session = Depends(get_db), user=Depends(get_current_user)):
    profile = crud.update_profile(db, user["user_id"], payload)
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")
    return profile 