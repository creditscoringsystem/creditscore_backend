import datetime
from sqlalchemy import Column, Integer, String, DateTime, Boolean
from .base import Base


class Alert(Base):
    __tablename__ = "alerts"

    id = Column(Integer, primary_key=True)
    user_id = Column(String(100), index=True, nullable=False)
    type = Column(String(50), nullable=False)  # score_drop, score_rise, rank_up, tip
    title = Column(String(200), nullable=False)
    message = Column(String(1000), nullable=False)
    severity = Column(String(20), nullable=False)  # low, medium, high
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    is_read = Column(Boolean, default=False)


