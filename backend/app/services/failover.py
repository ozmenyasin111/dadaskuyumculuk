"""Bayatlık (staleness) bazlı kaynak failover'ı.

finansveri bir sembolü 0/eksik DEĞİL ama "donuk" (timestamp eski) döndürebiliyor:
değer >0 olduğu için `_backfill_fiyatlar` bunu yakalamaz ve ekranda saatlerce eski
fiyat kalır. Bu modül her tick'te ana kaynakların timestamp yaşına bakar; eşikten
eskiyse, değeri neredeyse aynı olan **taze alternatif** sembolle değiştirir.

Değiştirme `fiyatlar` üzerinde (compute'tan ÖNCE) yapılır → `compute_prices` değişmez,
admin marjları normal eklenir, site alternatif tabanlı canlı fiyatı gösterir. Geçiş ve
geri dönüş anlarında Telegram bildirimi için olay listesi döndürülür.

Eşik: altın/sarrafiye/maden = `stale_threshold_gold_seconds` (10 dk),
döviz (DOVIZ.*) = `stale_threshold_doviz_seconds` (10 dk).
"""

import logging
from datetime import datetime, timezone

from app.config import settings

log = logging.getLogger("failover")

# (Sitedeki ad, ana kaynak "KATEGORI.SEMBOL", [(alternatif, ölçek), ...]).
# Ölçek: alternatif değer bu sayıya bölünerek ana kaynakla aynı birime getirilir
# (sadece DS_PARUSD / DS_GUMUSUSD ×1000 saklandığı için 1000, diğerleri 1).
FAILOVER_MAP: list[tuple[str, str, list[tuple[str, float]]]] = [
    ("Gram Altın", "SARRAFIYE.KULCEALTIN", [("DOVIZ.DS_KULCEALTIN", 1)]),
    ("Bilezik (22 Ayar)", "SARRAFIYE.AYAR22", [("DOVIZ.DS_22AYAR", 1)]),
    ("14 Ayar", "SARRAFIYE.AYAR14", [("DOVIZ.DS_14AYAR", 1)]),
    ("Yeni Çeyrek", "SARRAFIYE.CEYREK_YENI", [("DOVIZ.DS_CEYREK_YENI", 1)]),
    ("Eski Çeyrek", "SARRAFIYE.CEYREK_ESKI", [("DOVIZ.DS_CEYREK_YENI", 1)]),
    ("Yeni Yarım", "SARRAFIYE.YARIM_YENI", [("DOVIZ.DS_YARIM_YENI", 1)]),
    ("Eski Yarım", "SARRAFIYE.YARIM_ESKI", [("DOVIZ.DS_YARIM_YENI", 1)]),
    ("Yeni Tam", "SARRAFIYE.TEK_YENI", [("DOVIZ.DS_TEK_YENI", 1)]),
    ("Eski Tam", "SARRAFIYE.TEK_ESKI", [("DOVIZ.DS_TEK_YENI", 1)]),
    ("Ata (Cumhuriyet) alış kaynağı", "SARRAFIYE.ATA_ESKI", [("DOVIZ.DS_ATA_YENI", 1)]),
    ("Ata (Cumhuriyet) satış kaynağı", "SARRAFIYE.ATA_YENI", [("DOVIZ.DS_ATA_YENI", 1)]),
    ("Ata 5'li", "SARRAFIYE.ATA5_YENI", [("DOVIZ.DS_ATA5_YENI", 1)]),
    ("Yeni Gremse", "SARRAFIYE.GREMESE_YENI", [("DOVIZ.DS_GREMESE_YENI", 1)]),
    ("Eski Gremse", "SARRAFIYE.GREMESE_ESKI", [("DOVIZ.DS_GREMESE_YENI", 1)]),
    ("Gümüş (Kg)", "MADEN.GUMTRY", [("MADEN.GUMUSTRY", 1)]),
    ("USD/TRY", "DOVIZ.USDTRY", [("DOVIZ.DS_USDTRY", 1)]),
    ("EUR/TRY", "DOVIZ.EURTRY", [("DOVIZ.DS_EURTRY", 1)]),
    ("EUR/USD", "DOVIZ.EURUSDS", [("DOVIZ.DS_EURUSD", 1)]),
    ("GBP/TRY", "DOVIZ.GBPTRY", [("DOVIZ.DS_GBPTRY", 1)]),
    ("CHF/TRY", "DOVIZ.CHFTRY", [("DOVIZ.DS_CHFTRY", 1)]),
    ("SAR/TRY", "DOVIZ.SARTRY", [("DOVIZ.DS_SARTRY", 1)]),
    ("Has Altın (Ham)", "GRAM ALTIN.ALTIN", [("MADEN.DS_ALTIN", 1)]),
    ("Ons Altın", "MADEN.XAUUSD", [("MADEN.DS_ALTIN_XAUUSD", 1)]),
    ("Kg Altın USD", "MADEN.PARUSD", [("DOVIZ.DS_PARUSD", 1000)]),
    ("Altın/Gümüş Rasyo", "MADEN.XAUXAG", [("MADEN.DS_XAUXAG", 1)]),
    ("Ons Gümüş", "MADEN.XAGUSD", [("MADEN.DS_XAGUSD", 1)]),
    ("Gümüş Kg USD", "MADEN.GUMUSD", [("DOVIZ.DS_GUMUSUSD", 1000)]),
]

# Aktif failover durumu: ana kaynak -> {"alt", "since"(datetime), "name"}.
# Sadece geçiş/geri-dönüş anlarında bildirim atmak için tutulur (her tick spam'ı yok).
_state: dict[str, dict] = {}

# Toptan-donma durumu: {"active": bool, "since": datetime|None}.
_total_freeze_state: dict[str, object] = {"active": False, "since": None}

# Sembole özel bayatlık eşiği (saniye) — kategori varsayılanını ezer. USD/SAR non-DS
# beslemesi yavaş/aralıklı güncellendiği için (USD ~2-5 dk, SAR ~9-18 dk) standart 5 dk
# döviz eşiğinde çırpınıp gereksiz geçiş/bildirim üretiyordu → 20 dk. Değer birebir aynı
# olduğu için bu süre boyunca biraz daha eski tick gösterilmesi sorun değil.
PER_SYMBOL_THRESHOLD_SECONDS: dict[str, float] = {
    "DOVIZ.USDTRY": 1200.0,
    "DOVIZ.SARTRY": 1200.0,
}


def _split(key: str) -> tuple[str, str]:
    cat, _, sym = key.partition(".")
    return cat, sym


def _threshold_seconds(primary_key: str) -> float:
    if primary_key in PER_SYMBOL_THRESHOLD_SECONDS:
        return PER_SYMBOL_THRESHOLD_SECONDS[primary_key]
    if primary_key.startswith("DOVIZ."):
        return settings.stale_threshold_doviz_seconds
    return settings.stale_threshold_gold_seconds


def _parse_age_seconds(ts: object, now: datetime) -> float | None:
    """Sembol timestamp'inin yaşı (saniye). Çözülemezse None."""
    if ts is None:
        return None
    try:
        if isinstance(ts, (int, float)):
            secs = ts / 1000.0 if ts > 1e11 else float(ts)
            t = datetime.fromtimestamp(secs, timezone.utc)
        else:
            t = datetime.fromisoformat(str(ts).replace("Z", "+00:00"))
            if t.tzinfo is None:
                t = t.replace(tzinfo=timezone.utc)
        return (now - t).total_seconds()
    except (ValueError, OverflowError, OSError):
        return None


def _read(fiyatlar: dict, key: str, now: datetime) -> dict | None:
    """`{bid, ask, age, valid}` döner; sembol yoksa None."""
    cat, sym = _split(key)
    node = fiyatlar.get(cat)
    if not isinstance(node, dict):
        return None
    r = node.get(sym)
    if not isinstance(r, dict):
        return None
    bid = r.get("bid")
    ask = r.get("ask")
    try:
        bid_f = float(bid) if bid is not None else None
        ask_f = float(ask) if ask is not None else None
    except (TypeError, ValueError):
        return None
    valid = bid_f is not None and ask_f is not None and bid_f > 0 and ask_f > 0
    return {
        "bid": bid_f,
        "ask": ask_f,
        "age": _parse_age_seconds(r.get("timestamp"), now),
        "valid": valid,
    }


def apply_failover(fiyatlar: dict, now: datetime | None = None) -> list[dict]:
    """Donuk ana kaynakları taze alternatifle değiştirir (yerinde). Geçiş/geri-dönüş
    olaylarını döndürür: {type, name, primary, alt, dur_sec, old_bid, old_ask,
    new_bid, new_ask, primary_age}."""
    now = now or datetime.now(timezone.utc)
    events: list[dict] = []

    for name, primary, alts in FAILOVER_MAP:
        thr = _threshold_seconds(primary)
        cur = _read(fiyatlar, primary, now)
        # "Donuk": değer yok/geçersiz, ya da timestamp eşikten eski.
        primary_stale = (
            cur is None
            or not cur["valid"]
            or cur["age"] is None
            or cur["age"] > thr
        )

        if not primary_stale:
            # Ana kaynak taze. Daha önce alternatife geçmişsek geri dön + bildir.
            st = _state.pop(primary, None)
            if st is not None:
                dur = int((now - st["since"]).total_seconds())
                events.append({
                    "type": "recover",
                    "name": name,
                    "primary": primary,
                    "alt": st["alt"],
                    "dur_sec": dur,
                    "new_bid": cur["bid"],
                    "new_ask": cur["ask"],
                })
            continue

        # Ana kaynak donuk → ilk TAZE ve geçerli alternatifi bul.
        chosen = None
        for alt_key, scale in alts:
            av = _read(fiyatlar, alt_key, now)
            if av and av["valid"] and av["age"] is not None and av["age"] <= thr:
                chosen = (alt_key, scale, av)
                break

        if chosen is None:
            # Alternatif de donuk/yok → dokunma (backfill son-iyi değeri korur).
            log.warning(
                "failover: %s ana kaynak donuk ama taze alternatif yok — eski değer korunuyor",
                primary,
            )
            continue

        alt_key, scale, av = chosen
        new_bid = av["bid"] / scale
        new_ask = av["ask"] / scale

        # Donuk ana kaynağın o anki (eski) değerini bildirim için sakla.
        old_bid = cur["bid"] if cur else None
        old_ask = cur["ask"] if cur else None

        # Değeri yerine yaz: compute_prices ana kaynağı okuyunca alternatifi görür.
        cat, sym = _split(primary)
        node = fiyatlar.setdefault(cat, {})
        node[sym] = {"bid": new_bid, "ask": new_ask, "timestamp": None}

        st = _state.get(primary)
        if st is None or st.get("alt") != alt_key:
            # Yeni geçiş (veya farklı alternatife geçiş) → bildir.
            _state[primary] = {"alt": alt_key, "since": now, "name": name}
            events.append({
                "type": "switch",
                "name": name,
                "primary": primary,
                "alt": alt_key,
                "primary_age": int(cur["age"]) if cur and cur["age"] is not None else None,
                "old_bid": old_bid,
                "old_ask": old_ask,
                "new_bid": new_bid,
                "new_ask": new_ask,
            })

    return events


def _alts_for(primary: str) -> list[tuple[str, float]]:
    for _name, prim, alts in FAILOVER_MAP:
        if prim == primary:
            return alts
    return []


def resolve_fresh(fiyatlar: dict, primary: str, now: datetime) -> tuple[float, float] | None:
    """Bir ürün için TAZE (ölçekli) bid/ask döner: önce ana kaynak, sonra alternatifler.
    Hiçbiri taze değilse None. Hem failover hem cross-provider patch bunu kullanır."""
    thr = _threshold_seconds(primary)
    cur = _read(fiyatlar, primary, now)
    if cur and cur["valid"] and cur["age"] is not None and cur["age"] <= thr:
        return (cur["bid"], cur["ask"])
    for alt_key, scale in _alts_for(primary):
        av = _read(fiyatlar, alt_key, now)
        if av and av["valid"] and av["age"] is not None and av["age"] <= thr:
            return (av["bid"] / scale, av["ask"] / scale)
    return None


def unfilled_primaries(fiyatlar: dict, now: datetime | None = None) -> list[tuple[str, str]]:
    """Ne ana kaynağı ne de alternatifi taze olan ürünler [(ad, primary), ...].
    Bunlar bu sağlayıcıdan beslenemiyor → yedek sağlayıcıdan çekilmeli."""
    now = now or datetime.now(timezone.utc)
    out = []
    for name, primary, _alts in FAILOVER_MAP:
        if resolve_fresh(fiyatlar, primary, now) is None:
            out.append((name, primary))
    return out


def patch_from_secondary(
    fiyatlar: dict, secondary: dict, unfilled: list[tuple[str, str]], now: datetime | None = None
) -> list[dict]:
    """`unfilled` ürünleri yedek sağlayıcının (`secondary`) taze değeriyle doldurur.
    Doldurulan her ürün için olay döner (Telegram için)."""
    now = now or datetime.now(timezone.utc)
    events = []
    for name, primary in unfilled:
        val = resolve_fresh(secondary, primary, now)
        if val is None:
            continue  # yedek de veremedi → dokunma (backfill son-iyi değeri korur)
        old = _read(fiyatlar, primary, now)
        cat, sym = _split(primary)
        fiyatlar.setdefault(cat, {})[sym] = {"bid": val[0], "ask": val[1], "timestamp": None}
        events.append({
            "type": "cross_provider",
            "name": name,
            "primary": primary,
            "old_bid": old["bid"] if old else None,
            "old_ask": old["ask"] if old else None,
            "new_bid": val[0],
            "new_ask": val[1],
        })
    return events


def freshest_mapped_age(fiyatlar: dict, now: datetime | None = None) -> float | None:
    """Ana kaynak + alternatif tüm sembollerin EN TAZESİNİN yaşı (saniye). Hiç geçerli
    sembol yoksa None. Sağlayıcı sağlığı için: bu değer eşikten büyükse sağlayıcı ölü."""
    now = now or datetime.now(timezone.utc)
    ages = [
        v["age"]
        for key in _all_mapped_keys()
        if (v := _read(fiyatlar, key, now)) is not None and v["valid"] and v["age"] is not None
    ]
    return min(ages) if ages else None


def _all_mapped_keys() -> list[str]:
    """Haritadaki tüm ana + alternatif sembol anahtarları (tekrarsız)."""
    keys: list[str] = []
    for _name, primary, alts in FAILOVER_MAP:
        keys.append(primary)
        keys.extend(alt_key for alt_key, _scale in alts)
    return list(dict.fromkeys(keys))


def check_total_freeze(fiyatlar: dict, now: datetime | None = None) -> dict | None:
    """Ana + alternatif TÜM kaynakların en tazesi bile eşikten eskiyse "toptan donma"
    olayı döner. Sadece BAŞLA/DÜZELDİ geçişlerinde olay üretir (her tick spam'ı yok).

    Önemli: `apply_failover`'dan ÖNCE çağrılmalı — failover ana kaynakları alternatif
    değeriyle (timestamp=None) ezdiği için sonradan çağrılırsa yaş hesabı bozulur.
    """
    now = now or datetime.now(timezone.utc)
    thr = settings.total_freeze_threshold_seconds

    ages = [
        v["age"]
        for key in _all_mapped_keys()
        if (v := _read(fiyatlar, key, now)) is not None
        and v["valid"]
        and v["age"] is not None
    ]
    # En taze (en küçük yaş) kaynak. Hiç geçerli/çözülebilir kaynak yoksa donmuş say.
    freshest = min(ages) if ages else None
    frozen = freshest is None or freshest > thr

    if frozen and not _total_freeze_state["active"]:
        _total_freeze_state["active"] = True
        _total_freeze_state["since"] = now
        return {
            "type": "total_freeze_start",
            "freshest_age_sec": int(freshest) if freshest is not None else None,
        }
    if not frozen and _total_freeze_state["active"]:
        since = _total_freeze_state["since"]
        dur = int((now - since).total_seconds()) if since else 0
        _total_freeze_state["active"] = False
        _total_freeze_state["since"] = None
        return {"type": "total_freeze_recover", "dur_sec": dur}
    return None


def reset_state() -> None:
    """Testler için durum sıfırlama."""
    _state.clear()
    _total_freeze_state["active"] = False
    _total_freeze_state["since"] = None
