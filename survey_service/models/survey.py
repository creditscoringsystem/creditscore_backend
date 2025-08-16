from sqlalchemy import Column, Integer, String, Text, DateTime, JSON, Boolean, ForeignKey
from sqlalchemy.orm import relationship
import datetime
from .base import Base

class SurveyQuestion(Base):
    __tablename__ = "survey_questions"
    id = Column(Integer, primary_key=True, index=True)
    question_text = Column(Text, nullable=False)
    question_type = Column(String(50), nullable=False)  # single_choice, multiple_choice, number, text
    question_group = Column(String(100), nullable=False)  # nhóm câu hỏi
    options = Column(JSON, nullable=True)  # list các lựa chọn nếu là trắc nghiệm
    order = Column(Integer, nullable=False)
    is_required = Column(Boolean, default=True, nullable=False)
    version = Column(Integer, default=1)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)
    
    answers = relationship(
        "SurveyAnswer",
        back_populates="question",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )

class SurveyAnswer(Base):
    __tablename__ = "survey_answers"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String(100), nullable=False)
    question_id = Column(Integer, ForeignKey("survey_questions.id", ondelete="CASCADE"), nullable=False)
    answer = Column(JSON, nullable=False)  # Có thể là text, số, list, v.v.
    submitted_at = Column(DateTime, default=datetime.datetime.utcnow)
    
    question = relationship("SurveyQuestion", back_populates="answers")

