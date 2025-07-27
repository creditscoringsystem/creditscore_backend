from fastapi import APIRouter, Depends, HTTPException, status
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

@router.get(
    "/me",
    response_model=list[ConsentOut],
    summary="Lấy danh sách đồng ý",
    description="""
    Lấy danh sách tất cả consent (đồng ý) của user hiện tại.
    
    **Yêu cầu:**
    - Header `X-User-Id` phải được cung cấp
    
    **Trả về:**
    - Danh sách các consent với thông tin chi tiết
    """,
    responses={
        200: {
            "description": "Danh sách consent",
            "content": {
                "application/json": {
                    "example": [
                        {
                            "id": 1,
                            "service": "credit_score",
                            "scope": "read_profile",
                            "granted": True,
                            "revoked_at": None,
                            "created_at": "2024-01-01T00:00:00Z"
                        }
                    ]
                }
            }
        },
        401: {
            "description": "Thiếu header X-User-Id"
        }
    }
)
def get_my_consents(db: Session = Depends(get_db), user=Depends(get_current_user)):
    return crud.get_consents(db, user["user_id"])

@router.post(
    "/revoke",
    response_model=ConsentOut,
    summary="Thu hồi đồng ý",
    description="""
    Thu hồi một consent (đồng ý) của user.
    
    **Yêu cầu:**
    - Header `X-User-Id` phải được cung cấp
    - `consent_id` phải tồn tại và thuộc về user
    
    **Tham số:**
    - `consent_id`: ID của consent cần thu hồi
    
    **Lưu ý:**
    - Consent sẽ được đánh dấu là đã thu hồi
    - Không thể thu hồi consent đã bị thu hồi trước đó
    """,
    responses={
        200: {
            "description": "Consent đã được thu hồi"
        },
        401: {
            "description": "Thiếu header X-User-Id"
        },
        404: {
            "description": "Không tìm thấy consent",
            "content": {
                "application/json": {
                    "example": {"detail": "Consent not found"}
                }
            }
        }
    }
)
def revoke_consent(consent_id: int, db: Session = Depends(get_db), user=Depends(get_current_user)):
    consent = crud.revoke_consent(db, user["user_id"], consent_id)
    if not consent:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Consent not found"
        )
    return consent 