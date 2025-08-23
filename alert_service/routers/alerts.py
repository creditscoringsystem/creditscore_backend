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


@router.get(
    "/{user_id}",
    response_model=List[AlertOut],
    summary="Lấy danh sách cảnh báo của user",
    description=(
        "Mục đích: Trả về các cảnh báo liên quan đến điểm tín dụng của user, sắp theo thời gian giảm dần.\n\n"
        "Phản hồi: 200 trả về danh sách (có thể rỗng)."
    ),
    responses={
        200: {"description": "Danh sách cảnh báo"}
    },
)
def list_alerts(user_id: str, db: Session = Depends(get_db)):
    rows = (
        db.query(Alert)
        .filter(Alert.user_id == user_id)
        .order_by(Alert.created_at.desc())
        .all()
    )
    return rows


@router.post(
    "/on-score-updated",
    response_model=List[AlertOut],
    summary="Tạo cảnh báo khi điểm được cập nhật",
    description=(
        "Mục đích: Sinh cảnh báo dựa trên thay đổi điểm (tăng/giảm) và ngưỡng điểm mới.\n\n"
        "Yêu cầu: Body theo `ScoreUpdatedIn`.\n\n"
        "Phản hồi: 200 trả về danh sách cảnh báo đã tạo."
    ),
    responses={
        200: {"description": "Tạo cảnh báo thành công"}
    },
)
def on_score_updated(payload: ScoreUpdatedIn, db: Session = Depends(get_db)):
    alerts = _make_rules(payload)
    for a in alerts:
        db.add(a)
    db.commit()
    # refresh to return IDs
    for a in alerts:
        db.refresh(a)
    return alerts


@router.post(
    "/{alert_id}/read",
    response_model=MarkReadOut,
    summary="Đánh dấu đã đọc một cảnh báo",
    description=(
        "Mục đích: Đánh dấu trạng thái đã đọc cho alert theo `alert_id`.\n\n"
        "Phản hồi: 200 nếu thành công; 404 nếu không tìm thấy alert."
    ),
    responses={
        200: {"description": "Đã đánh dấu đã đọc"},
        404: {"description": "Không tìm thấy alert"},
    },
)
def mark_read(alert_id: int, db: Session = Depends(get_db)):
    row = db.query(Alert).filter(Alert.id == alert_id).first()
    if not row:
        raise HTTPException(status_code=404, detail="Alert not found")
    row.is_read = True
    db.commit()
    return {"success": True}


