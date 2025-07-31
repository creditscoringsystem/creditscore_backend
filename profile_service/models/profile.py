from sqlalchemy import Column, Integer, String, DateTime, Date
import datetime
from .base import Base 

class Profile(Base):
    __tablename__ = "profiles"
    
    id = Column(Integer, primary_key=True)
    user_id = Column(String(100), unique=True, index=True, nullable=False)
    full_name = Column(String(100), nullable=True)
    email = Column(String(100), nullable=True)
    phone = Column(String(20), nullable=True)
    avatar = Column(String(255), nullable=True)
    date_of_birth = Column(Date, nullable=True)
    address = Column(String(500), nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)
    
    def __repr__(self):
        return f"<Profile(user_id='{self.user_id}', full_name='{self.full_name}')>" 