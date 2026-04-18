"""Orchestration layer connecting all platform capabilities."""
import datetime
import secrets
import string
import uuid
from pathlib import Path

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
    return market_agent.recommend(
        artisan.get("craft_tradition", ""),
        artisan.get("region", ""),
        techniques,
        latest_bytes,
        latest_mime,
    )


def get_edge_summary(artisan_id: int) -> list[dict]:
    get_artisan(artisan_id)
    return [edge_agent.edge_assessment(item) for item in list_portfolio(artisan_id)]


def get_demand_forecast_for_artisan(artisan_id: int) -> dict:
    artisan = get_artisan(artisan_id)
    portfolio = list_portfolio(artisan_id)
    techniques: list[str] = []
    for item in portfolio:
        techniques.extend(item.get("detected_techniques", []))
    forecast = demand_agent.forecast(artisan.get("craft_tradition", ""), artisan.get("region", ""), techniques)
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
    existing = _find_certificate_by_product(payload["product_id"])
    if existing:
        existing_buyer = str(existing.get("buyer_name") or "").strip().lower()
        requested_buyer = str(payload["buyer_name"] or "").strip().lower()

        # A product can only have one owner-certificate pair.
        if existing_buyer and existing_buyer != requested_buyer:
            raise HTTPException(
                status_code=409,
                detail=(
                    f"Product {payload['product_id']} is already sold to "
                    f"{existing.get('buyer_name', 'another buyer')} and cannot be certified again."
                ),
            )

        # Idempotent retry for the same buyer.
        return existing

    result = trust_agent.mint_certificate(artisan["name"], payload["product_id"], payload["buyer_name"])
    result["artisan_id"] = payload["artisan_id"]
    result["buyer_name"] = payload["buyer_name"]
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


def _find_certificate_by_product(product_id: str) -> dict | None:
    for cert in state.provenance_certificates.values():
        if cert.get("product_id") == product_id:
            return cert

    if not supabase_service.enabled:
        return None

    cert = supabase_service.fetch_one(settings.supabase_certificates_table, product_id=product_id)
    if cert and cert.get("certificate_id"):
        state.provenance_certificates[cert["certificate_id"]] = cert
    return cert
