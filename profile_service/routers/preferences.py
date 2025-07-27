from fastapi import APIRouter, Depends, status
from schemas.preferences import Preferences
from core.security import get_current_user

router = APIRouter(prefix="/preferences", tags=["preferences"])

@router.get(
    "/me",
    response_model=Preferences,
    summary="Lấy tùy chọn người dùng",
    description="""
    Lấy tùy chọn cá nhân của user hiện tại.
    
    **Yêu cầu:**
    - Header `X-User-Id` phải được cung cấp
    
    **Trả về:**
    - Thông tin tùy chọn hiện tại
    """,
    responses={
        200: {
            "description": "Tùy chọn người dùng",
            "content": {
                "application/json": {
                    "example": {
                        "theme": "light",
                        "language": "vi",
                        "notifications": ["email", "sms", "push"]
                    }
                }
            }
        },
        401: {
            "description": "Thiếu header X-User-Id"
        }
    }
)
def get_preferences(user=Depends(get_current_user)):
    return Preferences()

@router.put(
    "/me",
    response_model=Preferences,
    summary="Cập nhật tùy chọn người dùng",
    description="""
    Cập nhật tùy chọn cá nhân của user hiện tại.
    
    **Yêu cầu:**
    - Header `X-User-Id` phải được cung cấp
    
    **Lưu ý:**
    - Chỉ cập nhật các trường được cung cấp
    - Các trường không cung cấp sẽ giữ nguyên giá trị cũ
    """,
    responses={
        200: {
            "description": "Tùy chọn đã được cập nhật"
        },
        401: {
            "description": "Thiếu header X-User-Id"
        },
        422: {
            "description": "Dữ liệu không hợp lệ",
            "content": {
                "application/json": {
                    "example": {
                        "detail": [
                            {
                                "loc": ["body", "theme"],
                                "msg": "string does not match regex",
                                "type": "value_error"
                            }
                        ]
                    }
                }
            }
        }
    }
)
def update_preferences(payload: Preferences, user=Depends(get_current_user)):
    return payload 