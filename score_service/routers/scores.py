from fastapi import APIRouter, Depends, HTTPException, Body
from sqlalchemy.orm import Session
from typing import List
from schemas.score import FeaturesIn, ScoreOut, HistoryOut, HistoryItem, SimulationOut
from database import get_db
from models.score import CreditScore, ScoreHistory
from services.ml_client import predict_score
from services.alert_client import notify_score_updated


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
        "Gọi ML service để tính điểm từ features và LƯU vào DB: \n"
        "- Cập nhật điểm hiện tại (upsert vào bảng `credit_scores`)\n"
        "- Ghi thêm một bản ghi vào `score_history` để phục vụ vẽ trend\n\n"
        "Dùng sau khi user hoàn thành Survey hoặc khi bấm 'Áp dụng thay đổi' ở What-If."
    ),
    responses={
        200: {"description": "Tính và lưu điểm thành công"},
        502: {"description": "Không gọi được ML service"},
    },
)
async def calculate_score(
    user_id: str,
    payload: FeaturesIn = Body(
        ...,
        examples={
            "demo": {
                "summary": "Ví dụ features tối giản",
                "value": {
                    "age": 28,
                    "monthly_income": 15000000,
                    "credit_usage_percent": 42.5,
                    "late_payments_12m": 1,
                    "credit_cards_count": 2,
                },
            }
        },
    ),
    db: Session = Depends(get_db),
):
    """Upsert điểm hiện tại và thêm lịch sử tính điểm cho `user_id`."""
    try:
        ml_resp = await predict_score(payload.model_dump())
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"ML service error: {e}")

    score_val = int(ml_resp.get("score", 0))
    category = ml_resp.get("category") or to_category(score_val)
    confidence = ml_resp.get("confidence")
    model_version = ml_resp.get("model_version")

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
        "Gọi ML service với features để tính thử điểm dự kiến, KHÔNG lưu DB.\n"
        "Dùng khi kéo slider What-If trên FE."
    ),
    responses={
        200: {"description": "Mô phỏng thành công (không lưu)"},
        502: {"description": "Không gọi được ML service"},
    },
)
async def simulate(
    user_id: str,
    payload: FeaturesIn = Body(
        ...,
        examples={
            "what_if": {
                "summary": "Ví dụ mô phỏng với credit usage thấp hơn",
                "value": {
                    "age": 28,
                    "monthly_income": 15000000,
                    "credit_usage_percent": 25.0,
                    "late_payments_12m": 0,
                    "credit_cards_count": 2,
                },
            }
        },
    ),
):
    """Mô phỏng điểm tín dụng cho `user_id` mà không ghi lịch sử/điểm hiện tại."""
    try:
        ml_resp = await predict_score(payload.model_dump())
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"ML service error: {e}")

    score_val = int(ml_resp.get("score", 0))
    category = ml_resp.get("category") or to_category(score_val)
    confidence = ml_resp.get("confidence")
    model_version = ml_resp.get("model_version")
    return SimulationOut(
        score=score_val,
        category=category,
        confidence=confidence,
        model_version=model_version,
    )


