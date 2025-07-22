from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from fastapi.security import HTTPBearer
from sqlalchemy.orm import Session
from schemas import survey as schemas
from crud import crud
from database import QuestionsSessionLocal, AnswersSessionLocal
from typing import List
import shutil
import os
from core.validation import validate_answer
from core.security import get_current_user, require_admin

router = APIRouter()
security = HTTPBearer()

# Dependency lấy session cho questions_db
def get_questions_db():
    db = QuestionsSessionLocal()
    try:
        yield db
    finally:
        db.close()

# Dependency lấy session cho answers_db
def get_answers_db():
    db = AnswersSessionLocal()
    try:
        yield db
    finally:
        db.close()

# Lấy danh sách câu hỏi cho user
@router.get("/questions", response_model=List[schemas.SurveyQuestionOut])
def get_questions(db: Session = Depends(get_questions_db)):
    return crud.get_all_questions(db)

# User gửi câu trả lời (nhiều câu hỏi cùng lúc)
@router.post("/submit", dependencies=[Depends(security)])
def submit_answers(payload: schemas.SurveySubmitRequest, db: Session = Depends(get_answers_db), qdb: Session = Depends(get_questions_db), user=Depends(get_current_user)):
    # Chỉ cho user đã đăng nhập gửi câu trả lời (user lấy từ JWT)
    # Có thể so khớp user_id trong token và payload nếu muốn tăng bảo mật
    errors = []
    questions = qdb.query(crud.models.SurveyQuestion).all()
    total_questions = len(questions)
    for ans in payload.answers:
        question = next((q for q in questions if q.id == ans.question_id), None)
        if not question:
            errors.append(f"Không tìm thấy câu hỏi với id {ans.question_id}")
            continue
        ok, err = validate_answer(question, ans.answer)
        if not ok:
            errors.append(err)
    if errors:
        raise HTTPException(status_code=400, detail=errors)
    # Chống spam: nếu user đã trả lời đủ số câu hỏi thì không cho trả lời lại
    success = crud.save_user_answers(db, payload.user_id, payload.answers, total_questions=total_questions)
    if not success:
        raise HTTPException(status_code=409, detail="User đã trả lời survey, không thể trả lời lại.")
    return {"message": "Answers submitted successfully"}

# Lấy câu trả lời của user
@router.get("/answers/{user_id}", response_model=List[schemas.SurveyAnswerOut], dependencies=[Depends(security)])
def get_answers(user_id: str, db: Session = Depends(get_answers_db), user=Depends(get_current_user)):
    # Chỉ cho user đã đăng nhập xem câu trả lời (có thể kiểm tra user_id == user["user_id"] nếu muốn)
    return crud.get_user_answers(db, user_id)

# Admin import câu hỏi từ file CSV
@router.post("/admin/import-questions", dependencies=[Depends(security)])
def import_questions(file: UploadFile = File(...), db: Session = Depends(get_questions_db), admin=Depends(require_admin)):
    # Chỉ cho admin import câu hỏi
    temp_path = f"temp_{file.filename}"
    with open(temp_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    try:
        crud.import_questions_from_csv(db, temp_path)
    finally:
        os.remove(temp_path)
    return {"message": "Questions imported successfully"}

@router.get("/admin/statistics", dependencies=[Depends(security)])
def survey_statistics(adb: Session = Depends(get_answers_db), admin=Depends(require_admin)):
    # Tổng số user đã trả lời survey (dựa vào user_id duy nhất trong survey_answers)
    user_count = adb.query(crud.models.SurveyAnswer.user_id).distinct().count()
    return {"total_users_submitted": user_count}

@router.get("/admin/question-stats/{question_id}", dependencies=[Depends(security)])
def question_statistics(question_id: int, adb: Session = Depends(get_answers_db), qdb: Session = Depends(get_questions_db), admin=Depends(require_admin)):
    # Thống kê đáp án cho 1 câu hỏi
    question = qdb.query(crud.models.SurveyQuestion).filter_by(id=question_id).first()
    if not question:
        raise HTTPException(status_code=404, detail="Không tìm thấy câu hỏi")
    answers = adb.query(crud.models.SurveyAnswer).filter_by(question_id=question_id).all()
    stats = {}
    if question.question_type in ["single_choice", "multiple_choice"]:
        # Đếm tần suất từng đáp án
        from collections import Counter
        all_answers = []
        for a in answers:
            if question.question_type == "single_choice":
                all_answers.append(a.answer)
            else:
                all_answers.extend(a.answer if isinstance(a.answer, list) else [])
        stats = dict(Counter(all_answers))
    elif question.question_type == "number":
        # Tính giá trị trung bình
        nums = []
        for a in answers:
            try:
                nums.append(float(a.answer))
            except Exception:
                pass
        if nums:
            stats = {"average": sum(nums)/len(nums), "count": len(nums)}
        else:
            stats = {"average": None, "count": 0}
    else:
        stats = {"count": len(answers)}
    return {"question_id": question_id, "question_text": question.question_text, "stats": stats} 