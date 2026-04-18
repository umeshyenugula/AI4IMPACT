"""Market intelligence agent."""
import base64
from datetime import datetime
from xml.sax.saxutils import escape

try:
    from app.services.cloudinary_service import cloudinary_service
    from app.services.gemini_service import gemini_service
except ModuleNotFoundError:
    from services.cloudinary_service import cloudinary_service
    from services.gemini_service import gemini_service


class MarketAgent:
    def recommend(
        self,
        craft_tradition: str,
        region: str,
        techniques: list[str],
        reference_image: bytes | None = None,
        image_mime_type: str = "image/jpeg",
    ) -> list[dict]:
        craft = (craft_tradition or "").lower()
        if "pashmina" in craft:
            pivots = [
                (
                    "Pashmina hospitality decor",
                    0.83,
                    ["Table runner", "Cushion cover", "Suite throw"],
                    ["Hotels", "Luxury resorts", "Interior stylists"],
                ),
                (
                    "Luxury gift textiles",
                    0.74,
                    ["Premium stole", "Corporate gifting set"],
                    ["Corporate gifting teams", "Luxury boutiques"],
                ),
            ]
        elif "block" in craft or "ikat" in craft:
            pivots = [
                (
                    "Tech accessories pivot",
                    0.81,
                    ["Laptop sleeve", "Cable organizer", "Tablet folio"],
                    ["Tech companies", "Startup gifting", "Design stores"],
                ),
                (
                    "Desk and stationery line",
                    0.72,
                    ["Notebook wrap", "Document sleeve"],
                    ["Corporate procurement", "Boutique retailers"],
                ),
            ]
        else:
            pivots = [
                (
                    "Boutique interior collection",
                    0.71,
                    ["Accent pillow", "Wall hanging"],
                    ["Interior designers", "Boutique hotels"],
                ),
                (
                    "Limited fashion accessories",
                    0.68,
                    ["Patch set", "Handmade pouch"],
                    ["Curated retail", "Museum shops"],
                ),
            ]

        recommendations = []
        for index, (title, score, products, buyer_segments) in enumerate(pivots, start=1):
            prompt = self._mockup_prompt(craft_tradition, region, title, products)
            mockup_url = self._mockup_url(
                prompt=prompt,
                reference_image=reference_image,
                image_mime_type=image_mime_type,
                public_id=f"{craft or 'craft'}-pivot-{index}",
                product_name=products[0],
            )
            recommendations.append(
                {
                "title": title,
                "confidence_score": score,
                "region_fit": region or "global",
                "supporting_techniques": techniques,
                "suggested_products": products,
                "buyer_segments": buyer_segments,
                "mockup_url": mockup_url,
                "mockup_prompt": prompt,
                "generated_at": datetime.utcnow(),
            }
            )
        return recommendations

    def _mockup_url(
        self,
        prompt: str,
        reference_image: bytes | None,
        image_mime_type: str,
        public_id: str,
        product_name: str,
    ) -> str:
        generated = gemini_service.generate_mockup(prompt, reference_image, image_mime_type)
        if generated:
            uploaded = cloudinary_service.upload_image(generated, public_id)
            if uploaded:
                return uploaded
            return cloudinary_service.inline_data_url(generated)
        return self._placeholder_mockup(product_name)

    @staticmethod
    def _mockup_prompt(craft_tradition: str, region: str, title: str, products: list[str]) -> str:
        return (
            f"Create a photorealistic ecommerce mockup for {title}. "
            f"Show {products[0]} made using {craft_tradition or 'traditional Indian craft'} motifs "
            f"from {region or 'India'}, styled on a clean premium studio background."
        )

    @staticmethod
    def _placeholder_mockup(product_name: str) -> str:
        label = escape(product_name)
        svg = f"""
        <svg xmlns="http://www.w3.org/2000/svg" width="640" height="480" viewBox="0 0 640 480">
          <defs>
            <linearGradient id="bg" x1="0%" y1="0%" x2="100%" y2="100%">
              <stop offset="0%" stop-color="#1c1009" />
              <stop offset="50%" stop-color="#c4501a" />
              <stop offset="100%" stop-color="#c9963a" />
            </linearGradient>
          </defs>
          <rect width="640" height="480" rx="32" fill="url(#bg)" />
          <rect x="140" y="95" width="360" height="250" rx="28" fill="#f6ead0" opacity="0.92" />
          <rect x="180" y="135" width="280" height="170" rx="18" fill="#8b1a1a" opacity="0.16" />
          <text x="320" y="225" text-anchor="middle" font-size="42" font-family="Georgia, serif" fill="#1c1009">{label}</text>
          <text x="320" y="275" text-anchor="middle" font-size="18" font-family="Georgia, serif" fill="#3d2b1f">AI market mockup ready</text>
        </svg>
        """.strip().encode("utf-8")
        return f"data:image/svg+xml;base64,{base64.b64encode(svg).decode('ascii')}"


market_agent = MarketAgent()
