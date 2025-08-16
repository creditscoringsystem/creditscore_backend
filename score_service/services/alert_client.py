import os
from typing import Optional
import httpx


ALERT_SERVICE_URL = os.getenv("ALERT_SERVICE_URL", "http://localhost:8004")


async def notify_score_updated(
    *,
    user_id: str,
    old_score: Optional[int],
    new_score: int,
    category: Optional[str],
    model_version: Optional[str],
    calculated_at: str,
) -> None:
    url = f"{ALERT_SERVICE_URL}/alerts/on-score-updated"
    payload = {
        "user_id": user_id,
        "old_score": old_score,
        "new_score": new_score,
        "category": category,
        "model_version": model_version,
        "calculated_at": calculated_at,
    }
    try:
        async with httpx.AsyncClient(timeout=3.0) as client:
            await client.post(url, json=payload)
    except Exception:
        # Không làm fail flow chính nếu alert service lỗi
        pass


