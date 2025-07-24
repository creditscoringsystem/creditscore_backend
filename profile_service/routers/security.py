from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from schemas.device import DeviceOut, DeviceBase
from crud import crud
from database import SessionLocal
from core.security import get_current_user

router = APIRouter(prefix="/security", tags=["security"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/2fa/enable")
def enable_2fa(user=Depends(get_current_user)):
    return {"message": "2FA enabled (dummy)"}

@router.post("/2fa/disable")
def disable_2fa(user=Depends(get_current_user)):
    return {"message": "2FA disabled (dummy)"}

@router.get("/devices", response_model=list[DeviceOut])
def get_devices(db: Session = Depends(get_db), user=Depends(get_current_user)):
    return crud.get_devices(db, user["user_id"])

@router.delete("/devices/{device_id}")
def remove_device(device_id: str, db: Session = Depends(get_db), user=Depends(get_current_user)):
    ok = crud.remove_device(db, user["user_id"], device_id)
    if not ok:
        raise HTTPException(status_code=404, detail="Device not found")
    return {"message": "Device removed"} 