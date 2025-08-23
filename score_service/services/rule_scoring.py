from typing import Dict, Any

# Rule dictionary as provided
SURVEY_RULES: Dict[str, Dict[str, int]] = {
    "age": {"18-24": 2, "25-34": 4, "35-50": 5, "51+": 4},
    "income": {"<5m": 1, "5-10m": 3, "10-20m": 4, "20-50m": 5, ">50m": 6},
    "job_type": {"freelance": 1, "employee": 4, "manager": 5},
    "credit_cards": {"0": 0, "1": 3, "2-3": 5, "4+": 4},
    "credit_usage": {"<10%": 6, "11-30%": 5, "31-50%": 3, "51-70%": 1, ">70%": 0},
    "pay_full_on_time": {"yes": 6, "sometimes": 3, "no": 0},
    "card_blocked": {"no": 5, "yes": 0},
    "late_12m": {"0": 10, "1-2": 7, "3-5": 3, "6+": 0},
    "pay_timing": {"early": 10, "on_time": 7, "late": 0},
    "late_fee": {"no": 5, "yes": 0},
    "market_behavior": {"hold": 4, "invest_more": 5, "withdraw": 1},
    "willing_to_borrow": {"yes": 4, "maybe": 3, "no": 1},
    "urgent_money": {"friends": 3, "bank": 4, "credit_card": 2},
    "large_money_use": {"invest": 5, "save": 4, "spend": 1},
}

# precompute max possible points for normalization
_MAX_POINTS = sum(max(v.values()) for v in SURVEY_RULES.values())  # 81


def _sum_points(answers: Dict[str, Any]) -> int:
    total = 0
    for k, options in SURVEY_RULES.items():
        ans = answers.get(k)
        if ans is None:
            continue  # allow partial; missing counts as 0
        score = options.get(str(ans))
        if score is not None:
            total += score
    return total


def _to_fico_category(fico: int) -> str:
    """Map a FICO-like score to a category.

    Ranges follow commonly used FICO buckets:
    - <580: poor
    - 580-669: fair
    - 670-739: good
    - 740-799: very_good
    - >=800: exceptional
    """
    if fico >= 800:
        return "exceptional"
    if fico >= 740:
        return "very_good"
    if fico >= 670:
        return "good"
    if fico >= 580:
        return "fair"
    return "poor"


def _category_display(cat: str) -> str:
    mapping = {
        "poor": "Poor",
        "fair": "Fair",
        "good": "Good",
        "very_good": "Very Good",
        "exceptional": "Exceptional",
    }
    return mapping.get(cat, cat.title())


def _band_info(fico: int) -> dict:
    """Return UI band info: color and min/max for the band that 'fico' falls into."""
    bands = [
        {"min": 300, "max": 579, "cat": "poor", "color": "#FF4C4C"},
        {"min": 580, "max": 669, "cat": "fair", "color": "#FFA500"},
        {"min": 670, "max": 739, "cat": "good", "color": "#FFD700"},
        {"min": 740, "max": 799, "cat": "very_good", "color": "#90EE90"},
        {"min": 800, "max": 850, "cat": "exceptional", "color": "#228B22"},
    ]
    for b in bands:
        if b["min"] <= fico <= b["max"]:
            return b
    return bands[0]


def compute_rule_based_score(answers: Dict[str, Any]) -> Dict[str, Any]:
    """Compute a FICO-like score (300-850) from survey answers.

    Steps:
    1) Sum rule points from answers.
    2) Normalize to [0, 1].
    3) Linearly map to [300, 850].

    Returns a dict compatible with callers:
    {"score": int, "category": str, "confidence": None, "model_version": "rules_fico:v1"}
    """
    raw = _sum_points(answers)
    # Normalize to [0,1]
    norm = max(0.0, min(1.0, (raw / _MAX_POINTS) if _MAX_POINTS > 0 else 0.0))
    # Map to FICO-like range: 300..850 (span 550)
    fico = int(round(300 + norm * 550))
    # Safety clamp
    fico = min(850, max(300, fico))

    category = _to_fico_category(fico)
    band = _band_info(fico)
    percentile = int(round(norm * 100))  # 0..100 to support UI percentile display

    return {
        "score": fico,
        "category": category,
        "category_display": _category_display(category),
        "percentile": percentile,
        "band_color": band["color"],
        "band_min": band["min"],
        "band_max": band["max"],
        "confidence": None,
        "model_version": "rules_fico:v1",
    }


def ui_from_fico(score: int) -> Dict[str, Any]:
    """Derive UI fields from a FICO-like score without raw survey answers.

    Percentile is approximated linearly from 300..850 -> 0..100 for display.
    """
    score = min(850, max(300, int(score)))
    category = _to_fico_category(score)
    band = _band_info(score)
    percentile = int(round(((score - 300) / 550) * 100))
    percentile = max(0, min(100, percentile))
    return {
        "category": category,
        "category_display": _category_display(category),
        "percentile": percentile,
        "band_color": band["color"],
        "band_min": band["min"],
        "band_max": band["max"],
    }
