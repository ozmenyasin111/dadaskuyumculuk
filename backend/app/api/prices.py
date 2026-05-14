from dataclasses import asdict

from fastapi import APIRouter

from app.schemas.price import PariteOut, PriceRowOut, PriceSnapshotOut
from app.services.cache import cache

router = APIRouter()


@router.get("", response_model=PriceSnapshotOut)
async def get_prices() -> PriceSnapshotOut:
    state = cache.get_prices()
    return PriceSnapshotOut(
        fiyatlar=[PriceRowOut(**asdict(r)) for r in state.rows],
        pariteler=[PariteOut(**p) for p in state.pariteler],
        guncellendi=state.guncellendi,
        healthy=state.healthy,
    )
