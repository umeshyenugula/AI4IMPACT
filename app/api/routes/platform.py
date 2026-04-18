"""Integrated platform endpoints."""
from fastapi import APIRouter, File, Form, UploadFile

try:
    from app.schemas.platform import (
        ArtisanCreate,
        ArtisanResponse,
        DemandForecastResponse,
        EdgeSyncResponse,
        LearningPathResponse,
        PivotRecommendationResponse,
        PortfolioResponse,
        TelemetryRequest,
        TelemetryResponse,
        UnifiedWorkspaceResponse,
    )
    from app.services.platform_service import (
        build_learning_path,
        create_artisan,
        get_artisan,
        get_demand_forecast_for_artisan,
        get_edge_summary,
        get_market_pivots,
        list_learning_paths,
        list_portfolio,
        telemetry_sync,
        unified_workspace,
        upload_portfolio,
    )
except ModuleNotFoundError:
    from schemas.platform import (
        ArtisanCreate,
        ArtisanResponse,
        DemandForecastResponse,
        EdgeSyncResponse,
        LearningPathResponse,
        PivotRecommendationResponse,
        PortfolioResponse,
        TelemetryRequest,
        TelemetryResponse,
        UnifiedWorkspaceResponse,
    )
    from services.platform_service import (
        build_learning_path,
        create_artisan,
        get_artisan,
        get_demand_forecast_for_artisan,
        get_edge_summary,
        get_market_pivots,
        list_learning_paths,
        list_portfolio,
        telemetry_sync,
        unified_workspace,
        upload_portfolio,
    )


router = APIRouter()


@router.post("/artisans", response_model=ArtisanResponse, status_code=201)
async def register_artisan(payload: ArtisanCreate):
    return create_artisan(payload.model_dump())


@router.get("/artisans/{artisan_id}", response_model=ArtisanResponse)
async def fetch_artisan(artisan_id: int):
    return get_artisan(artisan_id)


@router.post("/artisans/{artisan_id}/portfolio", response_model=PortfolioResponse, status_code=201)
async def add_portfolio_item(
    artisan_id: int,
    file: UploadFile = File(...),
    title: str | None = Form(None),
    description: str | None = Form(None),
):
    return await upload_portfolio(artisan_id, file, title, description)


@router.get("/artisans/{artisan_id}/portfolio", response_model=list[PortfolioResponse])
async def get_portfolio(artisan_id: int):
    return list_portfolio(artisan_id)


@router.post("/artisans/{artisan_id}/learning-paths", response_model=LearningPathResponse, status_code=201)
async def create_learning_path(artisan_id: int, title: str | None = None):
    return build_learning_path(artisan_id, title)


@router.get("/artisans/{artisan_id}/learning-paths", response_model=list[LearningPathResponse])
async def get_learning_paths(artisan_id: int):
    return list_learning_paths(artisan_id)


@router.get("/artisans/{artisan_id}/market-pivots", response_model=list[PivotRecommendationResponse])
async def market_pivots(artisan_id: int):
    return get_market_pivots(artisan_id)


@router.get("/artisans/{artisan_id}/demand-forecast", response_model=DemandForecastResponse)
async def demand_forecast(artisan_id: int):
    return get_demand_forecast_for_artisan(artisan_id)


@router.get("/artisans/{artisan_id}/edge-summary", response_model=list[EdgeSyncResponse])
async def edge_summary(artisan_id: int):
    return get_edge_summary(artisan_id)


@router.post("/telemetry/sync", response_model=TelemetryResponse)
async def sync_telemetry(payload: TelemetryRequest):
    return telemetry_sync(payload.model_dump())


@router.get("/artisans/{artisan_id}/workspace", response_model=UnifiedWorkspaceResponse)
async def workspace(artisan_id: int):
    return unified_workspace(artisan_id)
