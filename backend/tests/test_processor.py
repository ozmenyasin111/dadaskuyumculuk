from decimal import Decimal

from app.services.processor import (
    MarginRow,
    VolatilityRule,
    compute_prices,
    extract_pariteler,
)


def _margin(symbol_key: str, display_name: str, category: str, alis: float, satis: float, readonly: bool = False) -> MarginRow:
    return MarginRow(
        symbol_key=symbol_key,
        display_name=display_name,
        category=category,
        alis_offset=Decimal(str(alis)),
        satis_offset=Decimal(str(satis)),
        sort_order=0,
        is_readonly=readonly,
    )


def _vol(category: str, threshold: float, alis: float, satis: float, enabled: bool = True) -> VolatilityRule:
    return VolatilityRule(
        category=category,
        threshold=Decimal(str(threshold)),
        alis_override=Decimal(str(alis)),
        satis_override=Decimal(str(satis)),
        enabled=enabled,
    )


def test_normal_offset_applied(sample_fiyatlar):
    margins = [_margin("MADEN.ALTIN", "Has Altın", "ALTIN", -20, 20)]
    volatility = {"ALTIN": _vol("ALTIN", 500, -200, 300)}

    rows = compute_prices(sample_fiyatlar, margins, volatility)
    assert len(rows) == 1
    row = rows[0]
    assert row.using_volatility is False
    assert row.alis == 6800.00 - 20
    assert row.satis == 6828.94 + 20


def test_volatility_override_applied_when_fark_exceeds_threshold(volatile_fiyatlar):
    margins = [_margin("MADEN.ALTIN", "Has Altın", "ALTIN", -20, 20)]
    volatility = {"ALTIN": _vol("ALTIN", 500, -200, 300)}

    rows = compute_prices(volatile_fiyatlar, margins, volatility)
    row = rows[0]
    assert row.using_volatility is True
    assert row.alis == 6800.00 - 200
    assert row.satis == 7400.00 + 300


def test_volatility_disabled_falls_back_to_admin_offset(volatile_fiyatlar):
    margins = [_margin("MADEN.ALTIN", "Has Altın", "ALTIN", -20, 20)]
    volatility = {"ALTIN": _vol("ALTIN", 500, -200, 300, enabled=False)}

    rows = compute_prices(volatile_fiyatlar, margins, volatility)
    row = rows[0]
    assert row.using_volatility is False
    assert row.alis == 6800.00 - 20


def test_volatility_only_applies_to_eligible_symbols(sample_fiyatlar):
    """Doğal spread'i geniş ürünler (14 Ayar, ATA 5'li vb.) volatility'den etkilenmemeli."""
    # API'de fark > 500 olan bir sembol, ama eligible listesinde yok
    fake = dict(sample_fiyatlar)
    fake["SARRAFIYE"] = {"AYAR14": {"bid": 3500.00, "ask": 5000.00}}  # fark = 1500
    margins = [_margin("SARRAFIYE.AYAR14", "14 Ayar", "ALTIN", 0, 700)]
    volatility = {"ALTIN": _vol("ALTIN", 500, -200, 300)}

    rows = compute_prices(fake, margins, volatility)
    row = rows[0]
    # 14 Ayar eligible değil → admin offset uygulanır, override değil
    assert row.using_volatility is False
    assert row.alis == 3500.00
    assert row.satis == 5000.00 + 700


def test_readonly_row_returns_raw(sample_fiyatlar):
    margins = [_margin("MADEN.ALTIN_RO", "Has Altın", "READONLY", 0, 0, readonly=True)]
    rows = compute_prices(sample_fiyatlar, margins, {})
    row = rows[0]
    assert row.alis == 6800.00
    assert row.satis == 6828.94
    assert row.is_readonly is True


def test_computed_kg_ons_altin(sample_fiyatlar):
    margins = [_margin("COMPUTED.KG_ONS_ALTIN_RO", "Kg Ons Altın", "READONLY", 0, 0, readonly=True)]
    rows = compute_prices(sample_fiyatlar, margins, {})
    row = rows[0]
    assert abs(row.alis - 4687.91 * 32.1507) < 0.01
    assert abs(row.satis - 4688.54 * 32.1507) < 0.01


def test_missing_symbol_skipped(sample_fiyatlar):
    margins = [
        _margin("MADEN.ALTIN", "Has Altın", "ALTIN", 0, 0),
        _margin("DOVIZ.NONEXISTENT", "Yok", "DOVIZ", 0, 0),
    ]
    rows = compute_prices(sample_fiyatlar, margins, {})
    assert len(rows) == 1
    assert rows[0].symbol_key == "MADEN.ALTIN"


def test_pct_change_from_baseline(sample_fiyatlar):
    """Baseline'a göre pct ve trend hesaplanır."""
    margins = [_margin("MADEN.ALTIN", "Has Altın", "ALTIN", 0, 0)]
    # Baseline'da fiyat 6700.0 olsa, şu anda alis = 6800 → +1.49%
    baseline = {"MADEN.ALTIN": 6700.0}
    rows = compute_prices(sample_fiyatlar, margins, {}, baseline=baseline)
    row = rows[0]
    assert row.trend == "up"
    assert abs(row.pct_change - 1.4925) < 0.01


def test_pct_zero_when_no_baseline(sample_fiyatlar):
    """Baseline yoksa pct=0, trend=flat."""
    margins = [_margin("MADEN.ALTIN", "Has Altın", "ALTIN", 0, 0)]
    rows = compute_prices(sample_fiyatlar, margins, {})
    assert rows[0].pct_change == 0.0
    assert rows[0].trend == "flat"


def test_extract_pariteler(sample_fiyatlar):
    pariteler = extract_pariteler(sample_fiyatlar)
    assert len(pariteler) == 1
    assert pariteler[0]["symbol"] == "EURUSD"
    assert pariteler[0]["bid"] == 1.1679
