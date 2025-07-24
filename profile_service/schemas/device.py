from pydantic import BaseModel
from typing import Optional

class DeviceOut(BaseModel):
    device_id: str
    device_name: Optional[str]
    last_login: Optional[str]
    is_active: bool
    class Config:
        orm_mode = True

class DeviceBase(BaseModel):
    device_id: str
    device_name: Optional[str] 