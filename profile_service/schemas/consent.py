from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class ConsentOut(BaseModel):
    id: int = Field(..., description="ID duy nhất của consent")
    service: str = Field(..., description="Tên dịch vụ yêu cầu consent")
    scope: Optional[str] = Field(None, description="Phạm vi quyền được cấp")
    granted: bool = Field(..., description="Trạng thái đã được cấp quyền hay chưa")
    revoked_at: Optional[datetime] = Field(None, description="Thời gian thu hồi quyền")
    created_at: Optional[datetime] = Field(None, description="Thời gian tạo consent")
    
    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": 1,
                "service": "credit_score",
                "scope": "read_profile",
                "granted": True,
                "revoked_at": None,
                "created_at": "2024-01-01T00:00:00Z"
            }
        } 