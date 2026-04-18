"""Orchestration layer connecting all platform capabilities."""
import datetime
import secrets
import string
import uuid
from pathlib import Path
from urllib.parse import quote_plus

from fastapi import HTTPException, UploadFile

try:
    from app.agents.edge_agent import edge_agent
    from app.agents.demand_agent import demand_agent
    from app.agents.market_agent import market_agent
    from app.agents.pedagogy_agent import pedagogy_agent
    from app.agents.portfolio_agent import portfolio_agent
    from app.agents.trust_agent import trust_agent
    from app.core.config import settings
    from app.core.state import state
    from app.services.cloudinary_service import cloudinary_service
    from app.services.firecrawl_service import firecrawl_service
    from app.services.supabase_service import supabase_service
except ModuleNotFoundError:
    from agents.edge_agent import edge_agent
    from agents.demand_agent import demand_agent
    from agents.market_agent import market_agent
    from agents.pedagogy_agent import pedagogy_agent
    from agents.portfolio_agent import portfolio_agent
    from agents.trust_agent import trust_agent
    from core.config import settings
    from core.state import state
    from services.cloudinary_service import cloudinary_service
    from services.firecrawl_service import firecrawl_service
    from services.supabase_service import supabase_service


def create_artisan(payload: dict) -> dict:
    artisan_id = state.next_artisan_id
    state.next_artisan_id += 1
    artisan = {
        "id": artisan_id,
        "artisan_code": _generate_artisan_code(),
        **payload,
        "created_at": datetime.datetime.utcnow(),
    }
    state.artisans[artisan_id] = artisan
    state.portfolios[artisan_id] = []
    state.learning_paths[artisan_id] = []
    state.demand_forecasts[artisan_id] = get_demand_forecast_for_artisan(artisan_id)
    supabase_service.upsert(settings.supabase_artisans_table, artisan)
    return artisan


def get_artisan(artisan_id: int) -> dict:
    artisan = state.artisans.get(artisan_id)
    if artisan:
        return _ensure_artisan_code(artisan)
    if supabase_service.enabled:
        artisan = supabase_service.fetch_one(settings.supabase_artisans_table, id=artisan_id)
        if artisan:
            artisan = _ensure_artisan_code(artisan)
            state.artisans[artisan_id] = artisan
            state.portfolios.setdefault(artisan_id, [])
            state.learning_paths.setdefault(artisan_id, [])
            return artisan
    if not artisan:
        raise HTTPException(status_code=404, detail="Artisan not found.")
    return artisan


async def upload_portfolio(artisan_id: int, file: UploadFile, title: str | None, description: str | None) -> dict:
    artisan = get_artisan(artisan_id)
    content = await file.read()
    extension = Path(file.filename or "upload.jpg").suffix.lower() or ".jpg"
    artisan_dir = settings.media_dir / str(artisan_id)
    artisan_dir.mkdir(parents=True, exist_ok=True)
    image_path = artisan_dir / f"{uuid.uuid4().hex}{extension}"
    image_path.write_bytes(content)
    image_url = cloudinary_service.upload_image(content, public_id=f"portfolio-{artisan_id}-{uuid.uuid4().hex}")

    analysis = portfolio_agent.analyse(content)
    portfolio_item = {
        "id": state.next_portfolio_id,
        "artisan_id": artisan_id,
        "title": title,
        "description": description,
        "image_path": str(image_path),
        "image_url": image_url or f"/media/{artisan_id}/{image_path.name}",
        **analysis,
    }
    state.next_portfolio_id += 1
    state.portfolios[artisan_id].append(portfolio_item)
    supabase_service.upsert(settings.supabase_portfolio_table, portfolio_item)

    if not state.learning_paths[artisan_id]:
        build_learning_path(artisan_id, None)

    return portfolio_item


def list_portfolio(artisan_id: int) -> list[dict]:
    get_artisan(artisan_id)
    if not state.portfolios.get(artisan_id) and supabase_service.enabled:
        items = supabase_service.fetch_many(settings.supabase_portfolio_table, artisan_id=artisan_id)
        if items:
            state.portfolios[artisan_id] = items
    return state.portfolios[artisan_id]


def build_learning_path(artisan_id: int, title: str | None) -> dict:
    artisan = get_artisan(artisan_id)
    portfolio = list_portfolio(artisan_id)
    signals = _learning_signals(portfolio)
    generated = pedagogy_agent.build_learning_path(artisan.get("craft_tradition", ""), title, signals)
    path = {
        "id": state.next_learning_path_id,
        "artisan_id": artisan_id,
        **generated,
    }
    state.next_learning_path_id += 1
    state.learning_paths[artisan_id].append(path)
    supabase_service.upsert(settings.supabase_learning_paths_table, path)
    return path


def list_learning_paths(artisan_id: int) -> list[dict]:
    get_artisan(artisan_id)
    if not state.learning_paths.get(artisan_id) and supabase_service.enabled:
        items = supabase_service.fetch_many(settings.supabase_learning_paths_table, artisan_id=artisan_id)
        if items:
            state.learning_paths[artisan_id] = items
    return state.learning_paths[artisan_id]


def get_market_pivots(artisan_id: int) -> list[dict]:
    artisan = get_artisan(artisan_id)
    portfolio = list_portfolio(artisan_id)
    techniques = []
    for item in portfolio:
        techniques.extend(item["detected_techniques"])
    latest = portfolio[-1] if portfolio else None
    latest_bytes = None
    latest_mime = "image/jpeg"
    if latest:
        image_path = Path(latest["image_path"])
        if image_path.exists():
            latest_bytes = image_path.read_bytes()
            latest_mime = _mime_type_from_path(image_path)

    draft_pivots = market_agent.recommend(
        artisan.get("craft_tradition", ""),
        artisan.get("region", ""),
        techniques,
        source_image_bytes=latest_bytes,
        source_mime_type=latest_mime,
        market_signals=[],
    )

    product_keywords: list[str] = []
    for pivot in draft_pivots:
        for product in pivot.get("suggested_products", []):
            if product not in product_keywords:
                product_keywords.append(product)

    insights = get_market_insights(artisan_id, product_keywords)
    signals = insights.get("signals", [])
    for pivot in draft_pivots:
        pivot["market_signals"] = signals
        mockup_url = pivot.get("mockup_url")
        if mockup_url:
            pivot["mockup_preview_url"] = f"/api/v1/market/mockup-image?src={quote_plus(str(mockup_url))}"
    return draft_pivots


def get_market_insights(artisan_id: int, product_keywords: list[str] | None = None) -> dict:
    artisan = get_artisan(artisan_id)
    return firecrawl_service.fetch_market_signals(
        artisan.get("craft_tradition", "Traditional Craft"),
        artisan.get("region", "India"),
        product_keywords,
    )


def get_b2b_catalog(artisan_id: int) -> list[dict]:
    artisan = get_artisan(artisan_id)
    portfolio = list_portfolio(artisan_id)

    # Prefer real uploaded artworks for B2B catalog generation.
    products: list[str] = []
    for item in portfolio:
        title = (item.get("title") or "").strip()
        if title:
            products.append(title)

    # Keep a resilient fallback for artisans without uploads yet.
    if not products:
        pivots = get_market_pivots(artisan_id)
        for pivot in pivots:
            for product in pivot.get("suggested_products", []):
                if product not in products:
                    products.append(product)

    if not products:
        products = ["Signature textile bundle"]

    craft = (artisan.get("craft_tradition") or "artisan").upper().replace(" ", "-")[:12]
    catalog: list[dict] = []
    for index, title in enumerate(products[:8], start=1):
        moq = 25 if index == 1 else 40
        base_price = round(32.0 + (index * 9.5), 2)
        catalog.append(
            {
                "sku": f"{craft}-{index:03d}",
                "title": title,
                "category": "B2B Textile Procurement",
                "moq": moq,
                "available_units": 900 - (index * 95),
                "lead_time_days": 8 + (index * 2),
                "base_unit_price_usd": base_price,
                "bulk_discounts": [
                    {"min_qty": moq, "off_pct": 0},
                    {"min_qty": max(moq * 2, 80), "off_pct": 7},
                    {"min_qty": max(moq * 4, 160), "off_pct": 12},
                ],
                "fulfillment_badges": [
                    "Prime-style dispatch",
                    "Verified artisan origin",
                    "GST-ready invoicing",
                ],
            }
        )
    return catalog


def generate_b2b_quote(artisan_id: int, payload: dict) -> dict:
    get_artisan(artisan_id)
    catalog = get_b2b_catalog(artisan_id)
    sku = payload.get("sku")
    quantity = int(payload.get("quantity") or 0)
    destination = payload.get("destination_country") or "India"
    expedited = bool(payload.get("expedited"))

    item = next((row for row in catalog if row["sku"] == sku), None)
    if not item:
        raise HTTPException(status_code=404, detail="SKU not found in B2B catalog.")
    if quantity < item["moq"]:
        raise HTTPException(status_code=400, detail=f"MOQ for this item is {item['moq']} units.")

    discount_pct = 0
    for tier in item["bulk_discounts"]:
        if quantity >= tier["min_qty"]:
            discount_pct = tier["off_pct"]

    unit_price = round(item["base_unit_price_usd"] * (1 - (discount_pct / 100)), 2)
    subtotal = round(unit_price * quantity, 2)
    shipping_base = 45.0 if destination.lower() in {"india", "in"} else 140.0
    shipping = round(shipping_base + (0.28 * quantity) + (65.0 if expedited else 0.0), 2)
    tax = round(subtotal * 0.05, 2)
    total = round(subtotal + shipping + tax, 2)

    now = datetime.datetime.utcnow()
    return {
        "quote_id": f"Q-{uuid.uuid4().hex[:10].upper()}",
        "artisan_id": artisan_id,
        "sku": item["sku"],
        "quantity": quantity,
        "unit_price_usd": unit_price,
        "subtotal_usd": subtotal,
        "shipping_usd": shipping,
        "tax_usd": tax,
        "total_usd": total,
        "payment_terms": "30% advance, 70% against dispatch docs",
        "estimated_dispatch_days": item["lead_time_days"] + (0 if expedited else 2),
        "fulfillment_badges": item["fulfillment_badges"],
        "valid_until": now + datetime.timedelta(days=7),
        "generated_at": now,
    }


def get_edge_summary(artisan_id: int) -> list[dict]:
    get_artisan(artisan_id)
    return [edge_agent.edge_assessment(item) for item in list_portfolio(artisan_id)]


def get_demand_forecast_for_artisan(artisan_id: int) -> dict:
    artisan = get_artisan(artisan_id)
    portfolio = list_portfolio(artisan_id)
    techniques: list[str] = []
    for item in portfolio:
        techniques.extend(item.get("detected_techniques", []))

    product_keywords: list[str] = []
    pivots = get_market_pivots(artisan_id)
    for pivot in pivots:
        for product in pivot.get("suggested_products", []):
            if product not in product_keywords:
                product_keywords.append(product)

    insights = get_market_insights(artisan_id, product_keywords)
    forecast = demand_agent.forecast(
        artisan.get("craft_tradition", ""),
        artisan.get("region", ""),
        techniques,
        market_signals=insights.get("signals", []),
        market_query=insights.get("query", ""),
        market_source=insights.get("source", "fallback"),
    )
    state.demand_forecasts[artisan_id] = forecast
    return forecast


def telemetry_sync(payload: dict) -> dict:
    result = edge_agent.telemetry_sync(payload["device_id"], payload["jobs"])
    state.telemetry_batches.append(result)
    return result


def unified_workspace(artisan_id: int) -> dict:
    artisan = get_artisan(artisan_id)
    return {
        "artisan": artisan,
        "portfolio": list_portfolio(artisan_id),
        "learning_paths": list_learning_paths(artisan_id),
        "product_pivots": get_market_pivots(artisan_id),
        "demand_forecast": get_demand_forecast_for_artisan(artisan_id),
    }


def mint_provenance(payload: dict) -> dict:
    artisan = get_artisan(payload["artisan_id"])
    result = trust_agent.mint_certificate(artisan["name"], payload["product_id"], payload["buyer_name"])
    state.provenance_certificates[result["certificate_id"]] = result
    supabase_service.upsert(settings.supabase_certificates_table, result, on_conflict="certificate_id")
    return result


def create_escrow_contract(payload: dict) -> dict:
    get_artisan(payload["artisan_id"])
    contract = {
        "order_id": payload["order_id"],
        "artisan_id": payload["artisan_id"],
        "buyer_name": payload["buyer_name"],
        "total_amount_usd": payload["total_amount_usd"],
        "milestones": payload["milestones"],
    }
    state.escrow_contracts[payload["order_id"]] = contract
    supabase_service.upsert(settings.supabase_escrow_table, contract, on_conflict="order_id")
    return contract


def release_escrow(order_id: str, milestone_name: str) -> dict:
    contract = state.escrow_contracts.get(order_id)
    if not contract and supabase_service.enabled:
        contract = supabase_service.fetch_one(settings.supabase_escrow_table, order_id=order_id)
        if contract:
            state.escrow_contracts[order_id] = contract
    if not contract:
        raise HTTPException(status_code=404, detail="Escrow contract not found.")
    return trust_agent.release_milestone(contract, milestone_name)


def dashboard_summary() -> dict:
    return {
        "artisans": len(state.artisans),
        "portfolio_items": sum(len(items) for items in state.portfolios.values()),
        "learning_paths": sum(len(items) for items in state.learning_paths.values()),
        "provenance_certificates": len(state.provenance_certificates),
        "escrow_contracts": len(state.escrow_contracts),
    }


def _learning_signals(portfolio: list[dict]) -> dict:
    if not portfolio:
        return {"complexity_label": "Unknown", "top_techniques": [], "palette": []}

    latest = portfolio[-1]
    techniques: list[str] = []
    for item in portfolio:
        techniques.extend(item.get("detected_techniques", []))
    deduped = list(dict.fromkeys(techniques))
    return {
        "complexity_label": latest.get("complexity_label", "Unknown"),
        "top_techniques": deduped[:4],
        "palette": latest.get("color_palette", [])[:5],
    }


def _mime_type_from_path(path: Path) -> str:
    return {
        ".png": "image/png",
        ".webp": "image/webp",
        ".jpeg": "image/jpeg",
        ".jpg": "image/jpeg",
    }.get(path.suffix.lower(), "image/jpeg")


def _generate_artisan_code() -> str:
    prefix = f"ART-{datetime.datetime.utcnow():%Y}"
    alphabet = string.ascii_uppercase + string.digits

    for _ in range(12):
        suffix = "".join(secrets.choice(alphabet) for _ in range(6))
        code = f"{prefix}-{suffix}"
        if _artisan_code_exists(code):
            continue
        return code

    raise HTTPException(status_code=500, detail="Could not generate a unique artisan code.")


def _artisan_code_exists(code: str) -> bool:
    for artisan in state.artisans.values():
        if artisan.get("artisan_code") == code:
            return True

    if not supabase_service.enabled:
        return False

    return bool(supabase_service.fetch_one(settings.supabase_artisans_table, artisan_code=code))


def _ensure_artisan_code(artisan: dict) -> dict:
    if artisan.get("artisan_code"):
        return artisan

    artisan["artisan_code"] = _generate_artisan_code()
    supabase_service.upsert(settings.supabase_artisans_table, artisan)
    return artisan
