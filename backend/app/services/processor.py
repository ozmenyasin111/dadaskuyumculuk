"""Margin + volatility kuralı uygulayıp display fiyatları hesaplar.

  fark = ask - bid
  kategori volatility kuralı varsa ve fark >= eşik ve enabled:
      display_alis  = bid + volatility.alis_override   (admin offset ezilir)
      display_satis = ask + volatility.satis_override
  değilse:
      display_alis  = bid + margin.alis_offset
      display_satis = ask + margin.satis_offset

`baseline` (oturum başı her sembolün ilk gözlemlenen `alis` değeri) ile karşılaştırarak
`pct_change` ve `trend` hesaplanır.
"""

from dataclasses import dataclass
from decimal import Decimal

from app.services.symbol_map import lookup_raw


@dataclass(frozen=True)
class MarginRow:
    symbol_key: str
    display_name: str
    category: str
    alis_offset: Decimal
    satis_offset: Decimal
    sort_order: int
    is_readonly: bool


@dataclass(frozen=True)
class VolatilityRule:
    category: str
    threshold: Decimal
    alis_override: Decimal
    satis_override: Decimal
    enabled: bool


# Volatility override (fark ≥ eşik → admin offset ezilir) sadece bu sembollere
# uygulanır. ATA 5'li, GREMSE, 14 AYAR gibi doğal bid-ask spread'i geniş ürünler
# bu kuraldan etkilenmez. Döviz tarafında threshold çok büyük tutulduğu için pratikte
# tetiklenmez ama mantık çalışıyor.
VOLATILITY_ELIGIBLE_SYMBOLS = {
    "MADEN.ALTIN",
    "DOVIZ.USDTRY",
    "DOVIZ.EURTRY",
    "DOVIZ.GBPTRY",
    "DOVIZ.CHFTRY",
    "DOVIZ.AUDTRY",
    "DOVIZ.CADTRY",
    "DOVIZ.SARTRY",
    "DOVIZ.EURUSDS",
}


@dataclass
class PriceRow:
    symbol_key: str
    display_name: str
    category: str
    alis: float
    satis: float
    raw_bid: float
    raw_ask: float
    trend: str  # "up" | "down" | "flat"
    pct_change: float
    using_volatility: bool
    is_readonly: bool
    sort_order: int


def compute_prices(
    fiyatlar: dict,
    margins: list[MarginRow],
    volatility: dict[str, VolatilityRule],
    baseline: dict[str, float] | None = None,
) -> list[PriceRow]:
    baseline = baseline or {}
    out: list[PriceRow] = []
    for m in margins:
        raw = lookup_raw(fiyatlar, m.symbol_key)
        if raw is None:
            continue
        bid = raw["bid"]
        ask = raw["ask"]
        fark = ask - bid

        using_volatility = False
        if m.is_readonly:
            alis = bid
            satis = ask
        else:
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
            raw_bid=bid,
            raw_ask=ask,
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
    """PARITE kategorisindeki sembolleri pct/trend ile zenginleştirir.
    `baseline` parite sembolleri için `dict[symbol, bid_baseline]`."""
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
