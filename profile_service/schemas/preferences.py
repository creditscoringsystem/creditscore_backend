from pydantic import BaseModel, Field
from typing import List

class Preferences(BaseModel):
    theme: str = Field(
        default="light", 
        description="Giao diện (light/dark)",
        pattern="^(light|dark)$"
    )
    language: str = Field(
        default="vi", 
        description="Ngôn ngữ (vi/en)",
        pattern="^(vi|en)$"
    )
    notifications: List[str] = Field(
        default=["email"], 
        description="Danh sách loại thông báo được bật"
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "theme": "light",
                "language": "vi",
                "notifications": ["email", "sms", "push"]
            }
        } 