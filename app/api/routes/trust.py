"""Trust endpoints."""
from fastapi import APIRouter

try:
    from app.schemas.platform import (
        EscrowCreateRequest,
        EscrowReleaseResponse,
        ProvenanceRequest,
        ProvenanceResponse,
    )
    from app.services.platform_service import create_escrow_contract, mint_provenance, release_escrow
except ModuleNotFoundError:
    from schemas.platform import (
        EscrowCreateRequest,
        EscrowReleaseResponse,
        ProvenanceRequest,
        ProvenanceResponse,
    )
    from services.platform_service import create_escrow_contract, mint_provenance, release_escrow


router = APIRouter()


@router.post("/provenance", response_model=ProvenanceResponse)
async def provenance(payload: ProvenanceRequest):
    return mint_provenance(payload.model_dump())


@router.post("/escrow/contracts", response_model=EscrowCreateRequest)
async def create_contract(payload: EscrowCreateRequest):
    return create_escrow_contract(payload.model_dump())


@router.post("/escrow/contracts/{order_id}/release/{milestone_name}", response_model=EscrowReleaseResponse)
async def release_contract(order_id: str, milestone_name: str):
    return release_escrow(order_id, milestone_name)
