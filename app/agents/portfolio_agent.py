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


# Comprehensive technique vocabulary for detection
TECHNIQUE_LIBRARY = {
    "texture": ["woven-structure", "hand-knotted", "surface-texture", "fiber-layering", "tactile-detail"],
    "symmetry": ["bilateral-symmetry", "radial-pattern", "geometric-balance", "structural-harmony"],
    "detail": ["intricate-finishing", "fine-detailing", "edge-work", "border-crafting", "seam-technique"],
    "color": ["natural-dyeing", "color-harmony", "pigment-layering", "tonal-variation", "shade-blending"],
    "pattern": ["repeat-pattern", "motif-work", "geometric-design", "organic-pattern", "rhythmic-placement"],
    "technique": ["hand-finishing", "craft-technique", "traditional-method", "precision-work", "mixed-media"],
    "complexity": ["multi-layer", "compound-structure", "dimensional-effect", "relief-work", "sculptural-quality"],
}


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
        
        # Generate unique techniques based on detected image features
        techniques = self._detect_techniques(
            complexity, edge_density, contrast, symmetry, pattern_freq, len(set(palette))
        )

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

    def _detect_techniques(
        self,
        complexity: float,
        edge_density: float,
        contrast: float,
        symmetry: float,
        pattern_freq: float,
        color_diversity: int,
    ) -> list[str]:
        """Generate unique techniques based on image analysis features."""
        techniques = []

        # High edge density → textural techniques
        if edge_density > 0.15:
            techniques.append(TECHNIQUE_LIBRARY["texture"][int(edge_density * 5) % len(TECHNIQUE_LIBRARY["texture"])])

        # High contrast → color/tonal techniques
        if contrast > 40:
            techniques.append(TECHNIQUE_LIBRARY["color"][int(contrast / 20) % len(TECHNIQUE_LIBRARY["color"])])

        # High symmetry → symmetry/balance techniques
        if symmetry > 0.6:
            techniques.append(TECHNIQUE_LIBRARY["symmetry"][int(symmetry * 3) % len(TECHNIQUE_LIBRARY["symmetry"])])

        # High pattern frequency → pattern/motif techniques
        if pattern_freq > 0.15:
            techniques.append(TECHNIQUE_LIBRARY["pattern"][int(pattern_freq * 10) % len(TECHNIQUE_LIBRARY["pattern"])])

        # Color diversity → diverse palette techniques
        if color_diversity >= 4:
            techniques.append(TECHNIQUE_LIBRARY["color"][color_diversity % len(TECHNIQUE_LIBRARY["color"])])

        # Complexity-based techniques
        if complexity >= 0.7:
            techniques.append(TECHNIQUE_LIBRARY["complexity"][int(complexity * 5) % len(TECHNIQUE_LIBRARY["complexity"])])
        elif complexity >= 0.5:
            techniques.append(TECHNIQUE_LIBRARY["detail"][int(complexity * 5) % len(TECHNIQUE_LIBRARY["detail"])])

        # Ensure we always have at least 2-3 techniques
        if len(techniques) < 2:
            techniques.append(TECHNIQUE_LIBRARY["technique"][int(edge_density * 5) % len(TECHNIQUE_LIBRARY["technique"])])
            if len(techniques) < 3:
                techniques.append(TECHNIQUE_LIBRARY["pattern"][int(pattern_freq * 10) % len(TECHNIQUE_LIBRARY["pattern"])])

        # Return unique techniques (deduplicate and limit to 4)
        return list(dict.fromkeys(techniques))[:4]


portfolio_agent = PortfolioAgent()
