from fastapi import APIRouter, HTTPException, status

from app.api.deps import CurrentUserDep, DbDep
from app.models import PricingConfig
from app.schemas.pricing_mode import PricingModeOut, PricingModeUpdateIn
from app.services.bootstrap import hydrate_settings_cache

router = APIRouter()


@router.get("", response_model=PricingModeOut)
async def get_pricing_mode(_user: CurrentUserDep, db: DbDep) -> PricingModeOut:
    cfg = await db.get(PricingConfig, 1)
    if not cfg:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "pricing config eksik")
    return PricingModeOut.model_validate(cfg)


@router.put("", response_model=PricingModeOut)
async def update_pricing_mode(
    payload: PricingModeUpdateIn, _user: CurrentUserDep, db: DbDep
) -> PricingModeOut:
    cfg = await db.get(PricingConfig, 1)
    if not cfg:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "pricing config eksik")
    cfg.mode = payload.mode
    await db.commit()
    await db.refresh(cfg)
    await hydrate_settings_cache()
    return PricingModeOut.model_validate(cfg)
