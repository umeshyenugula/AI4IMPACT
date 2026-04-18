"""Firecrawl-powered market web intelligence with a safe local fallback."""
from __future__ import annotations

from datetime import datetime
from typing import Any
from urllib.parse import quote_plus

import httpx

try:
    from app.core.config import settings
except ModuleNotFoundError:
    from core.config import settings


class FirecrawlService:
    @property
    def enabled(self) -> bool:
        return bool(settings.firecrawl_api_key)

    def fetch_market_signals(
        self,
        craft_tradition: str,
        region: str,
        product_keywords: list[str] | None = None,
    ) -> dict[str, Any]:
        query = self._build_query(craft_tradition, region, product_keywords)

        if not self.enabled:
            return {
                "craft_tradition": craft_tradition or "Traditional Craft",
                "region": region or "Global",
                "source": "fallback",
                "query": query,
                "signals": self._fallback_signals(craft_tradition, region, product_keywords),
                "generated_at": datetime.utcnow(),
            }

        payload = {
            "query": query,
            "limit": 5,
            "scrapeOptions": {
                "formats": ["markdown"],
                "onlyMainContent": True,
            },
        }
        headers = {
            "Authorization": f"Bearer {settings.firecrawl_api_key}",
            "Content-Type": "application/json",
        }

        try:
            with httpx.Client(timeout=40.0) as client:
                response = client.post(f"{settings.firecrawl_api_root}/search", headers=headers, json=payload)
                response.raise_for_status()
            parsed = self._parse_search_payload(response.json())
            if parsed:
                return {
                    "craft_tradition": craft_tradition or "Traditional Craft",
                    "region": region or "Global",
                    "source": "firecrawl",
                    "query": query,
                    "signals": parsed,
                    "generated_at": datetime.utcnow(),
                }
        except Exception:
            pass

        return {
            "craft_tradition": craft_tradition or "Traditional Craft",
            "region": region or "Global",
            "source": "fallback",
            "query": query,
            "signals": self._fallback_signals(craft_tradition, region, product_keywords),
            "generated_at": datetime.utcnow(),
        }

    def search_youtube_video(self, query: str) -> dict[str, str]:
        cleaned_query = (query or "artisan craft tutorial").strip()
        search_url = f"https://www.youtube.com/results?search_query={quote_plus(cleaned_query)}"

        if not self.enabled:
            return {
                "title": f"YouTube search for {cleaned_query}",
                "url": search_url,
                "source": "fallback",
            }

        payload = {
            "query": f"site:youtube.com {cleaned_query}",
            "limit": 3,
        }
        headers = {
            "Authorization": f"Bearer {settings.firecrawl_api_key}",
            "Content-Type": "application/json",
        }

        try:
            with httpx.Client(timeout=30.0) as client:
                response = client.post(f"{settings.firecrawl_api_root}/search", headers=headers, json=payload)
                response.raise_for_status()

            rows = response.json().get("data") or response.json().get("results") or []
            for row in rows:
                url = str(row.get("url") or row.get("sourceURL") or "").strip()
                if "youtube.com/watch" in url or "youtu.be/" in url:
                    title = str(row.get("title") or row.get("metadata", {}).get("title") or "Related YouTube video").strip()
                    return {
                        "title": title,
                        "url": url,
                        "source": "firecrawl",
                    }
        except Exception:
            pass

        return {
            "title": f"YouTube search for {cleaned_query}",
            "url": search_url,
            "source": "fallback",
        }

    @staticmethod
    def _build_query(craft_tradition: str, region: str, product_keywords: list[str] | None = None) -> str:
        craft = (craft_tradition or "traditional textile").strip()
        market = (region or "india").strip()
        products = ", ".join((product_keywords or [])[:4]).strip()
        product_hint = f" for products: {products}" if products else ""
        return (
            f"{craft} B2B wholesale demand amazon business seasonal trends in {market}{product_hint} "
            "bulk buyer price benchmark"
        )

    @staticmethod
    def _parse_search_payload(payload: dict[str, Any]) -> list[dict[str, str]]:
        rows = payload.get("data") or payload.get("results") or []
        signals: list[dict[str, str]] = []
        for row in rows[:4]:
            title = str(row.get("title") or row.get("metadata", {}).get("title") or "Market signal").strip()
            url = str(row.get("url") or row.get("sourceURL") or row.get("source", "")).strip()
            snippet = str(
                row.get("description")
                or row.get("snippet")
                or row.get("markdown", "")[:220]
                or "No summary available."
            ).strip()
            if not title:
                continue
            signals.append(
                {
                    "title": title,
                    "url": url,
                    "summary": snippet,
                }
            )
        return signals

    @staticmethod
    def _fallback_signals(
        craft_tradition: str,
        region: str,
        product_keywords: list[str] | None = None,
    ) -> list[dict[str, str]]:
        craft = craft_tradition or "Traditional textile"
        market = region or "India"
        focus = ", ".join((product_keywords or [])[:2]) or "featured SKUs"
        return [
            {
                "title": "Hospitality buyers prioritise repeatable quality",
                "url": "",
                "summary": f"{craft} collections with consistent finishes and lead-time commitments are preferred in {market} hotel procurement.",
            },
            {
                "title": "Corporate gifting peaks before festive quarters",
                "url": "",
                "summary": f"Bulk accessory SKUs like {focus} with customization and reliable logistics perform best for enterprise gifting cycles.",
            },
            {
                "title": "Amazon-style B2B buyers reward tiered pricing",
                "url": "",
                "summary": "Transparent MOQ, quantity discounts, and dispatch ETA improve conversion in digital wholesale channels.",
            },
        ]


firecrawl_service = FirecrawlService()
