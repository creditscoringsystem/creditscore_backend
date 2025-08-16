from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from models.alert import Alert
from schemas.alert import AlertOut, ScoreUpdatedIn, MarkReadOut
from database import get_db


router = APIRouter(prefix="/alerts", tags=["alerts"])


def _make_rules(payload: ScoreUpdatedIn) -> list[Alert]:
    alerts: list[Alert] = []
    delta = None
    if payload.old_score is not None:
        delta = payload.new_score - payload.old_score

    # Rule: tăng/giảm điểm mạnh
    if delta is not None and delta <= -10:
        alerts.append(
            Alert(
                user_id=payload.user_id,
                type="score_drop",
                severity="high",
                title="Điểm giảm mạnh",
                message=f"Điểm tín dụng giảm {abs(delta)} điểm. Hãy giảm tỷ lệ sử dụng tín dụng và thanh toán đúng hạn.",
            )
        )
    elif delta is not None and delta >= 10:
        alerts.append(
            Alert(
                user_id=payload.user_id,
                type="score_rise",
                severity="medium",
                title="Điểm cải thiện",
                message=f"Điểm tín dụng tăng {delta} điểm. Tiếp tục duy trì thói quen thanh toán tốt.",
            )
        )

    # Rule: tips theo ngưỡng điểm hiện tại
    if payload.new_score < 60:
        alerts.append(
            Alert(
                user_id=payload.user_id,
                type="tip",
                severity="medium",
                title="Gợi ý cải thiện",
                message="Giữ tỷ lệ sử dụng tín dụng dưới 30% và tránh mở thẻ mới trong giai đoạn này.",
            )
        )
    elif payload.new_score < 80:
        alerts.append(
            Alert(
                user_id=payload.user_id,
                type="tip",
                severity="low",
                title="Gợi ý duy trì",
                message="Giữ tỷ lệ sử dụng dưới 50% và thanh toán đúng hạn để tăng điểm bền vững.",
            )
        )
    else:
        alerts.append(
            Alert(
                user_id=payload.user_id,
                type="tip",
                severity="low",
                title="Tiếp tục duy trì",
                message="Điểm tốt. Tránh trễ hạn và theo dõi chi tiêu để giữ mức hiện tại.",
            )
        )

    return alerts


@router.get("/{user_id}", response_model=List[AlertOut], summary="List alerts for user")
def list_alerts(user_id: str, db: Session = Depends(get_db)):
    rows = (
        db.query(Alert)
        .filter(Alert.user_id == user_id)
        .order_by(Alert.created_at.desc())
        .all()
    )
    return rows


@router.post("/on-score-updated", response_model=List[AlertOut], summary="Create alerts when score updated")
def on_score_updated(payload: ScoreUpdatedIn, db: Session = Depends(get_db)):
    alerts = _make_rules(payload)
    for a in alerts:
        db.add(a)
    db.commit()
    # refresh to return IDs
    for a in alerts:
        db.refresh(a)
    return alerts


@router.post("/{alert_id}/read", response_model=MarkReadOut, summary="Mark alert as read")
def mark_read(alert_id: int, db: Session = Depends(get_db)):
    row = db.query(Alert).filter(Alert.id == alert_id).first()
    if not row:
        raise HTTPException(status_code=404, detail="Alert not found")
    row.is_read = True
    db.commit()
    return {"success": True}


