from fastapi import APIRouter, Depends, HTTPException, status
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

@router.get(
    "/devices",
    response_model=list[DeviceOut],
    summary="Lấy danh sách thiết bị",
    description="""
    Lấy danh sách tất cả thiết bị đã đăng nhập của user.
    
    **Yêu cầu:**
    - Header `X-User-Id` phải được cung cấp
    
    **Trả về:**
    - Danh sách thiết bị với thông tin chi tiết
    """,
    responses={
        200: {
            "description": "Danh sách thiết bị",
            "content": {
                "application/json": {
                    "example": [
                        {
                            "device_id": "device_12345",
                            "device_name": "iPhone 15 Pro",
                            "last_login": "2024-01-01T10:30:00Z",
                            "is_active": True
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
def get_devices(db: Session = Depends(get_db), user=Depends(get_current_user)):
    return crud.get_devices(db, user["user_id"])

@router.delete(
    "/devices/{device_id}",
    summary="Xóa thiết bị",
    description="""
    Xóa một thiết bị khỏi danh sách thiết bị đã đăng nhập.
    
    **Yêu cầu:**
    - Header `X-User-Id` phải được cung cấp
    - `device_id` phải tồn tại trong danh sách thiết bị của user
    
    **Tham số:**
    - `device_id`: ID của thiết bị cần xóa
    """,
    responses={
        200: {
            "description": "Thiết bị đã được xóa",
            "content": {
                "application/json": {
                    "example": {"message": "Device removed"}
                }
            }
        },
        401: {
            "description": "Thiếu header X-User-Id"
        },
        404: {
            "description": "Không tìm thấy thiết bị",
            "content": {
                "application/json": {
                    "example": {"detail": "Device not found"}
                }
            }
        }
    }
)
def remove_device(device_id: str, db: Session = Depends(get_db), user=Depends(get_current_user)):
    ok = crud.remove_device(db, user["user_id"], device_id)
    if not ok:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Device not found"
        )
    return {"message": "Device removed"} 