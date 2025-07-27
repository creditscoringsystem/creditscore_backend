from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class DeviceOut(BaseModel):
    device_id: str = Field(..., description="ID duy nhất của thiết bị")
    device_name: Optional[str] = Field(None, description="Tên thiết bị")
    last_login: Optional[datetime] = Field(None, description="Thời gian đăng nhập cuối")
    is_active: bool = Field(..., description="Trạng thái hoạt động của thiết bị")
    
    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "device_id": "device_12345",
                "device_name": "iPhone 15 Pro",
                "last_login": "2024-01-01T10:30:00Z",
                "is_active": True
            }
        }

class DeviceBase(BaseModel):
    device_id: str = Field(..., description="ID duy nhất của thiết bị")
    device_name: Optional[str] = Field(None, description="Tên thiết bị")
    
    class Config:
        json_schema_extra = {
            "example": {
                "device_id": "device_12345",
                "device_name": "iPhone 15 Pro"
            }
        } 