"""Pedagogy agent."""

try:
    from app.services.gemini_service import gemini_service
except ModuleNotFoundError:
    from services.gemini_service import gemini_service


class PedagogyAgent:
    def build_learning_path(self, craft_tradition: str, title: str | None = None, signals: dict | None = None) -> dict:
        base = craft_tradition or "Traditional Craft"
        signals = signals or {}
        generated = self._build_with_gemini(base, title, signals)
        if generated:
            return generated

        modules = self._fallback_modules(base, signals)
        return {
            "title": title or f"{base} Masterclass",
            "total_modules": 10,
            "modules": [
                {
                    "order_index": index + 1,
                    "title": f"Module {index + 1}: {name}",
                    "description": f"Guided practice for {name.lower()} in {base.lower()}.",
                    "skill_nodes": [name, *(signals.get("top_techniques") or [])[:2]],
                    "estimated_hours": 2.0 + index * 0.5,
                }
                for index, name in enumerate(modules)
            ],
        }

    def _build_with_gemini(self, base: str, title: str | None, signals: dict) -> dict | None:
        prompt = (
            f"Create a 10-module digital masterclass for an artisan working in {base}. "
            f"Use this context: complexity={signals.get('complexity_label', 'unknown')}, "
            f"techniques={signals.get('top_techniques', [])}, palette={signals.get('palette', [])}. "
            "Modules should feel practical, culturally grounded, and commercially useful."
        )
        schema_hint = (
            '{"title": "string", "total_modules": 10, "modules": '
            '[{"order_index": 1, "title": "string", "description": "string", '
            '"skill_nodes": ["string"], "estimated_hours": 2.5}]}'
        )
        response = gemini_service.generate_json(prompt, schema_hint)
        if not response or not response.get("modules"):
            return None

        modules = response["modules"][:10]
        cleaned = []
        for index, module in enumerate(modules, start=1):
            cleaned.append(
                {
                    "order_index": index,
                    "title": module.get("title") or f"Module {index}",
                    "description": module.get("description") or f"Practice module {index} for {base}.",
                    "skill_nodes": list(module.get("skill_nodes") or [base]),
                    "estimated_hours": float(module.get("estimated_hours") or (2.0 + index * 0.5)),
                }
            )
        return {
            "title": title or response.get("title") or f"{base} Masterclass",
            "total_modules": 10,
            "modules": cleaned,
        }

    @staticmethod
    def _fallback_modules(base: str, signals: dict) -> list[str]:
        craft = base.lower()
        techniques = signals.get("top_techniques") or []

        if "ikat" in craft:
            seed = [
                "Warp planning for resist patterns",
                "Yarn tying precision",
                "Tension management on the loom",
                "Pattern alignment under load",
            ]
        elif "pashmina" in craft or "shawl" in craft:
            seed = [
                "Fiber grading and yarn preparation",
                "Fine-count loom setup",
                "Softness and drape control",
                "Luxury finishing standards",
            ]
        else:
            seed = [
                "Foundation and tools",
                "Material preparation",
                "Structural setup",
                "Pattern interpretation",
            ]

        dynamic = [item.replace("-", " ").title() for item in techniques[:3]]
        modules = seed + dynamic + [
            "Texture control",
            "Color sequencing",
            "Advanced detailing",
            "Quality inspection",
            "Product finishing",
            "Market readiness",
        ]
        unique: list[str] = []
        for item in modules:
            if item not in unique:
                unique.append(item)
        return unique[:10]


pedagogy_agent = PedagogyAgent()
