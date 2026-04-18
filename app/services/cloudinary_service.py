"""Cloudinary uploads for generated mockups and portfolio media."""
import base64
from datetime import datetime, timezone
from typing import Any

import httpx

try:
    from app.core.config import settings
except ModuleNotFoundError:
    from core.config import settings


class CloudinaryService:
    @property
    def enabled(self) -> bool:
        return all(
            [
                settings.cloudinary_cloud_name,
                settings.cloudinary_api_key,
                settings.cloudinary_api_secret,
            ]
        )

    def upload_image(self, image_bytes: bytes, public_id: str, folder: str | None = None) -> str | None:
        if not self.enabled:
            return None

        url = f"https://api.cloudinary.com/v1_1/{settings.cloudinary_cloud_name}/image/upload"
        auth = (settings.cloudinary_api_key, settings.cloudinary_api_secret)
        data = {
            "public_id": public_id,
            "folder": folder or settings.cloudinary_folder,
            "timestamp": str(int(datetime.now(tz=timezone.utc).timestamp())),
        }
        files: dict[str, Any] = {
            "file": ("mockup.png", image_bytes, "image/png"),
        }

        try:
            with httpx.Client(timeout=60.0) as client:
                response = client.post(url, data=data, files=files, auth=auth)
                response.raise_for_status()
            return response.json().get("secure_url")
        except Exception:
            return None

    @staticmethod
    def inline_data_url(image_bytes: bytes, mime_type: str = "image/png") -> str:
        encoded = base64.b64encode(image_bytes).decode("ascii")
        return f"data:{mime_type};base64,{encoded}"


cloudinary_service = CloudinaryService()
