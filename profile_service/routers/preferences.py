from fastapi import APIRouter, Depends
from schemas.preferences import Preferences
from core.security import get_current_user

router = APIRouter(prefix="/preferences", tags=["preferences"])

@router.get("/me", response_model=Preferences)
def get_preferences(user=Depends(get_current_user)):
    return Preferences()

@router.put("/me", response_model=Preferences)
def update_preferences(payload: Preferences, user=Depends(get_current_user)):
    return payload 