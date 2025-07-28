from pydantic import BaseModel, Field

class Preferences(BaseModel):
    theme: str = Field(
        default="light",
        description="Theme giao diện",
        pattern=r"^(light|dark|auto)$"
    )
    language: str = Field(
        default="vi", 
        description="Ngôn ngữ giao diện",
        pattern=r"^(vi|en|zh)$"
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "theme": "light",
                "language": "vi"
            }
        } 