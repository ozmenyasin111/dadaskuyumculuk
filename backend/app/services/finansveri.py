"""api.finansveri.com REST istemcisi.

1 req/sn limit; 429 olursa exponential backoff (1s, 2s, 4s).
"""

import asyncio
import logging

import httpx

from app.config import settings

log = logging.getLogger("finansveri")


class FinansveriError(Exception):
    pass


async def fetch_prices() -> dict:
    """`{fiyatlar, guncellendi}` döner. Başarısız olursa `FinansveriError` fırlatır."""
    url = f"{settings.finansveri_base_url}/v1/fiyatlar"
    headers = {"X-API-Key": settings.finansveri_api_key}

    wait_ms = 1000
    last_err: Exception | None = None
    async with httpx.AsyncClient(timeout=10.0) as client:
        for attempt in range(4):
            try:
                resp = await client.get(url, headers=headers)
                if resp.status_code == 429:
                    log.warning("finansveri 429, retrying in %dms", wait_ms)
                    await asyncio.sleep(wait_ms / 1000)
                    wait_ms *= 2
                    continue
                resp.raise_for_status()
                return resp.json()
            except (httpx.HTTPError, ValueError) as exc:
                last_err = exc
                log.warning("finansveri fetch error (attempt %d): %s", attempt, exc)
                await asyncio.sleep(wait_ms / 1000)
                wait_ms *= 2
    raise FinansveriError(f"failed after retries: {last_err}")
