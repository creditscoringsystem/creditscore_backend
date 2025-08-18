from fastapi import APIRouter, Depends, HTTPException, Body
from sqlalchemy.orm import Session
from typing import List
from schemas.score import (
    SurveyAnswersIn,
    ScoreOut,
    HistoryOut,
    HistoryItem,
    SimulationOut,
)
from database import get_db
from models.score import CreditScore, ScoreHistory
from services.alert_client import notify_score_updated
from services.rule_scoring import compute_rule_based_score


router = APIRouter(prefix="/scores", tags=["scores"])



def to_category(score: int) -> str:
    if score >= 80:
        return "good"
    if score >= 60:
        return "average"
    return "poor"


@router.post(
    "/{user_id}/calculate",
    response_model=ScoreOut,
    summary="Calculate and persist user's credit score",
    description=(
        "Tính điểm theo RULES từ câu trả lời Survey và LƯU vào DB: \n"
        "- Cập nhật điểm hiện tại (upsert vào bảng `credit_scores`)\n"
        "- Ghi thêm một bản ghi vào `score_history` để phục vụ vẽ trend\n\n"
        "Dùng sau khi user hoàn thành Survey hoặc khi bấm 'Áp dụng thay đổi' ở What-If."
    ),
    responses={
        200: {"description": "Tính và lưu điểm thành công"},
    },
)
async def calculate_score(
    user_id: str,
    payload: SurveyAnswersIn = Body(
        ...,
        examples={
            "survey_demo": {
                "summary": "Ví dụ câu trả lời survey",
                "value": {
                    "age": "25-34",
                    "income": "10-20m",
                    "job_type": "employee",
                    "credit_cards": "2-3",
                    "credit_usage": "31-50%",
                    "pay_full_on_time": "yes",
                    "card_blocked": "no",
                    "late_12m": "1-2",
                    "pay_timing": "on_time",
                    "late_fee": "no",
                    "market_behavior": "invest_more",
                    "willing_to_borrow": "maybe",
                    "urgent_money": "bank",
                    "large_money_use": "invest",
                },
            }
        },
    ),
    db: Session = Depends(get_db),
):
    """Upsert điểm hiện tại và thêm lịch sử tính điểm cho `user_id` theo RULES."""
    result = compute_rule_based_score(payload.model_dump())

    score_val = int(result.get("score", 0))
    category = result.get("category") or to_category(score_val)
    confidence = result.get("confidence")
    model_version = result.get("model_version")

    # upsert current
    current = db.query(CreditScore).filter(CreditScore.user_id == user_id).first()
    if current is None:
        current = CreditScore(
            user_id=user_id,
            current_score=score_val,
            category=category,
            confidence=confidence,
            model_version=model_version,
        )
        db.add(current)
    else:
        old_score_val = current.current_score
        current.current_score = score_val
        current.category = category
        current.confidence = confidence
        current.model_version = model_version

    # append history
    hist = ScoreHistory(
        user_id=user_id,
        score=score_val,
        category=category,
        confidence=confidence,
        model_version=model_version,
    )
    db.add(hist)
    db.commit()
    db.refresh(current)

    # notify alerts (fire-and-forget)
    try:
        await notify_score_updated(
            user_id=user_id,
            old_score=locals().get("old_score_val"),
            new_score=current.current_score,
            category=current.category,
            model_version=current.model_version,
            calculated_at=current.last_calculated.isoformat(),
        )
    except Exception:
        pass

    return ScoreOut(
        user_id=user_id,
        current_score=current.current_score,
        category=current.category,
        confidence=current.confidence,
        model_version=current.model_version,
        last_calculated=current.last_calculated,
    )


@router.get(
    "/{user_id}",
    response_model=ScoreOut,
    summary="Get user's current credit score",
    description=(
        "Trả về điểm hiện tại đã lưu trong bảng `credit_scores`.\n"
        "404 nếu user chưa từng được tính điểm."
    ),
    responses={
        200: {"description": "Lấy điểm hiện tại thành công"},
        404: {"description": "Chưa có điểm cho user"},
    },
)
def get_current_score(user_id: str, db: Session = Depends(get_db)):
    """Lấy điểm hiện tại từ DB cho `user_id`."""
    current = db.query(CreditScore).filter(CreditScore.user_id == user_id).first()
    if current is None:
        raise HTTPException(status_code=404, detail="Score not found")
    return ScoreOut(
        user_id=user_id,
        current_score=current.current_score,
        category=current.category,
        confidence=current.confidence,
        model_version=current.model_version,
        last_calculated=current.last_calculated,
    )


@router.get(
    "/{user_id}/history",
    response_model=HistoryOut,
    summary="Get user's score history",
    description=(
        "Trả về danh sách các lần tính điểm (mới nhất trước) từ bảng `score_history`\n"
        "để FE vẽ biểu đồ xu hướng."
    ),
)
def get_history(user_id: str, db: Session = Depends(get_db)):
    """Lấy lịch sử tính điểm cho `user_id`."""
    rows: List[ScoreHistory] = (
        db.query(ScoreHistory)
        .filter(ScoreHistory.user_id == user_id)
        .order_by(ScoreHistory.calculated_at.desc())
        .all()
    )
    history = [
        HistoryItem(
            score=r.score,
            category=r.category,
            confidence=r.confidence,
            model_version=r.model_version,
            calculated_at=r.calculated_at,
        )
        for r in rows
    ]
    return HistoryOut(user_id=user_id, history=history)


@router.post(
    "/{user_id}/simulate",
    response_model=SimulationOut,
    summary="Simulate (What-If) without saving",
    description=(
        "Tính thử điểm dự kiến bằng RULES từ Survey, KHÔNG lưu DB.\n"
        "Dùng khi kéo slider What-If trên FE."
    ),
    responses={
        200: {"description": "Mô phỏng thành công (không lưu)"},
    },
)
async def simulate(
    user_id: str,
    payload: SurveyAnswersIn = Body(
        ...,
        examples={
            "what_if_rules": {
                "summary": "Ví dụ mô phỏng bằng RULES",
                "value": {
                    "age": "25-34",
                    "income": "10-20m",
                    "job_type": "employee",
                    "credit_cards": "2-3",
                    "credit_usage": "11-30%",
                    "pay_full_on_time": "yes",
                    "card_blocked": "no",
                    "late_12m": "0",
                    "pay_timing": "on_time",
                    "late_fee": "no",
                    "market_behavior": "hold",
                    "willing_to_borrow": "maybe",
                    "urgent_money": "bank",
                    "large_money_use": "save",
                },
            }
        },
    ),
):
    """Mô phỏng điểm tín dụng theo RULES (không lưu DB)."""
    result = compute_rule_based_score(payload.model_dump())

    score_val = int(result.get("score", 0))
    category = result.get("category") or to_category(score_val)
    confidence = result.get("confidence")
    model_version = result.get("model_version")
    return SimulationOut(
        score=score_val,
        category=category,
        confidence=confidence,
        model_version=model_version,
    )


