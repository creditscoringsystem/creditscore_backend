from pydantic import BaseModel
from typing import Optional

class ConsentOut(BaseModel):
    id: int
    service: str
    scope: Optional[str]
    granted: bool
    revoked_at: Optional[str]
    created_at: Optional[str]
    class Config:
        orm_mode = True 