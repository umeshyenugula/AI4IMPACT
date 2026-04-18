"""Trust and settlement agents."""
from datetime import datetime
from hashlib import sha256

try:
    from app.core.config import settings
except ModuleNotFoundError:
    from core.config import settings


class TrustAgent:
    def mint_certificate(self, artisan_name: str, product_id: str, buyer_name: str) -> dict:
        certificate_id = sha256(f"{artisan_name}|{product_id}|{buyer_name}".encode("utf-8")).hexdigest()[:24]
        return {
            "certificate_id": certificate_id,
            "blockchain": settings.blockchain_name,
            "product_id": product_id,
            "minted_at": datetime.utcnow(),
        }

    def release_milestone(self, contract: dict, milestone_name: str) -> dict:
        milestone = next(item for item in contract["milestones"] if item["name"] == milestone_name)
        milestone_amount = contract["total_amount_usd"] * (milestone["payout_pct"] / 100.0)
        return {
            "order_id": contract["order_id"],
            "milestone_name": milestone_name,
            "payouts": [
                {
                    "party": "artisan",
                    "recipient": "artisan",
                    "amount_usd": round(milestone_amount * 0.75, 2),
                    "amount": round(milestone_amount * 0.75, 2),
                },
                {
                    "party": "supplier",
                    "recipient": "supplier",
                    "amount_usd": round(milestone_amount * 0.15, 2),
                    "amount": round(milestone_amount * 0.15, 2),
                },
                {
                    "party": "logistics",
                    "recipient": "logistics",
                    "amount_usd": round(milestone_amount * 0.10, 2),
                    "amount": round(milestone_amount * 0.10, 2),
                },
            ],
            "released_at": datetime.utcnow(),
        }


trust_agent = TrustAgent()
