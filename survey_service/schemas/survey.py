from typing import List, Optional, Any
from pydantic import BaseModel, Field
import datetime

class SurveyQuestionBase(BaseModel):
    question_text: str
    question_type: str  # single_choice, multiple_choice, number, text
    question_group: str
    options: Optional[List[str]] = None  # Chỉ dùng cho trắc nghiệm
    order: int
    is_required: bool = True
    version: int = 1

class SurveyQuestionCreate(SurveyQuestionBase):
    pass

class SurveyQuestionOut(SurveyQuestionBase):
    id: int
    created_at: datetime.datetime
    updated_at: datetime.datetime

    class Config:
        from_attributes = True

class SurveyAnswerBase(BaseModel):
    user_id: str
    question_id: int
    answer: Any  # Có thể là str, int, list, v.v.

class SurveyAnswerCreate(SurveyAnswerBase):
    pass

class SurveyAnswerOut(SurveyAnswerBase):
    id: int
    submitted_at: datetime.datetime

    class Config:
        from_attributes = True

# Schema cho request gửi nhiều câu trả lời một lúc
class SurveySubmitRequest(BaseModel):
    user_id: str
    answers: List[SurveyAnswerBase] 