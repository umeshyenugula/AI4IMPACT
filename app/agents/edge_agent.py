"""Edge and telemetry agent."""
from datetime import datetime

try:
    from app.core.config import settings
except ModuleNotFoundError:
    from core.config import settings


class EdgeAgent:
    def edge_assessment(self, portfolio_item: dict) -> dict:
        return {
            "model_name": settings.edge_model_name,
            "offline_ready": True,
            "complexity_score": portfolio_item["complexity_score"],
            "uniqueness_score": portfolio_item["uniqueness_score"],
            "last_synced_at": datetime.utcnow(),
        }

    def telemetry_sync(self, device_id: str, jobs: list[dict]) -> dict:
        return {
            "device_id": device_id,
            "synced_jobs": len(jobs),
            "update_available": False,
            "acknowledged_at": datetime.utcnow(),
        }


edge_agent = EdgeAgent()
