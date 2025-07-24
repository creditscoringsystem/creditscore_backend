from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from schemas.consent import ConsentOut
from crud import crud
from database import SessionLocal
from core.security import get_current_user

router = APIRouter(prefix="/consent", tags=["consent"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/me", response_model=list[ConsentOut])
def get_my_consents(db: Session = Depends(get_db), user=Depends(get_current_user)):
    return crud.get_consents(db, user["user_id"])

@router.post("/revoke", response_model=ConsentOut)
def revoke_consent(consent_id: int, db: Session = Depends(get_db), user=Depends(get_current_user)):
    consent = crud.revoke_consent(db, user["user_id"], consent_id)
    if not consent:
        raise HTTPException(status_code=404, detail="Consent not found")
    return consent 