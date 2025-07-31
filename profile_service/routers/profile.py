from fastapi import APIRouter, Depends, HTTPException, Body, status
from sqlalchemy.orm import Session
from schemas.profile import ProfileOut, ProfileUpdate
from crud import crud
from database import SessionLocal
from core.security import get_current_user
from models.profile import Profile
from datetime import datetime

router = APIRouter(prefix="/profile", tags=["profile"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get(
    "/me",
    response_model=ProfileOut,
    summary="Lấy thông tin hồ sơ cá nhân",
    description="""
    Lấy thông tin hồ sơ cá nhân của user hiện tại dựa trên user_id từ header.
    
    **Yêu cầu:**
    - Header `X-User-Id` phải được cung cấp
    
    **Trả về:**
    - Thông tin profile nếu tồn tại
    - 404 nếu chưa có profile
    """,
    responses={
        200: {
            "description": "Thông tin hồ sơ cá nhân"
        },
        401: {
            "description": "Thiếu header X-User-Id"
        },
        404: {
            "description": "Không tìm thấy profile"
        }
    }
)
def get_my_profile(db: Session = Depends(get_db), user=Depends(get_current_user)):
    """
    Lấy thông tin hồ sơ cá nhân của user hiện tại.
    """
    profile = crud.get_profile_by_user_id(db, user["user_id"])
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Profile not found"
        )
    return profile

@router.put(
    "/me",
    response_model=ProfileOut,
    summary="Cập nhật hồ sơ cá nhân",
    description="""
    Cập nhật thông tin hồ sơ cá nhân cho user hiện tại.
    
    **Yêu cầu:**
    - Header `X-User-Id` phải được cung cấp
    - Profile phải đã tồn tại
    
    **Lưu ý:**
    - Chỉ cập nhật các trường được cung cấp
    - Các trường không cung cấp sẽ giữ nguyên giá trị cũ
    """,
    responses={
        200: {
            "description": "Hồ sơ đã được cập nhật thành công"
        },
        401: {
            "description": "Thiếu header X-User-Id"
        },
        404: {
            "description": "Không tìm thấy profile để cập nhật"
        },
        422: {
            "description": "Dữ liệu không hợp lệ"
        }
    }
)
def update_my_profile(payload: ProfileUpdate, db: Session = Depends(get_db), user=Depends(get_current_user)):
    """
    Cập nhật thông tin hồ sơ cá nhân của user hiện tại.
    """
    profile = crud.update_profile(db, user["user_id"], payload)
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Profile not found"
        )
    return profile

@router.post(
    "/me",
    response_model=ProfileOut,
    summary="Tạo mới hồ sơ cá nhân",
    description="""
    Tạo mới hồ sơ cá nhân cho user hiện tại.
    
    **Yêu cầu:**
    - Header `X-User-Id` phải được cung cấp
    - User chưa có profile
    
    **Lưu ý:**
    - Chỉ tạo được 1 profile cho mỗi user
    - Nếu đã có profile sẽ trả về lỗi 400
    """,
    status_code=status.HTTP_201_CREATED,
    responses={
        201: {
            "description": "Hồ sơ đã được tạo thành công"
        },
        400: {
            "description": "Profile đã tồn tại"
        },
        401: {
            "description": "Thiếu header X-User-Id"
        },
        422: {
            "description": "Dữ liệu không hợp lệ"
        }
    }
)
def create_my_profile(
    payload: ProfileUpdate = Body(..., description="Thông tin hồ sơ cá nhân"),
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):
    """
    Tạo mới hồ sơ cá nhân cho user hiện tại. Trả về lỗi nếu đã có profile.
    """
    existing = crud.get_profile_by_user_id(db, user["user_id"])
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="Profile already exists"
        )
    
    # Convert date_of_birth string to Date object if provided
    date_of_birth = None
    if payload.date_of_birth:
        try:
            date_of_birth = datetime.strptime(payload.date_of_birth, "%Y-%m-%d").date()
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Invalid date format. Use YYYY-MM-DD"
            )
    
    new_profile = Profile(
        user_id=user["user_id"],
        full_name=payload.full_name,
        email=payload.email,
        phone=payload.phone,
        avatar=payload.avatar,
        date_of_birth=date_of_birth,
        address=payload.address,
    )
    db.add(new_profile)
    db.commit()
    db.refresh(new_profile)
    return new_profile 