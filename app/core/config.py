"""Configuration for the unified platform."""
from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


BASE_DIR = Path(__file__).resolve().parents[2]


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=BASE_DIR / ".env", extra="ignore")

    allowed_origins: list[str] = Field(
        default_factory=lambda: [
            "http://localhost:3000",
            "http://localhost:5173",
            "http://localhost:5500",
            "http://127.0.0.1:5500",
        ]
    )
    media_dir: Path = BASE_DIR / "media"
    static_dir: Path = BASE_DIR / "app" / "static"
    template_dir: Path = BASE_DIR / "app" / "templates"
    frontend_dir: Path = BASE_DIR / "app" / "frontend"
    edge_model_name: str = "phi-3-mini-simulated"
    blockchain_name: str = "solana-simulated"
    gemini_api_key: str | None = None
    gemini_text_model: str = "gemini-2.5-flash"
    gemini_image_model: str = "gemini-2.5-flash-image"
    cloudinary_cloud_name: str | None = None
    cloudinary_api_key: str | None = None
    cloudinary_api_secret: str | None = None
    cloudinary_folder: str = "artisan-ai"
    supabase_url: str | None = None
    supabase_service_role_key: str | None = None
    supabase_artisans_table: str = "artisans"
    supabase_portfolio_table: str = "portfolio_items"
    supabase_learning_paths_table: str = "learning_paths"
    supabase_certificates_table: str = "provenance_certificates"
    supabase_escrow_table: str = "escrow_contracts"
    firecrawl_api_key: str | None = None
    firecrawl_api_root: str = "https://api.firecrawl.dev/v1"


settings = Settings()
settings.media_dir.mkdir(parents=True, exist_ok=True)
settings.frontend_dir.mkdir(parents=True, exist_ok=True)
