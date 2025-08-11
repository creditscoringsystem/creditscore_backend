from typing import List
from pydantic import BaseModel
from datetime import datetime


class AlertOut(BaseModel):
    id: int
    user_id: str
    type: str
    title: str
    message: str
    severity: str
    created_at: datetime
    is_read: bool

    class Config:
        from_attributes = True


class ScoreUpdatedIn(BaseModel):
    user_id: str
    old_score: int | None = None
    new_score: int
    category: str | None = None
    model_version: str | None = None
    calculated_at: datetime | None = None


class MarkReadOut(BaseModel):
    success: bool


