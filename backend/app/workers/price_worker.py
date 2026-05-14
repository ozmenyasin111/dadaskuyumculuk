"""Arka plan worker: 1 sn aralıkla API çek → processor → cache → broadcast.

Gece yarısında (TR saati) baseline yenilenip `daily_baselines` tablosuna yazılır;
yüzdeler haremaltin.com'daki gibi günlük değişim olarak gösterilir. Readonly margin
satırları ve PARITE sembolleri de baseline tutar (Kuyumcu Paneli + Pariteler bölümü
için pct/trend).
"""

import asyncio
import logging
from datetime import date, datetime
from decimal import Decimal
from zoneinfo import ZoneInfo

from sqlalchemy.dialects.postgresql import insert as pg_insert

from app.config import settings
from app.db.session import SessionLocal
from app.models import DailyBaseline
from app.services.bootstrap import hydrate_baselines_cache, hydrate_settings_cache
from app.services.broadcaster import broadcast_prices
from app.services.cache import BaselineEntry, cache
from app.services.finansveri import FinansveriError, fetch_prices
from app.services.processor import PriceRow, compute_prices, extract_pariteler

log = logging.getLogger("price_worker")

TR_TZ = ZoneInfo("Europe/Istanbul")
PARITE_KEY_PREFIX = "PARITE."


async def _tick() -> None:
    try:
        payload = await fetch_prices()
    except FinansveriError as exc:
        log.warning("worker: fetch başarısız: %s", exc)
        await cache.mark_unhealthy()
        return

    fiyatlar = payload.get("fiyatlar", {})
    guncellendi = payload.get("guncellendi", 0)

    s = cache.get_settings()
    rows = compute_prices(fiyatlar, s.margins, s.volatility, baseline=cache.get_baseline_map())

    # Parite baseline: aynı tabloda "PARITE.{sym}" prefix ile saklanır
    parite_baselines = {
        k[len(PARITE_KEY_PREFIX):]: v
        for k, v in cache.get_baseline_map().items()
        if k.startswith(PARITE_KEY_PREFIX)
    }
    pariteler = extract_pariteler(fiyatlar, baseline=parite_baselines)

    await cache.update_prices(rows, pariteler, guncellendi)

    try:
        await _refresh_baselines_if_new_day(rows, pariteler)
    except Exception:
        log.exception("baseline refresh hatası — bu tick atlanıyor")

    await broadcast_prices()


async def _refresh_baselines_if_new_day(
    rows: list[PriceRow], pariteler: list[dict]
) -> None:
    today_tr: date = datetime.now(TR_TZ).date()
    today_iso = today_tr.isoformat()
    entries = cache.get_baseline_entries()
    updates: dict[str, BaselineEntry] = {}

    for r in rows:
        existing = entries.get(r.symbol_key)
        if existing is None or existing.date != today_iso:
            updates[r.symbol_key] = BaselineEntry(alis=r.alis, date=today_iso)

    for p in pariteler:
        key = f"{PARITE_KEY_PREFIX}{p['symbol']}"
        existing = entries.get(key)
        if existing is None or existing.date != today_iso:
            updates[key] = BaselineEntry(alis=p["bid"], date=today_iso)

    if not updates:
        return

    async with SessionLocal() as db:
        for sym, e in updates.items():
            alis_dec = Decimal(str(e.alis))
            stmt = pg_insert(DailyBaseline).values(
                symbol_key=sym,
                baseline_date=today_tr,
                baseline_alis=alis_dec,
            ).on_conflict_do_update(
                index_elements=["symbol_key"],
                set_={
                    "baseline_date": today_tr,
                    "baseline_alis": alis_dec,
                },
            )
            await db.execute(stmt)
        await db.commit()
    await cache.upsert_baselines(updates)
    log.info("baseline %d sembol için güncellendi (%s)", len(updates), today_iso)


async def _loop() -> None:
    await hydrate_settings_cache()
    await hydrate_baselines_cache()
    log.info("worker döngüsü başladı, interval=%s sn", settings.poll_interval_seconds)
    while True:
        try:
            await _tick()
        except Exception:
            log.exception("tick sırasında hata — bir sonraki tick'te devam ediliyor")
        await asyncio.sleep(settings.poll_interval_seconds)


async def start_price_worker() -> asyncio.Task:
    return asyncio.create_task(_loop(), name="price-worker")


async def stop_price_worker(task: asyncio.Task) -> None:
    task.cancel()
    try:
        await task
    except asyncio.CancelledError:
        pass
    except Exception:
        log.exception("price worker shutdown sırasında hata")
