"""Health route."""
from datetime import datetime

from fastapi import APIRouter


router = APIRouter()


@router.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok", "platform": "unified", "timestamp": datetime.utcnow().isoformat()}
