from fastapi import APIRouter, HTTPException, status
from sqlalchemy import select

from app.api.deps import CurrentUserDep, DbDep
from app.models import VolatilityOverride
from app.schemas.volatility import VolatilityOut, VolatilityUpdateIn
from app.services.bootstrap import hydrate_settings_cache

router = APIRouter()


@router.get("", response_model=list[VolatilityOut])
async def list_volatility(_user: CurrentUserDep, db: DbDep) -> list[VolatilityOut]:
    rows = await db.scalars(select(VolatilityOverride))
    return [VolatilityOut.model_validate(r) for r in rows]


@router.put("/{category}", response_model=VolatilityOut)
async def update_volatility(
    category: str, payload: VolatilityUpdateIn, _user: CurrentUserDep, db: DbDep
) -> VolatilityOut:
    row = await db.scalar(select(VolatilityOverride).where(VolatilityOverride.category == category))
    if not row:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "kategori bulunamadı")
    row.threshold = payload.threshold
    row.alis_override = payload.alis_override
    row.satis_override = payload.satis_override
    row.enabled = payload.enabled
    await db.commit()
    await db.refresh(row)
    await hydrate_settings_cache()
    return VolatilityOut.model_validate(row)
