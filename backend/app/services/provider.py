"""Sağlayıcı (provider) bazlı failover: finansveri birincil, altinapi yedek.

İki katmanlı dayanıklılık:
  1. SAĞLAYICI katmanı (bu modül): finansveri çökerse/donarsa tüm sistem altinapi'ye
     geçer, finansveri düzelince geri döner.
  2. SEMBOL katmanı (failover.py): hangi sağlayıcı aktifse onun verisinde tek-sembol
     donması olursa DS_ ikizine geçer. DS_ alternatifleri HER İKİ sağlayıcıda da var.

finansveri "sağlıklı" = fetch başarılı VE `guncellendi` yaşı `provider_stale_seconds`
altında (200 dönüp veriyi dondurma durumunu da yakalar). Değilse altinapi'ye düşülür.

altinapi yalnızca finansveri başarısız/donuk olduğunda çağrılır → Starter (30/dk)
kotası korunur (poll 3 sn = ~20/dk, sadece arıza anında).
"""

import logging
from datetime import datetime, timezone

from app.config import settings
from app.services import altinapi, finansveri
from app.services.failover import freshest_mapped_age

log = logging.getLogger("provider")


class AllProvidersDown(Exception):
    """Hem finansveri hem altinapi başarısız."""


# Aktif sağlayıcı durumu. Başlangıçta finansveri varsayılır; ilk tick gerçeğe göre düzeltir.
_state: dict[str, str] = {"active": "finansveri"}


def reset_state() -> None:
    _state["active"] = "finansveri"


def active_provider() -> str:
    return _state["active"]


async def fetch_secondary() -> dict:
    """Yedek sağlayıcıdan (altinapi) tam paket çeker — tek-sembol cross-provider patch
    için worker tarafından çağrılır. Hata olursa AltinapiError fırlatır."""
    return await altinapi.fetch_prices()


async def fetch_prices_with_failover(
    now: datetime | None = None,
) -> tuple[dict, str, list[dict]]:
    """(`payload`, aktif_sağlayıcı, olaylar) döner. Sağlayıcı geçişi: finansveri hata
    verir YA DA ana kaynak+alternatiflerinin hiçbiri `provider_stale_seconds` içinde
    taze değilse (finansveri bize tek taze sayı veremiyor) → altinapi'ye geçilir."""
    now = now or datetime.now(timezone.utc)
    events: list[dict] = []

    # 1) Birincil: finansveri (hızlı başarısız ol → altinapi'yi geciktirme).
    fv = None
    try:
        fv = await finansveri.fetch_prices(max_attempts=1, timeout=6.0)
    except finansveri.FinansveriError as exc:
        log.warning("provider: finansveri başarısız: %s", exc)

    if fv is not None:
        # Sağlık = ana kaynak + alternatiflerin EN TAZESİ eşik içinde mi?
        freshest = freshest_mapped_age(fv.get("fiyatlar", {}), now)
        if freshest is not None and freshest <= settings.provider_stale_seconds:
            if _state["active"] != "finansveri":
                events.append({"type": "recover", "to": "finansveri", "frm": _state["active"]})
                _state["active"] = "finansveri"
            return fv, "finansveri", events
        log.warning(
            "provider: finansveri'de taze veri yok (en taze %s sn) → altinapi",
            f"{freshest:.0f}" if freshest is not None else "yok",
        )

    # 2) Yedek: altinapi (tüm sistem geçişi).
    try:
        aa = await altinapi.fetch_prices()
    except altinapi.AltinapiError as exc:
        raise AllProvidersDown(f"finansveri+altinapi başarısız: {exc}") from exc

    if _state["active"] != "altinapi":
        reason = "yanıt vermedi" if fv is None else "tüm veri donuk"
        events.append({"type": "switch", "to": "altinapi", "frm": _state["active"], "reason": reason})
        _state["active"] = "altinapi"
    return aa, "altinapi", events
