from sqlalchemy.orm import Session
from typing import List
from models import survey as models
from schemas import survey as schemas
import pandas as pd

# Lấy danh sách tất cả câu hỏi (theo thứ tự)
def get_all_questions(db: Session) -> List[models.SurveyQuestion]:
    return db.query(models.SurveyQuestion).order_by(models.SurveyQuestion.order).all()

# Tạo mới một câu hỏi
def create_question(db: Session, question: schemas.SurveyQuestionCreate) -> models.SurveyQuestion:
    db_question = models.SurveyQuestion(**question.dict())
    db.add(db_question)
    db.commit()
    db.refresh(db_question)
    return db_question

# Import câu hỏi từ file CSV (dùng pandas)
def import_questions_from_csv(db: Session, csv_path: str):
    df = pd.read_csv(csv_path)
    for _, row in df.iterrows():
        # Lưu ý: options phải là list dạng JSON hoặc phân tách bằng dấu ; trong file CSV
        options = None
        if 'options' in row and pd.notna(row['options']):
            try:
                options = eval(row['options']) if row['options'].startswith('[') else row['options'].split(';')
            except Exception:
                options = None
        question = models.SurveyQuestion(
            question_text=row['question_text'],
            question_type=row['question_type'],
            question_group=row['question_group'],
            options=options,
            order=int(row['order']),
            is_required=bool(row.get('is_required', 1)),
            version=int(row.get('version', 1))
        )
        db.add(question)
    db.commit()

def has_user_submitted(db: Session, user_id: str, total_questions: int) -> bool:
    # Trả về True nếu user đã trả lời đủ số câu hỏi (chống spam/trả lời lại)
    count = db.query(models.SurveyAnswer).filter_by(user_id=user_id).count()
    return count >= total_questions

# Lưu câu trả lời của user (chỉ cho phép trả lời 1 lần, nếu đã có thì cập nhật)
def save_user_answers(db: Session, user_id: str, answers: List[schemas.SurveyAnswerBase], total_questions: int = None):
    # Nếu user đã trả lời đủ số câu hỏi thì không cho trả lời lại (chống spam)
    if total_questions is not None:
        if has_user_submitted(db, user_id, int(total_questions)):
            # Nếu muốn cho phép cập nhật, có thể bỏ đoạn này
            return False
    for ans in answers:
        db_answer = db.query(models.SurveyAnswer).filter_by(user_id=user_id, question_id=ans.question_id).first()
        if db_answer:
            db_answer.answer = ans.answer
        else:
            db_answer = models.SurveyAnswer(user_id=user_id, question_id=ans.question_id, answer=ans.answer)
            db.add(db_answer)
    db.commit()
    return True

# Lấy tất cả câu trả lời của một user
def get_user_answers(db: Session, user_id: str) -> List[models.SurveyAnswer]:
    return db.query(models.SurveyAnswer).filter_by(user_id=user_id).all()
