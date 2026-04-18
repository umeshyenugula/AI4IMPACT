"""Integrated platform endpoints."""

import httpx
from fastapi import APIRouter, File, Form, HTTPException, Query, UploadFile
from fastapi.responses import Response

try:
    from app.schemas.platform import (
        ArtisanCreate,
        ArtisanResponse,
        B2BCatalogItemResponse,
        B2BQuoteRequest,
        B2BQuoteResponse,
        DemandForecastResponse,
        EdgeSyncResponse,
        LearningPathResponse,
        MarketInsightResponse,
        PivotRecommendationResponse,
        PortfolioResponse,
        TelemetryRequest,
        TelemetryResponse,
        UnifiedWorkspaceResponse,
    )
    from app.services.platform_service import (
        build_learning_path,
        create_artisan,
        generate_b2b_quote,
        get_artisan,
        get_b2b_catalog,
        get_demand_forecast_for_artisan,
        get_edge_summary,
        get_market_insights,
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
        B2BCatalogItemResponse,
        B2BQuoteRequest,
        B2BQuoteResponse,
        DemandForecastResponse,
        EdgeSyncResponse,
        LearningPathResponse,
        MarketInsightResponse,
        PivotRecommendationResponse,
        PortfolioResponse,
        TelemetryRequest,
        TelemetryResponse,
        UnifiedWorkspaceResponse,
    )
    from services.platform_service import (
        build_learning_path,
        create_artisan,
        generate_b2b_quote,
        get_artisan,
        get_b2b_catalog,
        get_demand_forecast_for_artisan,
        get_edge_summary,
        get_market_insights,
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


@router.get("/artisans/{artisan_id}/market-insights", response_model=MarketInsightResponse)
async def market_insights(artisan_id: int):
    return get_market_insights(artisan_id)


@router.get("/artisans/{artisan_id}/b2b/catalog", response_model=list[B2BCatalogItemResponse])
async def b2b_catalog(artisan_id: int):
    return get_b2b_catalog(artisan_id)


@router.post("/artisans/{artisan_id}/b2b/quotes", response_model=B2BQuoteResponse)
async def b2b_quote(artisan_id: int, payload: B2BQuoteRequest):
    return generate_b2b_quote(artisan_id, payload.model_dump())


@router.get("/artisans/{artisan_id}/demand-forecast", response_model=DemandForecastResponse)
async def demand_forecast(artisan_id: int):
    return get_demand_forecast_for_artisan(artisan_id)


@router.get("/market/mockup-image")
async def market_mockup_image(src: str = Query(..., min_length=12)):
    if not (src.startswith("http://") or src.startswith("https://")):
        raise HTTPException(status_code=400, detail="Invalid image source URL.")

    try:
        async with httpx.AsyncClient(timeout=25.0, follow_redirects=True) as client:
            response = await client.get(src)
            response.raise_for_status()
    except Exception as error:
        raise HTTPException(status_code=502, detail=f"Could not fetch mockup image: {error}") from error

    media_type = response.headers.get("content-type", "image/png")
    if not media_type.startswith("image/"):
        media_type = "image/png"

    return Response(
        content=response.content,
        media_type=media_type,
        headers={"Cache-Control": "public, max-age=3600"},
    )


@router.get("/artisans/{artisan_id}/edge-summary", response_model=list[EdgeSyncResponse])
async def edge_summary(artisan_id: int):
    return get_edge_summary(artisan_id)


@router.post("/telemetry/sync", response_model=TelemetryResponse)
async def sync_telemetry(payload: TelemetryRequest):
    return telemetry_sync(payload.model_dump())


@router.get("/artisans/{artisan_id}/workspace", response_model=UnifiedWorkspaceResponse)
async def workspace(artisan_id: int):
    return unified_workspace(artisan_id)
