from pydantic import BaseModel
from typing import List

class Preferences(BaseModel):
    theme: str = "light"
    language: str = "vi"
    notifications: List[str] = ["email"] 