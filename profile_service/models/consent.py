from sqlalchemy import Column, Integer, String, DateTime, Boolean
import datetime
from .base import Base

class Consent(Base):
    __tablename__ = "consents"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String(100), index=True, nullable=False)
    service = Column(String(100), nullable=False)
    scope = Column(String(255), nullable=True)
    granted = Column(Boolean, default=True)
    revoked_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow) 