from sqlalchemy import Column, Integer, String, Boolean, DateTime
from datetime import datetime
from models.base import Base

class User(Base):
    __tablename__ = "users"
    __table_args__ = {'extend_existing': True}
    
    id = Column(Integer, primary_key=True)
    username = Column(String, unique=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    disabled = Column(Boolean, default=False)
    is_admin = Column(Boolean, default=False)
    reset_token = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f"<User(username='{self.username}', id={self.id})>"
