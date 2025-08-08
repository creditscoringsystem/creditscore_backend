from sqlalchemy.orm import Session
from typing import List, Optional
from models import survey as models
from schemas import survey as schemas
import pandas as pd
import os

# Lấy danh sách tất cả câu hỏi (theo thứ tự)
def get_all_questions(db: Session) -> List[models.SurveyQuestion]:
    return db.query(models.SurveyQuestion).order_by(models.SurveyQuestion.order).all()

# Tạo mới một câu hỏi
def create_question(db: Session, question: schemas.SurveyQuestionCreate) -> models.SurveyQuestion:
    db_question = models.SurveyQuestion(**question.model_dump())
    db.add(db_question)
    db.commit()
    db.refresh(db_question)
    return db_question

# Import câu hỏi từ file CSV (dùng pandas)
def import_questions_from_csv(db: Session, csv_path: str):
    # Hỗ trợ CSV hoặc Excel; kiểm tra phần mở rộng
    _, ext = os.path.splitext(csv_path.lower())

    if ext in [".csv", ".txt"]:
        # Đọc CSV với fallback encoding và auto-detect delimiter
        encodings_to_try = ["utf-8", "utf-8-sig", "latin1"]
        last_err: Exception | None = None
        df = None
        for enc in encodings_to_try:
            try:
                df = pd.read_csv(csv_path, encoding=enc, sep=None, engine="python")
                break
            except Exception as e:  # broad intentionally for parsing robustness
                last_err = e
                continue
        if df is None:
            raise ValueError(
                f"Failed to read CSV. Ensure the file is a valid CSV. Last error: {last_err}"
            )
    elif ext in [".xlsx", ".xls"]:
        try:
            df = pd.read_excel(csv_path)
        except Exception as e:
            raise ValueError(f"Failed to read Excel file: {e}")
    else:
        raise ValueError("Unsupported file type. Please upload a CSV or Excel (.xlsx) file.")

    # Chuẩn hoá tên cột
    df.columns = [str(c).strip().lower() for c in df.columns]

    required_cols = ["question_text", "question_type", "question_group", "order"]
    missing = [c for c in required_cols if c not in df.columns]
    if missing:
        raise ValueError(
            "Missing required columns: "
            + ", ".join(missing)
            + ". Expected header: question_text,question_type,question_group,options,order,is_required,version"
        )
    for _, row in df.iterrows():
        # Lưu ý: options phải là list dạng JSON hoặc phân tách bằng dấu ; trong file CSV
        options = None
        if 'options' in row and pd.notna(row['options']):
            try:
                text = str(row['options'])
                if text.strip().startswith('['):
                    import ast
                    options = ast.literal_eval(text)
                else:
                    options = text.split(';')
            except Exception:
                options = None
        question = models.SurveyQuestion(
            question_text=str(row['question_text']).strip(),
            question_type=str(row['question_type']).strip(),
            question_group=str(row['question_group']).strip(),
            options=options,
            order=int(row['order']),
            is_required=bool(int(row['is_required'])) if 'is_required' in row and pd.notna(row['is_required']) else True,
            version=int(row['version']) if 'version' in row and pd.notna(row['version']) else 1,
        )
        db.add(question)
    db.commit()

def has_user_submitted(db: Session, user_id: str, total_questions: int) -> bool:
    # Trả về True nếu user đã trả lời đủ số câu hỏi (chống spam/trả lời lại)
    answered_distinct_questions = (
        db.query(models.SurveyAnswer.question_id)
        .filter_by(user_id=user_id)
        .distinct()
        .count()
    )
    return answered_distinct_questions >= total_questions

# Lưu câu trả lời của user (chỉ cho phép trả lời 1 lần, nếu đã có thì cập nhật)
def save_user_answers(db: Session, user_id: str, answers: List[schemas.SurveyAnswerBase], total_questions: Optional[int] = None):
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
