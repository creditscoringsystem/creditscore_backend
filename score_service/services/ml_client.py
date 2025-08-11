import os
import httpx
from typing import Dict, Any


ML_PREDICT_URL = os.getenv("ML_PREDICT_URL", "http://localhost:8006/predict")


async def predict_score(features: Dict[str, Any]) -> Dict[str, Any]:
    async with httpx.AsyncClient(timeout=5.0) as client:
        resp = await client.post(ML_PREDICT_URL, json=features)
        resp.raise_for_status()
        return resp.json()


