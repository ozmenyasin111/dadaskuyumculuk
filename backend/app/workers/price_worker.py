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
from app.services.altinapi import AltinapiError
from app.services.failover import (
    apply_failover,
    check_total_freeze,
    patch_from_secondary,
    unfilled_primaries,
)
from app.services.provider import (
    AllProvidersDown,
    active_provider,
    fetch_prices_with_failover,
    fetch_secondary,
)
from app.services.notify import notify_telegram
from app.services.processor import PriceRow, compute_prices, extract_pariteler

log = logging.getLogger("price_worker")

TR_TZ = ZoneInfo("Europe/Istanbul")
PARITE_KEY_PREFIX = "PARITE."

# Son geçerli ham değerler: kategori -> sembol -> {bid, ask}.
# finansveri bir sembolü 0/eksik döndürdüğünde (sunucu arızası) satırı düşürmek
# yerine bununla doldururuz → ekran asla boşalmaz (müşteri "2 değer kaldı" sorununu
# bir daha görmez). Süreç içinde tutulur; restart sonrası ilk geçerli tick'le dolar.
_last_good_raw: dict[str, dict[str, dict]] = {}

# Eksik-veri durumu: sadece "başladı"/"düzeldi" anlarında loglamak için (her tick
# spam'ını önler). active=şu an doldurma var mı, since=ne zaman başladı.
_backfill_state: dict[str, object] = {"active": False, "since": None}


def _is_valid_raw(v: object) -> bool:
    """bid ve ask var mı ve ikisi de > 0 mı?"""
    if not isinstance(v, dict):
        return False
    bid = v.get("bid")
    ask = v.get("ask")
    try:
        return bid is not None and ask is not None and float(bid) > 0 and float(ask) > 0
    except (TypeError, ValueError):
        return False


def _backfill_fiyatlar(fiyatlar: dict) -> list[str]:
    """Gelen geçerli değerleri `_last_good_raw`'a kaydeder; eksik/0 olan sembolleri
    son geçerli değerle doldurur. Doldurulan `KATEGORI.SEMBOL` listesini döner (log için).
    `fiyatlar` yerinde değiştirilir; geçerli (canlı) değerlere asla dokunulmaz."""
    # 1) Bu tick'teki geçerli değerleri son-iyi deposuna yaz
    for cat, node in fiyatlar.items():
        if not isinstance(node, dict):
            continue
        store = _last_good_raw.setdefault(cat, {})
        for sym, v in node.items():
            if _is_valid_raw(v):
                store[sym] = {"bid": float(v["bid"]), "ask": float(v["ask"])}

    # 2) Eksik/0 gelen sembolleri son-iyi değerle doldur
    backfilled: list[str] = []
    for cat, store in _last_good_raw.items():
        node = fiyatlar.get(cat)
        if not isinstance(node, dict):
            node = {}
            fiyatlar[cat] = node
        for sym, good in store.items():
            if not _is_valid_raw(node.get(sym)):
                node[sym] = dict(good)
                backfilled.append(f"{cat}.{sym}")
    return backfilled


def _fmt(v: object) -> str:
    """Bildirim için sayı biçimi: küçük değerler 4 hane, büyükler 2 hane."""
    try:
        f = float(v)
    except (TypeError, ValueError):
        return "?"
    return f"{f:,.4f}" if abs(f) < 100 else f"{f:,.2f}"


def _notify_failover_event(ev: dict) -> None:
    """Failover geçiş/geri-dönüş olayını log + Telegram'a yazar."""
    now_tr = datetime.now(TR_TZ)
    hhmm = now_tr.strftime("%H:%M:%S")
    if ev["type"] == "switch":
        mins = (ev.get("primary_age") or 0) // 60
        log.warning(
            "failover: %s ana kaynak (%s) ~%d dk donuk → alternatif %s'e geçildi",
            ev["name"], ev["primary"], mins, ev["alt"],
        )
        msg = (
            f"🔁 Dadaş ({hhmm}): \"{ev['name']}\" ana kaynağı {ev['primary']} "
            f"~{mins} dk donuk → alternatif {ev['alt']}'e geçildi.\n"
            f"Ana (donuk): alış {_fmt(ev['old_bid'])} / satış {_fmt(ev['old_ask'])}\n"
            f"Alternatif : alış {_fmt(ev['new_bid'])} / satış {_fmt(ev['new_ask'])}\n"
            f"(site fiyatı artık alternatif + admin kârı ile hesaplanıyor)"
        )
    else:  # recover
        dur = ev.get("dur_sec", 0)
        log.warning(
            "failover: %s ana kaynak (%s) düzeldi (%d sn sürdü) — ana kaynağa dönüldü",
            ev["name"], ev["primary"], dur,
        )
        msg = (
            f"✅ Dadaş ({hhmm}): \"{ev['name']}\" ana kaynağa ({ev['primary']}) döndü "
            f"({dur} sn alternatifte kaldı).\n"
            f"Ana (canlı): alış {_fmt(ev['new_bid'])} / satış {_fmt(ev['new_ask'])}"
        )
    asyncio.create_task(notify_telegram(msg))


def _notify_total_freeze_event(ev: dict) -> None:
    """Toptan-donma başla/düzeldi olayını log + Telegram'a yazar."""
    now_tr = datetime.now(TR_TZ)
    hhmm = now_tr.strftime("%H:%M:%S")
    thr_min = int(settings.total_freeze_threshold_seconds // 60)
    if ev["type"] == "total_freeze_start":
        age = ev.get("freshest_age_sec")
        age_txt = f"en taze sembol bile ~{age // 60} dk eski" if age is not None else "hiçbir sembol okunamıyor"
        log.error("TOPTAN DONMA (%s) — tüm ana+alternatif kaynaklar donuk (%s)", hhmm, age_txt)
        msg = (
            f"🚨 Dadaş ({hhmm}): TÜM kaynaklar donuk! Ana ve alternatif sembollerin "
            f"hepsi ~{thr_min} dk'dır güncellenmiyor ({age_txt}). finansveri toptan "
            f"arızalı olabilir — site eski fiyat gösteriyor, alternatif de yok."
        )
    else:  # total_freeze_recover
        dur = ev.get("dur_sec", 0)
        log.warning("TOPTAN DONMA DÜZELDİ (%s) — %d sn sürdü", hhmm, dur)
        msg = (
            f"✅ Dadaş ({hhmm}): Besleme düzeldi — fiyatlar yeniden canlı "
            f"({dur} sn toptan donuk kaldı)."
        )
    asyncio.create_task(notify_telegram(msg))


def _notify_cross_provider_event(ev: dict) -> None:
    """Tek-sembol cross-provider patch bildirimi: bir ürün finansveri'de (kendisi+ikizi)
    donuk olduğu için sadece o ürün altinapi'den çekildi."""
    now_tr = datetime.now(TR_TZ)
    hhmm = now_tr.strftime("%H:%M:%S")
    log.warning(
        "cross-provider: %s (%s) finansveri'de donuk (kendisi+ikizi) → altinapi'den çekildi",
        ev["name"], ev["primary"],
    )
    msg = (
        f"🔧 Dadaş ({hhmm}): \"{ev['name']}\" finansveri'de donuk (hem kendisi hem ikizi) "
        f"→ SADECE bu ürün altinapi'den çekildi (diğerleri finansveri'de).\n"
        f"Eski (donuk): alış {_fmt(ev['old_bid'])} / satış {_fmt(ev['old_ask'])}\n"
        f"altinapi    : alış {_fmt(ev['new_bid'])} / satış {_fmt(ev['new_ask'])}"
    )
    asyncio.create_task(notify_telegram(msg))


def _notify_provider_event(ev: dict) -> None:
    """Sağlayıcı geçişi (finansveri↔altinapi) başla/geri-dönüş bildirimini yazar."""
    now_tr = datetime.now(TR_TZ)
    hhmm = now_tr.strftime("%H:%M:%S")
    if ev["type"] == "switch":  # → altinapi
        reason = ev.get("reason", "arıza")
        log.error("SAĞLAYICI GEÇİŞİ (%s): finansveri %s → altinapi", hhmm, reason)
        msg = (
            f"🔄 Dadaş ({hhmm}): finansveri {reason} → YEDEK kaynağa (altinapi) geçildi. "
            f"Site altinapi verisiyle çalışmaya devam ediyor (fiyatlar canlı, marj/failover aktif)."
        )
    else:  # recover → finansveri
        log.warning("SAĞLAYICI GERİ DÖNÜŞ (%s): finansveri düzeldi → ana kaynağa dönüldü", hhmm)
        msg = (
            f"✅ Dadaş ({hhmm}): finansveri düzeldi → ANA kaynağa (finansveri) geri dönüldü."
        )
    asyncio.create_task(notify_telegram(msg))


async def _tick() -> None:
    try:
        payload, provider_name, prov_events = await fetch_prices_with_failover()
    except AllProvidersDown as exc:
        log.warning("worker: tüm sağlayıcılar başarısız: %s", exc)
        await cache.mark_unhealthy()
        return

    # Sağlayıcı geçişi/geri-dönüşü olduysa Telegram'a haber ver.
    for ev in prov_events:
        _notify_provider_event(ev)

    fiyatlar = payload.get("fiyatlar", {})
    guncellendi = payload.get("guncellendi", 0)

    # Tek-sembol cross-provider patch: finansveri aktifken bir ürün HEM kendisi HEM ikizi
    # donuksa (finansveri o ürünü besleyemiyor), sadece o ürünü altinapi'den çek. Diğer
    # ürünler finansveri'de kalır → altinapi kotası korunur (yalnız boşluk varken 1 çağrı).
    if provider_name == "finansveri":
        unfilled = unfilled_primaries(fiyatlar)
        if unfilled:
            try:
                sec = await fetch_secondary()
                for ev in patch_from_secondary(fiyatlar, sec.get("fiyatlar", {}), unfilled):
                    _notify_cross_provider_event(ev)
            except AltinapiError as exc:
                log.warning("worker: cross-provider patch için altinapi alınamadı: %s", exc)

    # "Toptan donma" kontrolü (failover fiyatlar'ı ezmeden ÖNCE): aktif sağlayıcının
    # ana+alternatif tüm kaynaklarının en tazesi bile eşikten eskiyse → tek seferlik alarm
    # (artık ancak İKİ sağlayıcı birden ölürse tetiklenir).
    tf = check_total_freeze(fiyatlar)
    if tf is not None:
        _notify_total_freeze_event(tf)

    # Donuk (timestamp eski) ana kaynakları taze alternatifle değiştir — compute'tan
    # ÖNCE, böylece marjlar alternatif değere normal eklenir. Geçiş/dönüş anlarında
    # Telegram bildirimi at (her tick spam'ı yok; sadece olay anında).
    for ev in apply_failover(fiyatlar):
        _notify_failover_event(ev)

    # finansveri 0/eksik döndüyse satırları düşürmemek için son geçerli değerle doldur.
    # Loglama sadece durum değişiminde: "başladı" ve "düzeldi" (her tick spam'ı yok).
    backfilled = _backfill_fiyatlar(fiyatlar)
    now_tr = datetime.now(TR_TZ)
    if backfilled and not _backfill_state["active"]:
        _backfill_state["active"] = True
        _backfill_state["since"] = now_tr
        hhmm = now_tr.strftime("%H:%M:%S")
        log.warning(
            "finansveri EKSİK veri BAŞLADI (%s) — son değer gösteriliyor (%d sembol): %s",
            hhmm, len(backfilled), ", ".join(sorted(backfilled)),
        )
        asyncio.create_task(notify_telegram(
            f"⚠️ Dadaş: finansveri eksik veri ({hhmm}) — {len(backfilled)} sembol son "
            f"değerle gösteriliyor.\n{', '.join(sorted(backfilled))}"
        ))
    elif not backfilled and _backfill_state["active"]:
        since = _backfill_state["since"]
        dur = int((now_tr - since).total_seconds()) if since else 0
        _backfill_state["active"] = False
        _backfill_state["since"] = None
        hhmm = now_tr.strftime("%H:%M:%S")
        log.warning(
            "finansveri veri DÜZELDİ (%s) — tüm semboller canlı (%d sn sürdü)",
            hhmm, dur,
        )
        asyncio.create_task(notify_telegram(
            f"✅ Dadaş: finansveri düzeldi ({hhmm}) — tüm fiyatlar canlı ({dur} sn sürdü)."
        ))

    s = cache.get_settings()
    rows = compute_prices(
        fiyatlar,
        s.margins,
        s.volatility,
        baseline=cache.get_baseline_map(),
        pricing_mode=s.pricing_mode,
    )

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
        # Dinamik aralık: finansveri'deyken hızlı (1 sn), altinapi'deyken yavaş (3 sn,
        # Starter 30/dk kotası). Aktif sağlayıcıya göre seçilir.
        interval = (
            settings.poll_interval_seconds
            if active_provider() == "finansveri"
            else settings.altinapi_poll_interval_seconds
        )
        await asyncio.sleep(interval)


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
