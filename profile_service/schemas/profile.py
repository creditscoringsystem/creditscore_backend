from pydantic import BaseModel, Field, field_serializer
from typing import Optional
from datetime import datetime, date

class ProfileOut(BaseModel):
    user_id: str = Field(..., description="ID duy nhất của người dùng")
    full_name: Optional[str] = Field(None, description="Họ và tên đầy đủ")
    email: Optional[str] = Field(None, description="Email liên lạc (có thể khác với email đăng ký)")
    phone: Optional[str] = Field(None, description="Số điện thoại")
    avatar: Optional[str] = Field(None, description="URL ảnh đại diện")
    date_of_birth: Optional[date] = Field(None, description="Ngày sinh")
    address: Optional[str] = Field(None, description="Địa chỉ")
    created_at: Optional[datetime] = Field(None, description="Thời gian tạo")
    updated_at: Optional[datetime] = Field(None, description="Thời gian cập nhật cuối")
    
    @field_serializer('date_of_birth')
    def serialize_date_of_birth(self, value: Optional[date]) -> Optional[str]:
        """Convert date to string format YYYY-MM-DD"""
        if value is None:
            return None
        return value.strftime("%Y-%m-%d")
    
    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "user_id": "user_12345",
                "full_name": "Nguyễn Văn A",
                "email": "nguyenvana@gmail.com",
                "phone": "0123456789",
                "avatar": "https://example.com/avatar.jpg",
                "date_of_birth": "1990-01-01",
                "address": "123 Đường ABC, Quận 1, TP.HCM",
                "created_at": "2024-01-01T00:00:00Z",
                "updated_at": "2024-01-01T00:00:00Z"
            }
        }

class ProfileUpdate(BaseModel):
    full_name: Optional[str] = Field(
        None, 
        description="Họ và tên đầy đủ",
        min_length=1,
        max_length=100
    )
    email: Optional[str] = Field(
        None, 
        description="Email liên lạc (có thể khác với email đăng ký)",
        pattern=r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
    )
    phone: Optional[str] = Field(
        None, 
        description="Số điện thoại (định dạng: 0123456789)",
        pattern=r"^[0-9]{10,11}$"
    )
    avatar: Optional[str] = Field(
        None, 
        description="URL ảnh đại diện",
        pattern=r"^https?://.*"
    )
    date_of_birth: Optional[str] = Field(
        None,
        description="Ngày sinh (định dạng: YYYY-MM-DD)",
        pattern=r"^\d{4}-\d{2}-\d{2}$"
    )
    address: Optional[str] = Field(
        None,
        description="Địa chỉ",
        max_length=500
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "full_name": "Nguyễn Văn A",
                "email": "nguyenvana@gmail.com",
                "phone": "0123456789",
                "avatar": "https://example.com/avatar.jpg",
                "date_of_birth": "1990-01-01",
                "address": "123 Đường ABC, Quận 1, TP.HCM"
            }
        } 