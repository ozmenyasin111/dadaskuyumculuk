"""İşlenmiş fiyatların ve admin ayarlarının in-memory cache'i.

`baselines` = sembol başına `{date, alis}` — günlük kapanış benzeri referans. Worker
gece yarısında (TR saati) tarih değişimini fark edip günlük baseline'ı `daily_baselines`
tablosuna yazar ve cache'i günceller. Yüzde değişim bu referansa göre hesaplanır.
"""

import asyncio
import time
from dataclasses import dataclass, field

from app.services.processor import MarginRow, PriceRow, VolatilityRule


@dataclass
class BaselineEntry:
    alis: float
    date: str  # ISO date "2026-05-14" (TR günü)


@dataclass
class PriceState:
    rows: list[PriceRow] = field(default_factory=list)
    pariteler: list[dict] = field(default_factory=list)
    guncellendi: int = 0
    last_fetch_ms: int = 0
    healthy: bool = False


@dataclass
class SettingsState:
    margins: list[MarginRow] = field(default_factory=list)
    volatility: dict[str, VolatilityRule] = field(default_factory=dict)
    pricing_mode: str = "milyem"
    version: int = 0


class Cache:
    def __init__(self) -> None:
        self._lock = asyncio.Lock()
        self.prices = PriceState()
        self.settings = SettingsState()
        self._baselines: dict[str, BaselineEntry] = {}

    async def update_prices(
        self, rows: list[PriceRow], pariteler: list[dict], guncellendi: int
    ) -> None:
        async with self._lock:
            self.prices = PriceState(
                rows=rows,
                pariteler=pariteler,
                guncellendi=guncellendi,
                last_fetch_ms=int(time.time() * 1000),
                healthy=True,
            )

    async def mark_unhealthy(self) -> None:
        async with self._lock:
            self.prices = PriceState(
                rows=self.prices.rows,
                pariteler=self.prices.pariteler,
                guncellendi=self.prices.guncellendi,
                last_fetch_ms=self.prices.last_fetch_ms,
                healthy=False,
            )

    async def set_settings(
        self,
        margins: list[MarginRow],
        volatility: dict[str, VolatilityRule],
        pricing_mode: str = "milyem",
    ) -> None:
        async with self._lock:
            self.settings = SettingsState(
                margins=margins,
                volatility=volatility,
                pricing_mode=pricing_mode,
                version=self.settings.version + 1,
            )

    def get_settings(self) -> SettingsState:
        return self.settings

    def get_prices(self) -> PriceState:
        return self.prices

    def get_baseline_map(self) -> dict[str, float]:
        return {k: e.alis for k, e in self._baselines.items()}

    def get_baseline_entries(self) -> dict[str, BaselineEntry]:
        return dict(self._baselines)

    async def set_baselines(self, entries: dict[str, BaselineEntry]) -> None:
        async with self._lock:
            self._baselines = entries

    async def upsert_baselines(self, entries: dict[str, BaselineEntry]) -> None:
        async with self._lock:
            self._baselines.update(entries)


cache = Cache()
