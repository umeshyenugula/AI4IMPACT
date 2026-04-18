"""Optional persistence layer backed by Supabase REST."""
from datetime import datetime
from typing import Any

import httpx

try:
    from app.core.config import settings
except ModuleNotFoundError:
    from core.config import settings


def _jsonable(value: Any) -> Any:
    if isinstance(value, datetime):
        return value.isoformat()
    if isinstance(value, list):
        return [_jsonable(item) for item in value]
    if isinstance(value, dict):
        return {key: _jsonable(item) for key, item in value.items()}
    return value


class SupabaseService:
    @property
    def enabled(self) -> bool:
        return bool(settings.supabase_url and settings.supabase_service_role_key)

    @property
    def headers(self) -> dict[str, str]:
        token = settings.supabase_service_role_key or ""
        return {
            "apikey": token,
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        }

    def upsert(self, table: str, row: dict[str, Any], on_conflict: str = "id") -> None:
        if not self.enabled:
            return

        url = f"{settings.supabase_url}/rest/v1/{table}"
        headers = self.headers | {"Prefer": "return=minimal,resolution=merge-duplicates"}
        with httpx.Client(timeout=20.0) as client:
            client.post(url, headers=headers, params={"on_conflict": on_conflict}, json=[_jsonable(row)])

    def fetch_one(self, table: str, **filters: Any) -> dict[str, Any] | None:
        rows = self.fetch_many(table, limit=1, **filters)
        return rows[0] if rows else None

    def fetch_many(self, table: str, limit: int | None = None, **filters: Any) -> list[dict[str, Any]]:
        if not self.enabled:
            return []

        url = f"{settings.supabase_url}/rest/v1/{table}"
        params = {key: f"eq.{value}" for key, value in filters.items()}
        if limit:
            params["limit"] = str(limit)

        try:
            with httpx.Client(timeout=20.0) as client:
                response = client.get(url, headers=self.headers, params=params)
                response.raise_for_status()
            return response.json()
        except Exception:
            return []


supabase_service = SupabaseService()
