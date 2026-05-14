from pydantic import BaseModel


class PriceRowOut(BaseModel):
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


class PariteOut(BaseModel):
    symbol: str
    bid: float
    ask: float
    trend: str = "flat"
    pct_change: float = 0.0


class PriceSnapshotOut(BaseModel):
    fiyatlar: list[PriceRowOut]
    pariteler: list[PariteOut]
    guncellendi: int
    healthy: bool
