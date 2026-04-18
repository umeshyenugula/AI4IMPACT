"""Market intelligence and generative pivot agent."""
from __future__ import annotations

import os
import urllib.parse
from datetime import datetime

try:
    from google import genai
    from google.genai import types
except Exception:  # pragma: no cover - optional dependency
    genai = None
    types = None

from app.core.config import settings

class MarketAgent:
    def __init__(self):
        if genai and settings.gemini_api_key:
            self.client = genai.Client(api_key=settings.gemini_api_key)
        else:
            self.client = None

    def _extract_style(
        self,
        source_image_path: str | None,
        source_image_bytes: bytes | None,
        source_mime_type: str,
    ) -> str:
        """Use a reference image to infer artisan style details for prompt quality."""
        if not self.client:
            return "traditional geometric textile pattern with warm earthy palette"

        try:
            image_bytes = source_image_bytes
            mime_type = source_mime_type or "image/jpeg"

            if image_bytes is None and source_image_path and os.path.exists(source_image_path):
                with open(source_image_path, "rb") as handle:
                    image_bytes = handle.read()
                ext = os.path.splitext(source_image_path)[1].lower()
                if ext == ".png":
                    mime_type = "image/png"
                elif ext == ".webp":
                    mime_type = "image/webp"

            if not image_bytes:
                return "traditional geometric textile pattern with warm earthy palette"

            vision_prompt = (
                "Describe the exact textile pattern geometry, material texture, and color palette in one detailed sentence."
            )
            if not types:
                return "traditional geometric textile pattern with warm earthy palette"
            response = self.client.models.generate_content(
                model="gemini-2.5-flash",
                contents=[types.Part.from_bytes(data=image_bytes, mime_type=mime_type), vision_prompt],
            )
            return (response.text or "traditional geometric textile pattern").strip()
        except Exception as error:
            print(f"Market style extraction failed: {error}")
            return "traditional geometric textile pattern with warm earthy palette"

    def generate_mockup_prompt(self, product_name: str, extracted_style: str, craft_tradition: str) -> str:
        return (
            f"Amazon-style premium B2B catalog product photo of {product_name}. "
            f"Use this artisan fabric style: {extracted_style}. "
            f"Show commercial-ready merchandising inspired by {craft_tradition or 'traditional craft'}. "
            "Crisp white background, soft studio shadows, e-commerce ready framing, photorealistic."
        )

    def generate_mockup_url(self, prompt: str) -> str:
        encoded_prompt = urllib.parse.quote(prompt)
        return f"https://image.pollinations.ai/prompt/{encoded_prompt}?width=896&height=896&nologo=true"

    def recommend(
        self,
        craft_tradition: str,
        region: str,
        techniques: list[str],
        source_image_path: str | None = None,
        source_image_bytes: bytes | None = None,
        source_mime_type: str = "image/jpeg",
        market_signals: list[dict] | None = None,
    ) -> list[dict]:
        craft = (craft_tradition or "").lower()

        extracted_style = self._extract_style(source_image_path, source_image_bytes, source_mime_type)

        if "pashmina" in craft:
            pivots = [
                (
                    "Luxury hospitality textile bundle",
                    0.86,
                    ["Executive throw blanket", "Premium room runner", "Boutique lounge shawl"],
                    ["Hotels and resorts", "Interior procurement teams"],
                )
            ]
        elif "block" in craft or "ikat" in craft:
            pivots = [
                (
                    "Corporate tech gifting collection",
                    0.84,
                    ["Laptop sleeve", "Tablet folio", "Executive mouse pad"],
                    ["Amazon Business sellers", "Corporate gifting buyers"],
                )
            ]
        else:
            pivots = [
                (
                    "Boutique interior sourcing line",
                    0.77,
                    ["Accent cushion set", "Wall tapestry", "Table linen trio"],
                    ["Design studios", "Home decor wholesalers"],
                )
            ]

        results = []
        top_signals = (market_signals or [])[:3]

        for title, score, products, buyers in pivots:
            mockup_prompt = self.generate_mockup_prompt(products[0], extracted_style, craft_tradition)
            mockup_url = self.generate_mockup_url(mockup_prompt)
            results.append({
                "title": title,
                "confidence_score": score,
                "region_fit": region or "global",
                "supporting_techniques": techniques,
                "suggested_products": products,
                "buyer_segments": buyers,
                "market_signals": top_signals,
                "mockup_prompt": mockup_prompt,
                "mockup_url": mockup_url,
                "generated_at": datetime.utcnow(),
            })

        return results


market_agent = MarketAgent()