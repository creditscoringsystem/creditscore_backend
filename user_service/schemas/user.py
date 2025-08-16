from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class UserBase(BaseModel):
    email: str = Field(..., description="Email đăng ký", pattern=r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
    disabled: Optional[bool] = Field(False, description="Trạng thái tài khoản")
    is_admin: Optional[bool] = Field(False, description="Quyền admin")

class UserCreate(UserBase):
    password: str = Field(..., description="Mật khẩu", min_length=6)
    is_admin: Optional[bool] = Field(False, description="Không cho phép client truyền is_admin khi đăng ký")

    class Config:
        json_schema_extra = {
            "example": {"email": "alice@example.com", "password": "yourpassword123"}
        }

class UserOut(UserBase):
    id: int = Field(..., description="ID duy nhất của user")
    created_at: Optional[datetime] = Field(None, description="Thời gian tạo tài khoản")
    
    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": 1,
                "email": "alice@example.com",
                "disabled": False,
                "is_admin": False,
                "created_at": "2024-01-01T00:00:00Z"
            }
        }

class UserLogin(BaseModel):
    email: str = Field(..., description="Email")
    password: str = Field(..., description="Mật khẩu")
    
    class Config:
        json_schema_extra = {
            "example": {"email": "alice@example.com", "password": "yourpassword123"}
        }

class UserUpdatePassword(BaseModel):
    old_password: str = Field(..., description="Mật khẩu cũ")
    new_password: str = Field(..., description="Mật khẩu mới", min_length=6)
    
    class Config:
        json_schema_extra = {
            "example": {
                "old_password": "oldpassword",
                "new_password": "newpassword123"
            }
        }

class UserForgotPassword(BaseModel):
    email: str = Field(..., description="Email")
    
    class Config:
        json_schema_extra = {
            "example": {"email": "alice@example.com"}
        }
