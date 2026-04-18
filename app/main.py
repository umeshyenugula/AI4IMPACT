"""Single-entry FastAPI app combining all platform phases."""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

try:
    from app.api.routes import dashboard, health, platform, trust
    from app.core.config import settings
except ModuleNotFoundError:
    from api.routes import dashboard, health, platform, trust
    from core.config import settings


app = FastAPI(
    title="ArtisanAI Unified Platform",
    description="Combined platform spanning portfolio intelligence, market access, edge resilience, and trust automation.",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/static", StaticFiles(directory=str(settings.static_dir)), name="static")
app.mount("/media", StaticFiles(directory=str(settings.media_dir)), name="media")
app.mount("/css", StaticFiles(directory=str(settings.frontend_dir / "css")), name="frontend-css")
app.mount("/js", StaticFiles(directory=str(settings.frontend_dir / "js")), name="frontend-js")
app.include_router(health.router, prefix="/api/v1", tags=["health"])
app.include_router(platform.router, prefix="/api/v1", tags=["platform"])
app.include_router(trust.router, prefix="/api/v1/trust", tags=["trust"])
app.include_router(dashboard.router, tags=["dashboard"])
