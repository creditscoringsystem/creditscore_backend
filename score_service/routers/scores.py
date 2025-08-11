from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from schemas.score import FeaturesIn, ScoreOut, HistoryOut, HistoryItem, SimulationOut
from database import get_db
from models.score import CreditScore, ScoreHistory
from services.ml_client import predict_score


router = APIRouter(prefix="/scores", tags=["scores"])



def to_category(score: int) -> str:
    if score >= 80:
        return "good"
    if score >= 60:
        return "average"
    return "poor"


@router.post("/{user_id}/calculate", response_model=ScoreOut)
async def calculate_score(user_id: str, payload: FeaturesIn, db: Session = Depends(get_db)):
    """Gọi ML để tính điểm và LƯU current + append history."""
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

    return ScoreOut(
        user_id=user_id,
        current_score=current.current_score,
        category=current.category,
        confidence=current.confidence,
        model_version=current.model_version,
        last_calculated=current.last_calculated,
    )


@router.get("/{user_id}", response_model=ScoreOut)
def get_current_score(user_id: str, db: Session = Depends(get_db)):
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


@router.get("/{user_id}/history", response_model=HistoryOut)
def get_history(user_id: str, db: Session = Depends(get_db)):
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


@router.post("/{user_id}/simulate", response_model=SimulationOut)
async def simulate(user_id: str, payload: FeaturesIn):
    """Gọi ML để mô phỏng, KHÔNG lưu DB."""
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


