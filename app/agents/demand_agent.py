"""Seasonal demand forecasting for institutional buyers."""


class DemandAgent:
    def forecast(
        self,
        craft_tradition: str,
        region: str,
        techniques: list[str],
        market_signals: list[dict] | None = None,
        market_query: str | None = None,
        market_source: str | None = None,
    ) -> dict:
        signals = market_signals or []

        if signals:
            spikes = []
            buyer_segments: list[str] = []
            periods = ["Q2", "Q3", "Q4"]
            for i, signal in enumerate(signals[:3]):
                title = signal.get("title") or "Market signal"
                summary = signal.get("summary") or "Web trend signal from current market data."
                text = f"{title} {summary}".lower()

                if "hotel" in text or "hospitality" in text:
                    buyer = "Hotels and hospitality buyers"
                elif "corporate" in text or "procurement" in text:
                    buyer = "Corporate procurement teams"
                elif "designer" in text or "interior" in text:
                    buyer = "Interior and design studios"
                else:
                    buyer = "Specialty wholesale buyers"

                if buyer not in buyer_segments:
                    buyer_segments.append(buyer)

                spikes.append(
                    {
                        "label": title[:72],
                        "period": periods[i % len(periods)],
                        "demand_score": min(96, 68 + (i * 9) + (6 if "bulk" in text else 0)),
                        "buyer_segment": buyer,
                        "rationale": summary[:220],
                    }
                )

            opportunity = spikes[0]["label"] if spikes else "Web-tracked opportunity"
            buyers = buyer_segments or ["Institutional buyers"]
        else:
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
            "market_source": market_source or ("firecrawl" if signals else "fallback"),
            "market_query": market_query or "",
            "market_signals": signals[:3],
        }


demand_agent = DemandAgent()
