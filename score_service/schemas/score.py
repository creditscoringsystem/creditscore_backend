from typing import Optional, List
from pydantic import BaseModel, Field
from datetime import datetime


class FeaturesIn(BaseModel):
    age: int = Field(..., ge=18, le=100)
    monthly_income: int = Field(..., ge=0)
    credit_usage_percent: float = Field(..., ge=0.0, le=100.0)
    late_payments_12m: int = Field(..., ge=0)
    credit_cards_count: int = Field(..., ge=0)


class SurveyAnswersIn(BaseModel):
    """Survey-form answers mapped to scoring rule labels.

    Each field expects one of the label strings defined by FE options.
    """

    age: str = Field(..., examples=["18-24", "25-34", "35-50", "51+"])
    income: str = Field(..., examples=["<5m", "5-10m", "10-20m", "20-50m", ">50m"])
    job_type: str = Field(..., examples=["freelance", "employee", "manager"])
    credit_cards: str = Field(..., examples=["0", "1", "2-3", "4+"])
    credit_usage: str = Field(..., examples=["<10%", "11-30%", "31-50%", "51-70%", ">70%"])
    pay_full_on_time: str = Field(..., examples=["yes", "sometimes", "no"])
    card_blocked: str = Field(..., examples=["no", "yes"])
    late_12m: str = Field(..., examples=["0", "1-2", "3-5", "6+"])
    pay_timing: str = Field(..., examples=["early", "on_time", "late"])
    late_fee: str = Field(..., examples=["no", "yes"])
    market_behavior: str = Field(..., examples=["hold", "invest_more", "withdraw"])
    willing_to_borrow: str = Field(..., examples=["yes", "maybe", "no"])
    urgent_money: str = Field(..., examples=["friends", "bank", "credit_card"])
    large_money_use: str = Field(..., examples=["invest", "save", "spend"])


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


