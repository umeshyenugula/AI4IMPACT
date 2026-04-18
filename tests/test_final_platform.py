"""Smoke tests for the unified platform service layer."""
import pytest

from fastapi import HTTPException

from app.services.platform_service import (
    create_artisan,
    create_escrow_contract,
    dashboard_summary,
    get_market_pivots,
    mint_provenance,
    release_escrow,
)


def test_artisan_creation_and_market_flow():
    artisan = create_artisan(
        {
            "name": "Amina Noor",
            "email": "amina@example.com",
            "region": "Kashmir",
            "village": "Ganderbal",
            "craft_tradition": "Pashmina Weaving",
        }
    )
    pivots = get_market_pivots(artisan["id"])
    assert artisan["id"] >= 1
    assert pivots


def test_provenance_and_escrow_flow():
    artisan = create_artisan(
        {
            "name": "Rafiq Ali",
            "email": "rafiq@example.com",
            "region": "Ladakh",
            "village": "Leh",
            "craft_tradition": "Pashmina Weaving",
        }
    )
    certificate = mint_provenance(
        {"artisan_id": artisan["id"], "product_id": "shawl-001", "buyer_name": "Azure Hotels"}
    )
    create_escrow_contract(
        {
            "order_id": "order-100",
            "artisan_id": artisan["id"],
            "buyer_name": "Azure Hotels",
            "total_amount_usd": 1000.0,
            "milestones": [{"name": "loom-complete", "payout_pct": 50.0}],
        }
    )
    released = release_escrow("order-100", "loom-complete")
    assert certificate["certificate_id"]
    assert len(released["payouts"]) == 3


def test_dashboard_summary_shape():
    summary = dashboard_summary()
    assert set(summary) == {
        "artisans",
        "portfolio_items",
        "learning_paths",
        "provenance_certificates",
        "escrow_contracts",
    }


def test_provenance_rejects_second_buyer_for_same_product():
    artisan = create_artisan(
        {
            "name": "Kiran Devi",
            "email": "kiran@example.com",
            "region": "Rajasthan",
            "village": "Jodhpur",
            "craft_tradition": "Block Printing",
        }
    )

    mint_provenance(
        {"artisan_id": artisan["id"], "product_id": "sku-royal-print-09", "buyer_name": "Buyer One"}
    )

    with pytest.raises(HTTPException) as exc:
        mint_provenance(
            {"artisan_id": artisan["id"], "product_id": "sku-royal-print-09", "buyer_name": "Buyer Two"}
        )

    assert exc.value.status_code == 409
