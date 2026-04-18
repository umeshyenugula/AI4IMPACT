"""Gemini helpers for structured text and image generation."""
import base64
import json
from typing import Any

import httpx

try:
    from app.core.config import settings
except ModuleNotFoundError:
    from core.config import settings


class GeminiService:
    api_root = "https://generativelanguage.googleapis.com/v1beta/models"

    @property
    def enabled(self) -> bool:
        return bool(settings.gemini_api_key)

    def generate_json(self, prompt: str, schema_hint: str) -> dict[str, Any] | None:
        if not self.enabled:
            return None

        payload = {
            "contents": [{"parts": [{"text": f"{prompt}\n\nReturn JSON only.\nSchema:\n{schema_hint}"}]}],
            "generationConfig": {"responseMimeType": "application/json"},
        }
        url = f"{self.api_root}/{settings.gemini_text_model}:generateContent"

        try:
            with httpx.Client(timeout=30.0) as client:
                response = client.post(url, params={"key": settings.gemini_api_key}, json=payload)
                response.raise_for_status()
            text = self._extract_text(response.json())
            return json.loads(text) if text else None
        except Exception:
            return None

    def generate_mockup(self, prompt: str, reference_image: bytes | None = None, mime_type: str = "image/jpeg") -> bytes | None:
        if not self.enabled:
            return None

        parts: list[dict[str, Any]] = [{"text": prompt}]
        if reference_image:
            parts.append(
                {
                    "inline_data": {
                        "mime_type": mime_type,
                        "data": base64.b64encode(reference_image).decode("ascii"),
                    }
                }
            )

        payload = {
            "contents": [{"parts": parts}],
            "generationConfig": {"responseModalities": ["TEXT", "IMAGE"]},
        }
        url = f"{self.api_root}/{settings.gemini_image_model}:generateContent"

        try:
            with httpx.Client(timeout=60.0) as client:
                response = client.post(url, params={"key": settings.gemini_api_key}, json=payload)
                response.raise_for_status()
            return self._extract_image_bytes(response.json())
        except Exception:
            return None

    @staticmethod
    def _extract_text(payload: dict[str, Any]) -> str | None:
        candidates = payload.get("candidates") or []
        for candidate in candidates:
            parts = candidate.get("content", {}).get("parts") or []
            for part in parts:
                if part.get("text"):
                    return part["text"]
        return None

    @staticmethod
    def _extract_image_bytes(payload: dict[str, Any]) -> bytes | None:
        candidates = payload.get("candidates") or []
        for candidate in candidates:
            parts = candidate.get("content", {}).get("parts") or []
            for part in parts:
                inline_data = part.get("inlineData") or part.get("inline_data")
                if inline_data and inline_data.get("data"):
                    return base64.b64decode(inline_data["data"])
        return None


gemini_service = GeminiService()
