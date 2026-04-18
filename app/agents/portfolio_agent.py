"""Portfolio scoring agent."""
import io
from datetime import datetime

import numpy as np
from PIL import Image, ImageFilter


def _complexity_label(score: float) -> str:
    if score >= 0.75:
        return "Very High"
    if score >= 0.55:
        return "High"
    if score >= 0.35:
        return "Medium"
    return "Low"


class PortfolioAgent:
    def analyse(self, image_bytes: bytes) -> dict:
        image = Image.open(io.BytesIO(image_bytes)).convert("RGB")
        image.thumbnail((512, 512), Image.Resampling.LANCZOS)

        gray = image.convert("L")
        pixels = np.asarray(gray, dtype=np.float32)
        edges = np.asarray(gray.filter(ImageFilter.FIND_EDGES), dtype=np.float32)
        edge_density = float(np.mean(edges > 24))
        contrast = float(np.std(pixels))
        symmetry = float(1.0 - np.mean(np.abs(np.asarray(gray, dtype=np.float32) / 255.0 - np.fliplr(np.asarray(gray, dtype=np.float32) / 255.0))))
        pattern_freq = float(min(np.max(np.abs(np.fft.fft2(pixels))) / (np.mean(np.abs(np.fft.fft2(pixels))) + 1e-9) / 10000.0, 1.0))

        complexity = round(
            min(edge_density * 0.4 + (contrast / 128.0) * 0.25 + symmetry * 0.15 + pattern_freq * 0.2, 1.0),
            4,
        )

        palette = []
        rgb = np.asarray(image.resize((64, 64)).convert("RGB"), dtype=np.uint8).reshape(-1, 3)
        for center in np.linspace(0, len(rgb) - 1, num=min(5, len(rgb)), dtype=int):
            red, green, blue = rgb[center]
            palette.append(f"#{red:02X}{green:02X}{blue:02X}")

        uniqueness = round(min(0.45 + len(set(palette)) * 0.08 + pattern_freq * 0.2, 1.0), 4)
        techniques = ["woven-structure", "texture-balance", "craft-finishing"]

        return {
            "complexity_score": complexity,
            "uniqueness_score": uniqueness,
            "complexity_label": _complexity_label(complexity),
            "detected_techniques": techniques,
            "color_palette": palette,
            "texture_features": {"edge_density": edge_density, "contrast": contrast},
            "structural_features": {"symmetry": symmetry, "pattern_freq": pattern_freq},
            "analysed_at": datetime.utcnow(),
        }


portfolio_agent = PortfolioAgent()
