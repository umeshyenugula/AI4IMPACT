"""Frontend page routes."""
from pathlib import Path

from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse

try:
    from app.core.config import settings
    from app.services.platform_service import dashboard_summary
except ModuleNotFoundError:
    from core.config import settings
    from services.platform_service import dashboard_summary


router = APIRouter()

PAGES = {
    "index": settings.frontend_dir / "index.html",
    "dashboard": settings.frontend_dir / "dashboard.html",
    "register": settings.frontend_dir / "register.html",
    "portfolio": settings.frontend_dir / "portfolio.html",
    "learning": settings.frontend_dir / "learning.html",
    "workspace": settings.frontend_dir / "workspace.html",
}


def _page_response(path: Path) -> FileResponse:
    if not path.exists():
        raise HTTPException(status_code=404, detail="Frontend page not found.")
    return FileResponse(path)


@router.get("/")
async def home():
    return _page_response(PAGES["index"])


@router.get("/{page_name}.html")
async def page(page_name: str):
    path = PAGES.get(page_name)
    if not path:
        raise HTTPException(status_code=404, detail="Page not found.")
    return _page_response(path)


@router.get("/pages/{page_name}.html")
async def nested_page(page_name: str):
    return await page(page_name)


@router.get("/api/v1/dashboard-summary")
async def dashboard_summary_route():
    return dashboard_summary()
