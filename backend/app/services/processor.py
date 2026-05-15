"""Margin + volatility + milyem (çarpan) kuralı uygulayıp display fiyatları hesaplar.

Mantık:
  1. Has Altın display alış/satış hesaplanır:
        fark = ask - bid
        Has Altın için volatility eligible:
          fark ≥ eşik ve enabled → bid + volatility.alis_override, ask + volatility.satis_override
          değilse → bid + margin.alis_offset, ask + margin.satis_offset
  2. Diğer satırlar için:
        is_multiplier=true → has_altin_display × alis_milyem (alis_offset alanı milyem olarak yorumlanır)
        is_multiplier=false ve is_readonly=false → bid + alis_offset, ask + satis_offset
        is_readonly=true → API ham bid/ask doğrudan
"""

from dataclasses import dataclass
from decimal import Decimal

from app.services.symbol_map import lookup_raw

VOLATILITY_ELIGIBLE_SYMBOLS = {
    "SARRAFIYE.KULCEALTIN",
    "DOVIZ.USDTRY",
    "DOVIZ.EURTRY",
    "DOVIZ.GBPTRY",
    "DOVIZ.CHFTRY",
    "DOVIZ.AUDTRY",
    "DOVIZ.CADTRY",
    "DOVIZ.SARTRY",
    "DOVIZ.EURUSDS",
}

# Milyem (multiplier) hesabı için baz alınan "gram altın" sembolü.
# Sarrafiye'deki Gram Altın satırı bu sembolü kaynak alır, diğer altın ürünleri
# bu satırın display alış/satış değeriyle milyem çarpılarak hesaplanır.
HAS_ALTIN_KEY = "SARRAFIYE.KULCEALTIN"


@dataclass(frozen=True)
class MarginRow:
    symbol_key: str
    display_name: str
    category: str
    alis_offset: Decimal
    satis_offset: Decimal
    sort_order: int
    is_readonly: bool
    is_multiplier: bool = False


@dataclass(frozen=True)
class VolatilityRule:
    category: str
    threshold: Decimal
    alis_override: Decimal
    satis_override: Decimal
    enabled: bool


@dataclass
class PriceRow:
    symbol_key: str
    display_name: str
    category: str
    alis: float
    satis: float
    raw_bid: float
    raw_ask: float
    trend: str
    pct_change: float
    using_volatility: bool
    is_readonly: bool
    sort_order: int


def _has_altin_display(
    fiyatlar: dict,
    has_altin_row: MarginRow | None,
    volatility: dict[str, VolatilityRule],
) -> dict | None:
    """Has Altın display alış/satış hesaplar — multiplier satırlar için referans."""
    if not has_altin_row:
        return None
    raw = lookup_raw(fiyatlar, HAS_ALTIN_KEY)
    if raw is None:
        return None
    bid = raw["bid"]
    ask = raw["ask"]
    fark = ask - bid

    using_volatility = False
    vol = volatility.get("ALTIN")
    if vol and vol.enabled and fark >= float(vol.threshold):
        alis = bid + float(vol.alis_override)
        satis = ask + float(vol.satis_override)
        using_volatility = True
    else:
        alis = bid + float(has_altin_row.alis_offset)
        satis = ask + float(has_altin_row.satis_offset)
    return {
        "alis": alis,
        "satis": satis,
        "raw_bid": bid,
        "raw_ask": ask,
        "using_volatility": using_volatility,
    }


def compute_prices(
    fiyatlar: dict,
    margins: list[MarginRow],
    volatility: dict[str, VolatilityRule],
    baseline: dict[str, float] | None = None,
) -> list[PriceRow]:
    baseline = baseline or {}
    has_altin_row = next((m for m in margins if m.symbol_key == HAS_ALTIN_KEY), None)
    has_altin = _has_altin_display(fiyatlar, has_altin_row, volatility)

    out: list[PriceRow] = []
    for m in margins:
        if m.is_multiplier:
            if has_altin is None:
                continue
            alis = has_altin["alis"] * float(m.alis_offset)
            satis = has_altin["satis"] * float(m.satis_offset)
            raw_bid = has_altin["raw_bid"]
            raw_ask = has_altin["raw_ask"]
            using_volatility = has_altin["using_volatility"]
        else:
            raw = lookup_raw(fiyatlar, m.symbol_key)
            if raw is None:
                continue
            bid = raw["bid"]
            ask = raw["ask"]
            raw_bid = bid
            raw_ask = ask
            using_volatility = False

            if m.is_readonly:
                alis = bid
                satis = ask
            else:
                fark = ask - bid
                vol = volatility.get(m.category)
                eligible = m.symbol_key in VOLATILITY_ELIGIBLE_SYMBOLS
                if vol and vol.enabled and eligible and fark >= float(vol.threshold):
                    alis = bid + float(vol.alis_override)
                    satis = ask + float(vol.satis_override)
                    using_volatility = True
                else:
                    alis = bid + float(m.alis_offset)
                    satis = ask + float(m.satis_offset)

        bl = baseline.get(m.symbol_key)
        if bl is not None and bl != 0:
            pct = (alis - bl) / bl * 100.0
            if alis > bl:
                trend = "up"
            elif alis < bl:
                trend = "down"
            else:
                trend = "flat"
        else:
            pct = 0.0
            trend = "flat"

        out.append(PriceRow(
            symbol_key=m.symbol_key,
            display_name=m.display_name,
            category=m.category,
            alis=alis,
            satis=satis,
            raw_bid=raw_bid,
            raw_ask=raw_ask,
            trend=trend,
            pct_change=pct,
            using_volatility=using_volatility,
            is_readonly=m.is_readonly,
            sort_order=m.sort_order,
        ))
    return out


def extract_pariteler(
    fiyatlar: dict, baseline: dict[str, float] | None = None
) -> list[dict]:
    parite = fiyatlar.get("PARITE", {})
    if not isinstance(parite, dict):
        return []
    baseline = baseline or {}
    out = []
    for sym, raw in parite.items():
        if isinstance(raw, dict) and raw.get("bid") is not None and raw.get("ask") is not None:
            bid = float(raw["bid"])
            ask = float(raw["ask"])
            bl = baseline.get(sym)
            if bl is not None and bl != 0:
                pct = (bid - bl) / bl * 100.0
                trend = "up" if bid > bl else "down" if bid < bl else "flat"
            else:
                pct = 0.0
                trend = "flat"
            out.append({
                "symbol": sym,
                "bid": bid,
                "ask": ask,
                "trend": trend,
                "pct_change": pct,
            })
    out.sort(key=lambda x: x["symbol"])
    return out
