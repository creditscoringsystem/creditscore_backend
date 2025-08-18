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


def _to_category(score_0_100: int) -> str:
    if score_0_100 >= 80:
        return "good"
    if score_0_100 >= 60:
        return "average"
    return "poor"


def compute_rule_based_score(answers: Dict[str, Any]) -> Dict[str, Any]:
    """Compute normalized score (0-100) from survey answers.

    Returns a dict matching the ML client's shape for compatibility:
    {"score": int, "category": str, "confidence": None, "model_version": "rules:v1"}
    """
    raw = _sum_points(answers)
    normalized = round((raw / _MAX_POINTS) * 100)
    return {
        "score": int(normalized),
        "category": _to_category(int(normalized)),
        "confidence": None,
        "model_version": "rules:v1",
    }
