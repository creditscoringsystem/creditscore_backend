from pydantic import BaseModel, EmailStr, root_validator
from typing import Optional

class UserBase(BaseModel):
    username: str
    email: Optional[EmailStr] = None
    phonenumber: Optional[str] = None
    full_name: Optional[str] = None
    disabled: Optional[bool] = False
    is_admin: Optional[bool] = False

class UserCreate(UserBase):
    password: str
    is_admin: Optional[bool] = None  # Không cho phép client truyền is_admin khi đăng ký

    @root_validator(pre=True)
    def at_least_one_identifier(cls, values):
        username = values.get('username')
        email = values.get('email')
        phonenumber = values.get('phonenumber')
        if not (username or email or phonenumber):
            raise ValueError('At least one of username, email, or phonenumber must be provided')
        return values

    model_config = {
        "json_schema_extra": {
            "example": {
                "username": "alice",
                "email": "alice@example.com",
                "phonenumber": "0123456789",
                "full_name": "Alice",
                "password": "yourpassword"
            }
        }
    }

class UserOut(UserBase):
    id: int
    class Config:
        from_attributes = True 

class UserLogin(BaseModel):
    username: str
    password: str
    model_config = {
        "json_schema_extra": {
            "example": {
                "username": "alice",
                "password": "yourpassword"
            }
        }
    }

class UserUpdatePassword(BaseModel):
    old_password: str
    new_password: str
    model_config = {
        "json_schema_extra": {
            "example": {
                "old_password": "oldpassword",
                "new_password": "newpassword"
            }
        }
    }

class UserForgotPassword(BaseModel):
    username: str
    model_config = {
        "json_schema_extra": {
            "example": {
                "username": "alice"
            }
        }
    }

class UserUpdateInfo(BaseModel):
    email: Optional[EmailStr] = None
    phonenumber: Optional[str] = None
    full_name: Optional[str] = None

    @root_validator(pre=True)
    def at_least_one_field(cls, values):
        email = values.get('email')
        phonenumber = values.get('phonenumber')
        full_name = values.get('full_name')
        if not (email or phonenumber or full_name):
            raise ValueError('At least one of email, phonenumber, or full_name must be provided')
        return values

    model_config = {
        "json_schema_extra": {
            "example": {
                "email": "alice@example.com",
                "phonenumber": "0123456789",
                "full_name": "Alice Updated"
            }
        }
    }
