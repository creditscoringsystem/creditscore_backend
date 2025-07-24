from sqlalchemy.orm import Session
from models.profile import Profile
from models.device import Device
from models.consent import Consent
from schemas.profile import ProfileUpdate
from schemas.device import DeviceBase

# Profile CRUD

def get_profile_by_user_id(db: Session, user_id: str):
    return db.query(Profile).filter(Profile.user_id == user_id).first()

def update_profile(db: Session, user_id: str, payload: ProfileUpdate):
    profile = db.query(Profile).filter(Profile.user_id == user_id).first()
    if not profile:
        return None
    for field, value in payload.dict(exclude_unset=True).items():
        setattr(profile, field, value)
    db.commit()
    db.refresh(profile)
    return profile

# Device CRUD

def get_devices(db: Session, user_id: str):
    return db.query(Device).filter(Device.user_id == user_id).all()

def remove_device(db: Session, user_id: str, device_id: str):
    device = db.query(Device).filter(Device.user_id == user_id, Device.device_id == device_id).first()
    if device:
        db.delete(device)
        db.commit()
        return True
    return False

# Consent CRUD

def get_consents(db: Session, user_id: str):
    return db.query(Consent).filter(Consent.user_id == user_id).all()

def revoke_consent(db: Session, user_id: str, consent_id: int):
    consent = db.query(Consent).filter(Consent.user_id == user_id, Consent.id == consent_id).first()
    if consent:
        consent.granted = False
        from datetime import datetime
        consent.revoked_at = datetime.utcnow()
        db.commit()
        db.refresh(consent)
        return consent
    return None 