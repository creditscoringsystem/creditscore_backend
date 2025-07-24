from pydantic import BaseModel
from typing import Optional

class ProfileOut(BaseModel):
    user_id: str
    full_name: Optional[str]
    email: Optional[str]
    phone: Optional[str]
    avatar: Optional[str]
    class Config:
        orm_mode = True

class ProfileUpdate(BaseModel):
    full_name: Optional[str]
    email: Optional[str]
    phone: Optional[str]
    avatar: Optional[str] 