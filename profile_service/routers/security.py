from fastapi import APIRouter, Depends, status
from core.security import get_current_user

router = APIRouter(prefix="/security", tags=["security"])

@router.post(
    "/2fa/enable",
    summary="Bật xác thực 2 yếu tố",
    description="""
    Bật tính năng xác thực 2 yếu tố (2FA) cho tài khoản.
    
    **Yêu cầu:**
    - Header `X-User-Id` phải được cung cấp
    
    **Lưu ý:**
    - Đây là endpoint demo, chưa implement thực tế
    """,
    responses={
        200: {
            "description": "2FA đã được bật",
            "content": {
                "application/json": {
                    "example": {"message": "2FA enabled (dummy)"}
                }
            }
        },
        401: {
            "description": "Thiếu header X-User-Id"
        }
    }
)
def enable_2fa(user=Depends(get_current_user)):
    return {"message": "2FA enabled (dummy)"}

@router.post(
    "/2fa/disable",
    summary="Tắt xác thực 2 yếu tố",
    description="""
    Tắt tính năng xác thực 2 yếu tố (2FA) cho tài khoản.
    
    **Yêu cầu:**
    - Header `X-User-Id` phải được cung cấp
    
    **Lưu ý:**
    - Đây là endpoint demo, chưa implement thực tế
    """,
    responses={
        200: {
            "description": "2FA đã được tắt",
            "content": {
                "application/json": {
                    "example": {"message": "2FA disabled (dummy)"}
                }
            }
        },
        401: {
            "description": "Thiếu header X-User-Id"
        }
    }
)
def disable_2fa(user=Depends(get_current_user)):
    return {"message": "2FA disabled (dummy)"} 