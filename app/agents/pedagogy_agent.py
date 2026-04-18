"""Pedagogy agent with dynamic curriculum and image generation."""
import json
import urllib.parse

try:
    from google import genai
except Exception:  # pragma: no cover - optional dependency
    genai = None

from app.core.config import settings
from app.services.firecrawl_service import firecrawl_service

class PedagogyAgent:
    def __init__(self):
        if genai and settings.gemini_api_key:
            self.client = genai.Client(api_key=settings.gemini_api_key)
        else:
            self.client = None

    def build_learning_path(self, craft_tradition: str, title: str | None = None, signals: dict | None = None) -> dict:
        base = craft_tradition or "Traditional Craft"
        signal_hint = ""
        if signals:
            tops = ", ".join(signals.get("top_techniques", [])[:3])
            complexity = signals.get("complexity_label", "")
            signal_hint = f" Prioritize techniques: {tops}. Complexity profile: {complexity}."
        
        prompt = f"""
        You are a master artisan. Create a 3-module masterclass for the craft of '{base}'.{signal_hint}
        Return ONLY a valid JSON array of objects. Each object must have exactly these keys:
        - 'title': (string) Module name
        - 'description': (string) 1 sentence description of what is taught
        - 'skill': (string) The core physical skill learned
        Do not include markdown or code blocks. Just the raw JSON array.
        """
        
        try:
            if not self.client:
                raise RuntimeError("Gemini unavailable")
            response = self.client.models.generate_content(
                model='gemini-2.5-flash', # Updated model to prevent 404
                contents=prompt
            )
            raw_text = response.text.replace('```json', '').replace('```', '').strip()
            modules_data = json.loads(raw_text)
        except Exception as e:
            print(f"🚨 Pedagogy Generation Failed: {e}")
            # Fallback so the UI never crashes
            modules_data = [
                {"title": "Material Preparation", "description": "Sourcing and prepping raw materials.", "skill": "Material handling"}
            ]

        modules = []
        for index, mod in enumerate(modules_data):
            module_skill = mod.get("skill", "core hand skill")
            module_title = mod.get("title", f"Craft module {index + 1}")

            # Generate a specific image for the skill being taught
            img_prompt = f"A close-up, cinematic photograph of an artisan's hands performing {module_skill} for {base}. Warm lighting, highly detailed, instructional aesthetic."
            encoded_img = urllib.parse.quote(img_prompt)
            img_url = f"https://image.pollinations.ai/prompt/{encoded_img}?width=400&height=300&nologo=true"

            yt_query = f"{base} {module_skill} tutorial step by step"
            yt_video = firecrawl_service.search_youtube_video(yt_query)
            submodules = [
                f"Foundation: tools and setup for {module_skill}",
                f"Practice drill: repeatable rhythm for {module_skill}",
                f"Quality check: finishing and error correction in {module_title}",
            ]
            
            modules.append({
                "order_index": index + 1,
                "title": f"Module {index + 1}: {module_title}",
                "description": mod.get("description", "Learn the fundamentals and guided practice."),
                "skill_nodes": [module_skill],
                "submodules": submodules,
                "estimated_hours": 2.0 + index * 0.5,
                "thumbnail_url": img_url,
                "video_title": yt_video.get("title", "Related YouTube tutorial"),
                "video_url": yt_video.get("url", ""),
                "video_search_query": yt_query,
            })
            
        return {
            "title": title or f"{base} Masterclass",
            "total_modules": len(modules),
            "modules": modules
        }

pedagogy_agent = PedagogyAgent()