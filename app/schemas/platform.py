"""Schemas shared across unified platform endpoints."""
from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class ArtisanCreate(BaseModel):
    name: str
    email: EmailStr
    region: str | None = None
    village: str | None = None
    craft_tradition: str | None = None


class ArtisanResponse(ArtisanCreate):
    id: int
    artisan_code: str
    created_at: datetime


class PortfolioResponse(BaseModel):
    id: int
    artisan_id: int
    title: str | None = None
    description: str | None = None
    image_path: str
    image_url: str | None = None
    complexity_score: float
    uniqueness_score: float
    complexity_label: str
    detected_techniques: list[str]
    color_palette: list[str]
    analysed_at: datetime


class LearningModuleResponse(BaseModel):
    order_index: int
    title: str
    description: str
    skill_nodes: list[str]
    submodules: list[str] = Field(default_factory=list)
    estimated_hours: float
    video_title: str | None = None
    video_url: str | None = None
    video_search_query: str | None = None


class LearningPathResponse(BaseModel):
    id: int
    artisan_id: int
    title: str
    total_modules: int
    modules: list[LearningModuleResponse]


class PivotRecommendationResponse(BaseModel):
    title: str
    confidence_score: float
    region_fit: str
    supporting_techniques: list[str]
    suggested_products: list[str]
    buyer_segments: list[str] = Field(default_factory=list)
    market_signals: list[dict] = Field(default_factory=list)
    mockup_url: str | None = None
    mockup_preview_url: str | None = None
    mockup_prompt: str | None = None
    generated_at: datetime


class MarketInsightResponse(BaseModel):
    craft_tradition: str
    region: str
    source: str
    query: str
    signals: list[dict]
    generated_at: datetime


class DemandSpikeResponse(BaseModel):
    label: str
    period: str
    demand_score: int = Field(..., ge=0, le=100)
    buyer_segment: str
    rationale: str


class DemandForecastResponse(BaseModel):
    craft_tradition: str
    forecast_window: str
    buyer_segments: list[str]
    top_opportunity: str
    spikes: list[DemandSpikeResponse]
    market_source: str | None = None
    market_query: str | None = None
    market_signals: list[dict] = Field(default_factory=list)


class EdgeSyncResponse(BaseModel):
    model_config = ConfigDict(protected_namespaces=())
    model_name: str
    offline_ready: bool
    complexity_score: float
    uniqueness_score: float
    last_synced_at: datetime


class TelemetryJob(BaseModel):
    job_ref: str
    payload_type: str
    summary: str


class TelemetryRequest(BaseModel):
    device_id: str
    jobs: list[TelemetryJob]


class TelemetryResponse(BaseModel):
    device_id: str
    synced_jobs: int
    update_available: bool
    acknowledged_at: datetime


class UnifiedWorkspaceResponse(BaseModel):
    artisan: ArtisanResponse
    portfolio: list[PortfolioResponse]
    learning_paths: list[LearningPathResponse]
    product_pivots: list[PivotRecommendationResponse]
    demand_forecast: DemandForecastResponse


class B2BCatalogItemResponse(BaseModel):
    sku: str
    title: str
    category: str
    moq: int
    available_units: int
    lead_time_days: int
    base_unit_price_usd: float
    bulk_discounts: list[dict]
    fulfillment_badges: list[str]


class B2BQuoteRequest(BaseModel):
    sku: str
    quantity: int = Field(..., ge=1)
    destination_country: str = Field(default="India", min_length=2)
    expedited: bool = False


class B2BQuoteResponse(BaseModel):
    quote_id: str
    artisan_id: int
    sku: str
    quantity: int
    unit_price_usd: float
    subtotal_usd: float
    shipping_usd: float
    tax_usd: float
    total_usd: float
    payment_terms: str
    estimated_dispatch_days: int
    fulfillment_badges: list[str]
    valid_until: datetime
    generated_at: datetime


class ProvenanceRequest(BaseModel):
    artisan_id: int
    product_id: str
    buyer_name: str


class ProvenanceResponse(BaseModel):
    certificate_id: str
    blockchain: str
    product_id: str
    minted_at: datetime


class EscrowMilestone(BaseModel):
    name: str
    payout_pct: float = Field(..., gt=0, le=100)


class EscrowCreateRequest(BaseModel):
    order_id: str
    artisan_id: int
    buyer_name: str
    total_amount_usd: float
    milestones: list[EscrowMilestone]


class EscrowReleaseResponse(BaseModel):
    order_id: str
    milestone_name: str
    payouts: list[dict]
    released_at: datetime
