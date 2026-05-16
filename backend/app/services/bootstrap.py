"""Uygulama açılışında çalışan görevler ve cache hidrasyonu."""

import logging

from sqlalchemy import select

from app.config import settings
from app.db.session import SessionLocal
from app.models import (
    DailyBaseline,
    MarginSetting,
    PricingConfig,
    User,
    VolatilityOverride,
)
from app.services.auth import hash_password
from app.services.cache import BaselineEntry, cache
from app.services.processor import MarginRow, VolatilityRule

log = logging.getLogger("bootstrap")


async def bootstrap_admin_if_missing() -> None:
    async with SessionLocal() as db:
        existing = await db.scalar(select(User).limit(1))
        if existing:
            return
        user = User(
            username=settings.admin_bootstrap_username,
            password_hash=hash_password(settings.admin_bootstrap_password),
        )
        db.add(user)
        await db.commit()
        log.info("bootstrap admin oluşturuldu: %s", settings.admin_bootstrap_username)


async def hydrate_settings_cache() -> None:
    async with SessionLocal() as db:
        margins_res = await db.scalars(
            select(MarginSetting).order_by(MarginSetting.category, MarginSetting.sort_order)
        )
        margins = [
            MarginRow(
                symbol_key=m.symbol_key,
                display_name=m.display_name,
                category=m.category,
                alis_offset=m.alis_offset,
                satis_offset=m.satis_offset,
                sort_order=m.sort_order,
                is_readonly=m.is_readonly,
                is_multiplier=m.is_multiplier,
                classic_alis_offset=m.classic_alis_offset,
                classic_satis_offset=m.classic_satis_offset,
            )
            for m in margins_res
        ]
        vol_res = await db.scalars(select(VolatilityOverride))
        volatility = {
            v.category: VolatilityRule(
                category=v.category,
                threshold=v.threshold,
                alis_override=v.alis_override,
                satis_override=v.satis_override,
                enabled=v.enabled,
            )
            for v in vol_res
        }
        cfg = await db.get(PricingConfig, 1)
        pricing_mode = cfg.mode if cfg else "milyem"
        await cache.set_settings(margins, volatility, pricing_mode)
        log.info(
            "ayarlar belleğe alındı: %d sembol, %d volatility, mode=%s",
            len(margins), len(volatility), pricing_mode,
        )


async def hydrate_baselines_cache() -> None:
    async with SessionLocal() as db:
        res = await db.scalars(select(DailyBaseline))
        entries = {
            b.symbol_key: BaselineEntry(
                alis=float(b.baseline_alis),
                date=b.baseline_date.isoformat(),
            )
            for b in res
        }
        await cache.set_baselines(entries)
        log.info("baselines belleğe alındı: %d sembol", len(entries))
