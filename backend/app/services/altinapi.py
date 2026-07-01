"""altinapi.com REST istemcisi (finansveri'nin yerine, 2026-06-30).

altinapi yanıtı DÜZ dizidir:
    {"data": [{"symbol","category","bid","ask","timestamp",...}], "updatedAt", "stale"}

Kodun geri kalanı (symbol_map/processor/failover) eski finansveri formatını
(`fiyatlar[KATEGORI][SEMBOL] = {bid, ask, timestamp}`) beklediği için burada
düz diziyi o iç içe yapıya ÇEVİRİYORUZ. Böylece downstream hiç değişmeden çalışır.

Önemli: per-sembol `timestamp` alanı `+03:00` offset'li ve güvenilir; `timestamp_utc`
bazı sembollerde yanlış (TR saatini Z ile) etiketli — onu KULLANMA.

Rate limit: Free Trial 1000/ay (header `x-ratelimit-*`). Bu yüzden poll aralığı
seyrek tutulur (config `poll_interval_seconds`). 429 olursa backoff.
"""

import asyncio
import logging
from datetime import datetime

import httpx

from app.config import settings

log = logging.getLogger("altinapi")


class AltinapiError(Exception):
    pass


def _to_ms(updated_at: object) -> int:
    """ISO 8601 (ör. '2026-06-30T13:13:16.639Z') → epoch ms. Çözülemezse 0."""
    if not isinstance(updated_at, str):
        return 0
    try:
        dt = datetime.fromisoformat(updated_at.replace("Z", "+00:00"))
        return int(dt.timestamp() * 1000)
    except ValueError:
        return 0


def _transform(payload: dict) -> dict:
    """altinapi düz `data` dizisini finansveri iç içe `fiyatlar` yapısına çevirir."""
    fiyatlar: dict[str, dict] = {}
    for r in payload.get("data", []):
        if not isinstance(r, dict):
            continue
        cat = r.get("category")
        sym = r.get("symbol")
        if not cat or not sym:
            continue
        bid = r.get("bid")
        ask = r.get("ask")
        if bid is None or ask is None:
            continue
        fiyatlar.setdefault(cat, {})[sym] = {
            "bid": bid,
            "ask": ask,
            # +03:00 offset'li güvenilir alan (timestamp_utc DEĞİL).
            "timestamp": r.get("timestamp"),
        }
    return {
        "fiyatlar": fiyatlar,
        "guncellendi": _to_ms(payload.get("updatedAt")),
    }


async def fetch_prices() -> dict:
    """`{fiyatlar, guncellendi}` döner (finansveri formatı). Başarısızsa AltinapiError."""
    url = f"{settings.altinapi_base_url}/prices"
    headers = {"X-API-Key": settings.altinapi_api_key}

    wait_ms = 1000
    last_err: Exception | None = None
    async with httpx.AsyncClient(timeout=10.0) as client:
        for attempt in range(4):
            try:
                resp = await client.get(url, headers=headers)
                if resp.status_code == 429:
                    log.warning("altinapi 429 (rate limit), retrying in %dms", wait_ms)
                    await asyncio.sleep(wait_ms / 1000)
                    wait_ms *= 2
                    continue
                resp.raise_for_status()
                return _transform(resp.json())
            except (httpx.HTTPError, ValueError) as exc:
                last_err = exc
                log.warning("altinapi fetch error (attempt %d): %s", attempt, exc)
                await asyncio.sleep(wait_ms / 1000)
                wait_ms *= 2
    raise AltinapiError(f"failed after retries: {last_err}")
