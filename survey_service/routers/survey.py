from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, status, Body
from sqlalchemy.orm import Session
from schemas import survey as schemas
from crud import crud
from database import SessionLocal
from typing import List
import shutil
import os
from core.validation import validate_answer
from core.security import get_current_user, require_admin

# Gợi ý rõ ràng cho Swagger: không yêu cầu auth ở DEV mode

router = APIRouter(prefix="/survey", tags=["survey"])

# Dependency lấy session cho questions_db
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Lấy danh sách câu hỏi cho user
@router.get(
    
    "/questions",
    response_model=List[schemas.SurveyQuestionOut],
    summary="List all survey questions",
    description="Trả về toàn bộ câu hỏi theo thứ tự `order`. Dùng để render form khảo sát ở client.",
)
def get_questions(db: Session = Depends(get_db)):
    """Lấy danh sách câu hỏi khảo sát (đủ trường và metadata)."""
    return crud.get_all_questions(db)

# User gửi câu trả lời (nhiều câu hỏi cùng lúc)
@router.post(
    "/submit",
    status_code=status.HTTP_200_OK,
    summary="Submit all answers at once",
    description=(
        "User gửi toàn bộ câu trả lời. Hệ thống sẽ validate theo loại câu hỏi.\n"
        "Cơ chế chống spam: nếu đã trả lời đủ số câu hỏi, lần gửi sau sẽ bị từ chối (409)."
    ),
    responses={
        200: {"description": "Answers submitted successfully"},
        400: {"description": "Validation failed"},
        409: {"description": "User đã trả lời đủ, không thể gửi lại"},
    },
)
def submit_answers(
    payload: schemas.SurveySubmitRequest = Body(
        ...,
        examples={
            "simple": {
                "summary": "Ví dụ submit",
                "value": {
                    "user_id": "user_123",
                    "answers": [
                        {"question_id": 1, "answer": "Nam"},
                        {"question_id": 2, "answer": ["Thẻ tín dụng", "Vay tiêu dùng"]},
                        {"question_id": 3, "answer": 27},
                    ],
                },
            }
        },
    ),
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
):
    # Chỉ cho user đã đăng nhập gửi câu trả lời (user lấy từ JWT)
    # Có thể so khớp user_id trong token và payload nếu muốn tăng bảo mật
    errors = []
    questions = db.query(crud.models.SurveyQuestion).all()
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
@router.get(
    "/answers/{user_id}",
    response_model=List[schemas.SurveyAnswerOut],
    summary="Get user's answers",
    description="Trả về toàn bộ câu trả lời của một user (phục vụ resume hoặc hiển thị lại).",
)
def get_answers(user_id: str, db: Session = Depends(get_db), user=Depends(get_current_user)):
    # Chỉ cho user đã đăng nhập xem câu trả lời (có thể kiểm tra user_id == user["user_id"] nếu muốn)
    return crud.get_user_answers(db, user_id)

# Admin import câu hỏi từ file CSV
@router.post(
    "/admin/import-questions",
    status_code=status.HTTP_200_OK,
    summary="Admin import survey questions from CSV/Excel",
    description=(
        "File chấp nhận: .csv/.xlsx.\n\n"
        "Cột bắt buộc: question_text, question_type, question_group, order.\n"
        "Cột tuỳ chọn: options, is_required, version.\n"
        "CSV: hệ thống tự dò delimiter và encoding."
    ),
)
def import_questions(
    file: UploadFile = File(..., description="CSV hoặc Excel (.xlsx) chứa danh sách câu hỏi"),
    db: Session = Depends(get_db),
    admin=Depends(require_admin),
):
    # Chỉ cho admin import câu hỏi
    temp_path = f"temp_{file.filename}"
    with open(temp_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    try:
        crud.import_questions_from_csv(db, temp_path)
    finally:
        os.remove(temp_path)
    return {"message": "Questions imported successfully"}

@router.get(
    "/admin/statistics",
    summary="Admin - overall survey statistics",
    description="Số lượng user đã có ít nhất một câu trả lời (distinct theo user_id).",
)
def survey_statistics(db: Session = Depends(get_db), admin=Depends(require_admin)):
    # Tổng số user đã trả lời survey (dựa vào user_id duy nhất trong survey_answers)
    user_count = db.query(crud.models.SurveyAnswer.user_id).distinct().count()
    return {"total_users_submitted": user_count}

@router.get(
    "/admin/question-stats/{question_id}",
    summary="Admin - statistics for a specific question",
    description=(
        "Thống kê tuỳ theo loại câu hỏi: \n"
        "- single_choice/multiple_choice: tần suất các đáp án\n"
        "- number: trung bình và số lượng\n"
        "- text: tổng số câu trả lời"
    ),
)
def question_statistics(question_id: int, db: Session = Depends(get_db), admin=Depends(require_admin)):
    # Thống kê đáp án cho 1 câu hỏi
    question = db.query(crud.models.SurveyQuestion).filter_by(id=question_id).first()
    if not question:
        raise HTTPException(status_code=404, detail="Không tìm thấy câu hỏi")
    answers = db.query(crud.models.SurveyAnswer).filter_by(question_id=question_id).all()
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

@router.patch(
    "/answer",
    summary="Save or update a single answer (resume)",
    description=(
        "Lưu một câu trả lời đơn lẻ, phục vụ resume. Nếu đã tồn tại sẽ cập nhật, không áp dụng chặn spam theo tổng số."
    ),
)
def save_single_answer(
    payload: schemas.SurveyAnswerBase = Body(
        ...,
        examples={
            "single": {
                "summary": "Ví dụ lưu một câu",
                "value": {"user_id": "user_123", "question_id": 2, "answer": ["Thẻ tín dụng"]},
            }
        },
    ),
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
):
    # Validate câu hỏi tồn tại
    question = db.query(crud.models.SurveyQuestion).filter_by(id=payload.question_id).first()
    if not question:
        raise HTTPException(status_code=404, detail=f"Không tìm thấy câu hỏi với id {payload.question_id}")
    ok, err = validate_answer(question, payload.answer)
    if not ok:
        raise HTTPException(status_code=400, detail=err)
    # Lưu hoặc cập nhật câu trả lời
    success = crud.save_user_answers(db, payload.user_id, [payload])
    if not success:
        raise HTTPException(status_code=409, detail="Không thể lưu câu trả lời.")
    return {"message": "Answer saved successfully"}

@router.get(
    "/progress/{user_id}",
    summary="Get survey progress for a user",
    description="Trả về danh sách câu đã trả lời, còn thiếu và tổng số câu hỏi để client hiển thị tiến độ.",
)
def get_survey_progress(user_id: str, db: Session = Depends(get_db), user=Depends(get_current_user)):
    # Lấy tất cả câu hỏi
    questions = db.query(crud.models.SurveyQuestion).all()
    question_ids = set(q.id for q in questions)
    # Lấy tất cả câu đã trả lời
    answers = db.query(crud.models.SurveyAnswer).filter_by(user_id=user_id).all()
    answered_ids = set(a.question_id for a in answers)
    missing_ids = list(question_ids - answered_ids)
    return {
        "answered": list(answered_ids),
        "missing": missing_ids,
        "total": len(question_ids)
    } 