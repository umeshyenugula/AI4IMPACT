"""Seasonal demand forecasting for institutional buyers."""


class DemandAgent:
    def forecast(self, craft_tradition: str, region: str, techniques: list[str]) -> dict:
        craft = (craft_tradition or "").lower()

        if "pashmina" in craft or "shawl" in craft:
            spikes = [
                {
                    "label": "Winter hospitality restocking",
                    "period": "Q4",
                    "demand_score": 92,
                    "buyer_segment": "Hotels and luxury retreats",
                    "rationale": "Cold-season room styling and premium gifting increase bulk textile orders.",
                },
                {
                    "label": "Festive gifting collections",
                    "period": "Q3",
                    "demand_score": 74,
                    "buyer_segment": "Corporate procurement teams",
                    "rationale": "Premium shawls and throws align with festive and year-end gifting cycles.",
                },
            ]
            buyers = ["Hotels and luxury retreats", "Corporate procurement teams", "Interior stylists"]
            opportunity = "Q4 Winter Hospitality Restocking"
        elif "ikat" in craft or "block" in craft or "print" in craft:
            spikes = [
                {
                    "label": "Corporate gifting tech accessories",
                    "period": "Q3",
                    "demand_score": 88,
                    "buyer_segment": "Tech companies and startups",
                    "rationale": "Laptop sleeves, folios, and desk accessories fit monsoon-to-festive gifting budgets.",
                },
                {
                    "label": "Boutique hotel soft-furnishing refresh",
                    "period": "Q2",
                    "demand_score": 67,
                    "buyer_segment": "Boutique hospitality brands",
                    "rationale": "Small-batch printed textiles perform well in pre-summer renovation cycles.",
                },
            ]
            buyers = ["Tech companies and startups", "Boutique hospitality brands", "Design-led retailers"]
            opportunity = "Q3 Corporate Gifting"
        else:
            spikes = [
                {
                    "label": "Interior designer sourcing window",
                    "period": "Q2",
                    "demand_score": 71,
                    "buyer_segment": "Interior designers",
                    "rationale": "Design projects lock sourcing before peak wedding and festive seasons.",
                },
                {
                    "label": "Festival and wedding retail surge",
                    "period": "Q3",
                    "demand_score": 79,
                    "buyer_segment": "Curated retail buyers",
                    "rationale": "Handcrafted decor and gifting assortments rise during festive buying periods.",
                },
            ]
            buyers = ["Interior designers", "Curated retail buyers", "Hospitality groups"]
            opportunity = "Q3 Festive Retail Surge"

        return {
            "craft_tradition": craft_tradition or "Traditional Craft",
            "forecast_window": "Next 12 months",
            "buyer_segments": buyers,
            "top_opportunity": opportunity,
            "spikes": spikes,
            "supporting_techniques": techniques,
            "region": region,
        }


demand_agent = DemandAgent()
