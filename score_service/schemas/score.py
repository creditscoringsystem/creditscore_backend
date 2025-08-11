from typing import Optional, List
from pydantic import BaseModel, Field
from datetime import datetime


class FeaturesIn(BaseModel):
    age: int = Field(..., ge=18, le=100)
    monthly_income: int = Field(..., ge=0)
    credit_usage_percent: float = Field(..., ge=0.0, le=100.0)
    late_payments_12m: int = Field(..., ge=0)
    credit_cards_count: int = Field(..., ge=0)


class ScoreOut(BaseModel):
    user_id: str
    current_score: int
    category: str
    confidence: Optional[float] = None
    model_version: Optional[str] = None
    last_calculated: datetime


class HistoryItem(BaseModel):
    score: int
    category: str
    confidence: Optional[float] = None
    model_version: Optional[str] = None
    calculated_at: datetime


class HistoryOut(BaseModel):
    user_id: str
    history: List[HistoryItem]


class SimulationOut(BaseModel):
    score: int
    category: str
    confidence: Optional[float] = None
    model_version: Optional[str] = None


