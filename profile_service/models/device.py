from sqlalchemy import Column, Integer, String, DateTime, Boolean
from sqlalchemy.ext.declarative import declarative_base
import datetime
from.base import Base

class Device(Base):
    __tablename__ = "devices"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String(100), index=True, nullable=False)
    device_id = Column(String(100), nullable=False)
    device_name = Column(String(100), nullable=True)
    last_login = Column(DateTime, default=datetime.datetime.utcnow)
    is_active = Column(Boolean, default=True) 