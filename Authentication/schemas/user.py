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

class UserOut(UserBase):
    id: int
    class Config:
        orm_mode = True

class UserLogin(BaseModel):
    username: str
    password: str

class UserUpdatePassword(BaseModel):
    old_password: str
    new_password: str

class UserForgotPassword(BaseModel):
    username: str
