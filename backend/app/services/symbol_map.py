"""API yanıt yapısı ile display sembol arasındaki köprüleme.

API yanıtı: `fiyatlar[CATEGORY][SYMBOL] = {bid, ask, timestamp}`. Bir display satırının
`symbol_key`'i (ör. `MADEN.ALTIN`) bu yola eşlenir. Salt-okunur sembollerde key sonuna
`_RO` eklenir, böylece aynı API path'i hem editable hem readonly olarak gözükebilir
(ör. `MADEN.ALTIN` admin offset'leriyle, `MADEN.ALTIN_RO` ham veriyle).

`COMPUTED.*` özel anahtarlar API yanıtından hesaplanır.
"""

# 1 kg = 32.1507 troy ons
TROY_OUNCES_PER_KG = 32.1507

COMPUTED_KEY_KG_ONS_ALTIN = "COMPUTED.KG_ONS_ALTIN"


def parse_symbol_key(symbol_key: str) -> tuple[str, str, bool]:
    """`MADEN.ALTIN_RO` → (`MADEN`, `ALTIN`, True). Salt-okunur olup olmadığını ve
    asıl API path'ini döner."""
    key = symbol_key
    is_readonly_suffix = key.endswith("_RO")
    if is_readonly_suffix:
        key = key[:-3]
    if "." not in key:
        return "", key, is_readonly_suffix
    category, symbol = key.split(".", 1)
    return category, symbol, is_readonly_suffix


def lookup_raw(fiyatlar: dict, symbol_key: str) -> dict | None:
    """API yanıtından (`fiyatlar` üst nesnesi) verilen `symbol_key` için `{bid, ask}`
    paketini döner. Bulunamazsa `None`."""
    category, symbol, _ = parse_symbol_key(symbol_key)
    if category == "COMPUTED":
        return _compute(fiyatlar, symbol)
    if not category or not symbol:
        return None
    cat_node = fiyatlar.get(category)
    if not isinstance(cat_node, dict):
        return None
    raw = cat_node.get(symbol)
    if not isinstance(raw, dict):
        return None
    bid = raw.get("bid")
    ask = raw.get("ask")
    if bid is None or ask is None:
        return None
    bid_f = float(bid)
    ask_f = float(ask)
    # API bir kategoriyi durdurduğunda 0 dönüyor (stale veri). 0'ı geçersiz say,
    # böylece processor fallback'i devreye girer ve canlı altın 0 TL gösterilmez.
    if bid_f <= 0 or ask_f <= 0:
        return None
    return {"bid": bid_f, "ask": ask_f}


def _compute(fiyatlar: dict, name: str) -> dict | None:
    if name == "KG_ONS_ALTIN":
        xauusd = lookup_raw(fiyatlar, "MADEN.XAUUSD")
        if not xauusd:
            return None
        return {
            "bid": xauusd["bid"] * TROY_OUNCES_PER_KG,
            "ask": xauusd["ask"] * TROY_OUNCES_PER_KG,
        }
    if name == "KG_GUMUS_TL":
        # MADEN.GUMTRY canlı, SARRAFIYE.GUMUSTRY günler eskiye düşebiliyor
        gram = lookup_raw(fiyatlar, "MADEN.GUMTRY")
        if not gram:
            return None
        return {"bid": gram["bid"] * 1000, "ask": gram["ask"] * 1000}
    return None
