from fastapi import APIRouter, Depends, HTTPException, Body
from sqlalchemy.orm import Session
from typing import List
from schemas.score import (
    SurveyAnswersIn,
    ScoreOut,
    HistoryOut,
    HistoryItem,
    SimulationOut,
    ProjectionOut,
    FactorsOut,
    FactorItem,
    RecommendationItem,
)
from database import get_db
from models.score import CreditScore, ScoreHistory
from services.alert_client import notify_score_updated
from services.rule_scoring import compute_rule_based_score, ui_from_fico, SURVEY_RULES


router = APIRouter(prefix="/scores", tags=["scores"])


def to_category(score: int) -> str:
    """Fallback category mapping for a FICO-like score (300-850)."""
    if score >= 800:
        return "exceptional"
    if score >= 740:
        return "very_good"
    if score >= 670:
        return "good"
    if score >= 580:
        return "fair"
    return "poor"


def _validate_labels(payload: SurveyAnswersIn):
    """Validate that each provided label exists in SURVEY_RULES options.

    Raise HTTPException 422 on invalid label, with explicit field message.
    """
    data = payload.model_dump()
    for field, options in SURVEY_RULES.items():
        if field not in data:
            # Pydantic already enforces presence; keep defensive
            raise HTTPException(status_code=422, detail=f"Missing field: {field}")
        val = str(data[field])
        if val not in options:
            valid = ", ".join(options.keys())
            raise HTTPException(
                status_code=422,
                detail=f"Invalid label for '{field}': '{val}'. Expected one of: {valid}"
            )


def _build_factors_and_recos(category: str, fico: int):
    """Construct a simple, category-driven factor breakdown and recommendations.

    Since we don't persist survey answers, we infer typical drivers from the
    current score category. We keep weights summing ~1.0 and set 'score' as
    normalized user score on 0..1 to help UI visualization.
    """
    norm = max(0.0, min(1.0, (fico - 300) / 550))
    # Define base factors and their intended impact by category
    factors_cfg = [
        ("Payment history", 0.35, "Positive" if category in ("good", "very_good", "exceptional") else ("Negative" if category in ("poor", "fair") else "Neutral"),
         "Tỷ lệ thanh toán đúng hạn ảnh hưởng lớn nhất đến điểm tín dụng."),
        ("Credit utilization", 0.30, "Positive" if category in ("very_good", "exceptional") else ("Negative" if category in ("poor", "fair") else "Neutral"),
         "Giữ mức sử dụng thẻ <30% giúp cải thiện điểm đáng kể."),
        ("Recent late payments (12m)", 0.20, "Negative" if category in ("poor", "fair") else ("Neutral" if category == "good" else "Positive"),
         "Các khoản trễ hạn gần đây làm giảm điểm mạnh."),
        ("Credit mix & cards", 0.10, "Neutral" if category in ("good",) else ("Negative" if category in ("poor", "fair") else "Positive"),
         "Đa dạng hóa và duy trì thẻ ở trạng thái tốt."),
        ("Account tenure", 0.05, "Positive" if category in ("very_good", "exceptional") else "Neutral",
         "Tuổi tài khoản lâu năm thể hiện lịch sử tín dụng tốt."),
    ]

    factors = [
        FactorItem(name=n, weight=w, score=round(norm, 3), impact=imp, description=desc)
        for (n, w, imp, desc) in factors_cfg
    ]

    # Recommendations tailored by category band
    if category in ("poor", "fair"):
        recos = [
            RecommendationItem(title="Thanh toán đúng hạn 100% trong 3–6 tháng tới", detail="Thiết lập nhắc lịch/auto-pay để tránh trễ hạn."),
            RecommendationItem(title="Giảm sử dụng hạn mức xuống <30%", detail="Trả bớt dư nợ thẻ hoặc tăng hạn mức hợp lý."),
            RecommendationItem(title="Tránh phí phạt và nợ quá hạn", detail="Theo dõi sao kê hàng tháng, xử lý ngay khi phát sinh."),
        ]
    elif category == "good":
        recos = [
            RecommendationItem(title="Duy trì thanh toán đầy đủ và đúng hạn", detail="Bảo toàn lịch sử tốt để lên Very Good."),
            RecommendationItem(title="Hạ sử dụng thẻ về 10–20%", detail="Chia nhỏ chi tiêu qua tháng hoặc trả thêm sớm."),
        ]
    else:  # very_good / exceptional
        recos = [
            RecommendationItem(title="Tiếp tục giữ kỷ luật tài chính", detail="Duy trì sử dụng thấp và không trễ hạn."),
            RecommendationItem(title="Hạn chế mở tài khoản mới không cần thiết", detail="Tránh hard inquiry không cần thiết."),
        ]

    return factors, recos


@router.get(
    "/{user_id}/factors",
    response_model=FactorsOut,
    summary="Lấy yếu tố ảnh hưởng & khuyến nghị",
    description=(
        "Mục đích: Cung cấp breakdown các yếu tố ảnh hưởng tới điểm và gợi ý cải thiện cho Dashboard.\n\n"
        "Điều kiện: User phải có điểm hiện tại trong DB.\n\n"
        "Phản hồi: 200 trả về danh sách yếu tố và khuyến nghị; 404 nếu chưa có dữ liệu điểm."
    ),
    responses={
        200: {"description": "OK"},
        404: {"description": "Chưa có điểm cho user"},
    },
)
def get_factors(user_id: str, db: Session = Depends(get_db)):
    current = db.query(CreditScore).filter(CreditScore.user_id == user_id).first()
    if current is None:
        raise HTTPException(status_code=404, detail="Score not found")

    fico = int(current.current_score)
    category = current.category or to_category(fico)
    factors, recos = _build_factors_and_recos(category, fico)
    return FactorsOut(user_id=user_id, factors=factors, recommendations=recos)


@router.post(
    "/{user_id}",
    response_model=ScoreOut,
    summary="Tính và lưu điểm tín dụng người dùng",
    description=(
        "Mục đích: Tính điểm theo RULES từ câu trả lời Survey và lưu kết quả vào DB.\n\n"
        "Hành động:\n"
        "- Upsert điểm hiện tại vào `credit_scores`.\n"
        "- Ghi thêm bản ghi vào `score_history` để vẽ xu hướng.\n\n"
        "Sử dụng: Sau khi user hoàn thành Survey hoặc bấm 'Áp dụng thay đổi' ở What-If."
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

    prev = locals().get("old_score_val")
    delta = (current.current_score - prev) if isinstance(prev, int) else None
    return ScoreOut(
        user_id=user_id,
        current_score=current.current_score,
        category=current.category,
        confidence=current.confidence,
        model_version=current.model_version,
        last_calculated=current.last_calculated,
        category_display=result.get("category_display"),
        percentile=result.get("percentile"),
        band_color=result.get("band_color"),
        band_min=result.get("band_min"),
        band_max=result.get("band_max"),
        previous_score=prev,
        delta=delta,
    )


@router.get(
    "/{user_id}",
    response_model=ScoreOut,
    summary="Lấy điểm tín dụng hiện tại",
    description=(
        "Mục đích: Trả về điểm hiện tại đã lưu trong bảng `credit_scores`.\n\n"
        "Phản hồi: 200 nếu có điểm; 404 nếu user chưa từng được tính điểm."
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
    ui = ui_from_fico(current.current_score)
    return ScoreOut(
        user_id=user_id,
        current_score=current.current_score,
        category=current.category,
        confidence=current.confidence,
        model_version=current.model_version,
        last_calculated=current.last_calculated,
        category_display=ui.get("category_display"),
        percentile=ui.get("percentile"),
        band_color=ui.get("band_color"),
        band_min=ui.get("band_min"),
        band_max=ui.get("band_max"),
    )


@router.get(
    "/{user_id}/history",
    response_model=HistoryOut,
    summary="Lấy lịch sử tính điểm",
    description=(
        "Mục đích: Trả về danh sách các lần tính điểm (mới nhất trước) từ bảng `score_history` để FE vẽ biểu đồ xu hướng.\n\n"
        "Phản hồi: 200 trả về danh sách (có thể rỗng)."
    ),
    responses={
        200: {"description": "Lấy lịch sử tính điểm thành công"}
    },
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
    summary="Mô phỏng (What‑If) không lưu",
    description=(
        "Mục đích: Tính thử điểm dự kiến theo RULES từ Survey, không ghi vào DB.\n\n"
        "Sử dụng: Khi người dùng điều chỉnh What‑If trên FE."
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
        category_display=result.get("category_display"),
        percentile=result.get("percentile"),
        band_color=result.get("band_color"),
        band_min=result.get("band_min"),
        band_max=result.get("band_max"),
    )



@router.post(
    "/{user_id}/simulate/projection",
    response_model=ProjectionOut,
    summary="Mô phỏng projection theo tháng (không lưu)",
    description=(
        "Mục đích: Trả về snapshot và chuỗi projection theo tháng, không ghi vào DB.\n\n"
        "Yêu cầu: Body theo `SurveyAnswersIn` (flat) giống endpoint simulate.\n\n"
        "Phản hồi: 200 trả về snapshot + projection; 422 nếu schema sai hoặc label không hợp lệ."
    ),
    responses={
        200: {"description": "Trả về snapshot + projection"},
        422: {"description": "Sai schema hoặc label không hợp lệ"},
    },
)
async def simulate_projection(
    user_id: str,
    payload: SurveyAnswersIn = Body(...),
    db: Session = Depends(get_db),
):
    """Mô phỏng snapshot và chuỗi projection theo tháng cho What-If."""
    # Validate labels strictly against SURVEY_RULES
    _validate_labels(payload)

    # Compute simulated snapshot
    sim_result = compute_rule_based_score(payload.model_dump())
    simulated_score = int(sim_result.get("score", 0))
    category = sim_result.get("category") or to_category(simulated_score)
    confidence_0_1 = sim_result.get("confidence")  # may be None

    # Baseline current score from DB if exists; else use simulated as fallback
    current = db.query(CreditScore).filter(CreditScore.user_id == user_id).first()
    current_score = int(current.current_score) if current else simulated_score

    # Build 12-month projection; simple constant path with uncertainty band
    months = 12
    # derive a confidence pct for summary (0..100); default 70 if None
    confidence_pct = int(round((confidence_0_1 if isinstance(confidence_0_1, (int, float)) else 0.7) * 100))
    confidence_pct = max(0, min(100, confidence_pct))

    # Band width proportional to uncertainty: wider when confidence lower
    # width_base ~ 30 points at 70% confidence; scale roughly inverse to confidence
    width = int(round(30 * (100 / max(1, confidence_pct)))) if confidence_pct > 0 else 60

    projection = []
    for m in range(1, months + 1):
        hi = min(850, simulated_score + width)
        lo = max(300, simulated_score - width)
        projection.append(
            {
                "month": m,
                "current": current_score,
                "simulated": simulated_score,
                "confHi": hi,
                "confLo": lo,
            }
        )

    summary = {
        "projected": simulated_score,
        "delta": simulated_score - current_score,
        "confidence": confidence_pct,
    }

    return ProjectionOut(
        score=simulated_score,
        category=category,
        confidence=confidence_0_1,
        projection=projection,
        summary=summary,
    )

