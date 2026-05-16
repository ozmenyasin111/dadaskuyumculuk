from fastapi import APIRouter, HTTPException, status
from sqlalchemy import select

from app.api.deps import CurrentUserDep, DbDep
from app.models import MarginSetting
from app.schemas.margin import MarginOut, MarginUpdateIn
from app.services.bootstrap import hydrate_settings_cache

router = APIRouter()


@router.get("", response_model=list[MarginOut])
async def list_margins(_user: CurrentUserDep, db: DbDep) -> list[MarginOut]:
    rows = await db.scalars(
        select(MarginSetting).order_by(MarginSetting.category, MarginSetting.sort_order)
    )
    return [MarginOut.model_validate(r) for r in rows]


@router.put("/{margin_id}", response_model=MarginOut)
async def update_margin(
    margin_id: int, payload: MarginUpdateIn, _user: CurrentUserDep, db: DbDep
) -> MarginOut:
    row = await db.get(MarginSetting, margin_id)
    if not row:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "kayıt bulunamadı")
    if row.is_readonly:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "salt-okunur satır düzenlenemez")
    row.alis_offset = payload.alis_offset
    row.satis_offset = payload.satis_offset
    if payload.classic_alis_offset is not None:
        row.classic_alis_offset = payload.classic_alis_offset
    if payload.classic_satis_offset is not None:
        row.classic_satis_offset = payload.classic_satis_offset
    await db.commit()
    await db.refresh(row)
    await hydrate_settings_cache()  # worker bir sonraki tick'te yeni offset'leri görür
    return MarginOut.model_validate(row)
