from sqlalchemy.orm import Session
from models.profile import Profile
from models.device import Device
from models.consent import Consent
from schemas.profile import ProfileUpdate
from schemas.device import DeviceBase
from datetime import datetime

# Profile CRUD

def get_profile_by_user_id(db: Session, user_id: str):
    return db.query(Profile).filter(Profile.user_id == user_id).first()

def update_profile(db: Session, user_id: str, payload: ProfileUpdate):
    profile = db.query(Profile).filter(Profile.user_id == user_id).first()
    if not profile:
        return None
    
    # Convert payload to dict and handle date_of_birth
    update_data = payload.dict(exclude_unset=True)
    
    # Convert date_of_birth string to Date object if provided
    if 'date_of_birth' in update_data and update_data['date_of_birth']:
        try:
            update_data['date_of_birth'] = datetime.strptime(
                update_data['date_of_birth'], "%Y-%m-%d"
            ).date()
        except ValueError:
            raise ValueError("Invalid date format. Use YYYY-MM-DD")
    
    # Update fields
    for field, value in update_data.items():
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

def grant_consent(db: Session, user_id: str, service: str, scope: str = None):
    """Grant consent for a service"""
    # Check if consent already exists
    existing = db.query(Consent).filter(
        Consent.user_id == user_id,
        Consent.service == service,
        Consent.scope == scope
    ).first()
    
    if existing:
        # Update existing consent
        existing.granted = True
        existing.revoked_at = None
        db.commit()
        db.refresh(existing)
        return existing
    
    # Create new consent
    new_consent = Consent(
        user_id=user_id,
        service=service,
        scope=scope,
        granted=True,
        created_at=datetime.utcnow()
    )
    db.add(new_consent)
    db.commit()
    db.refresh(new_consent)
    return new_consent

def revoke_consent(db: Session, user_id: str, consent_id: int):
    consent = db.query(Consent).filter(Consent.user_id == user_id, Consent.id == consent_id).first()
    if consent:
        consent.granted = False
        consent.revoked_at = datetime.utcnow()
        db.commit()
        db.refresh(consent)
        return consent
    return None 