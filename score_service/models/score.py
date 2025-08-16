import datetime
from sqlalchemy import Column, Integer, String, DateTime, Float
from models.base import Base


class CreditScore(Base):
    __tablename__ = "credit_scores"

    id = Column(Integer, primary_key=True)
    user_id = Column(String(100), index=True, nullable=False, unique=True)

    current_score = Column(Integer, nullable=False)
    category = Column(String(50), nullable=False)
    confidence = Column(Float, nullable=True)
    model_version = Column(String(64), nullable=True)
    last_calculated = Column(
        DateTime,
        default=datetime.datetime.utcnow,
        onupdate=datetime.datetime.utcnow,
    )


class ScoreHistory(Base):
    __tablename__ = "score_history"

    id = Column(Integer, primary_key=True)
    user_id = Column(String(100), index=True, nullable=False)
    score = Column(Integer, nullable=False)
    category = Column(String(50), nullable=False)
    confidence = Column(Float, nullable=True)
    model_version = Column(String(64), nullable=True)
    calculated_at = Column(DateTime, default=datetime.datetime.utcnow)


