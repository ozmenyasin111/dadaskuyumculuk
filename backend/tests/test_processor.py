from decimal import Decimal

from app.services.processor import (
    MarginRow,
    VolatilityRule,
    compute_prices,
    extract_pariteler,
)


def _margin(
    symbol_key: str,
    display_name: str,
    category: str,
    alis: float,
    satis: float,
    readonly: bool = False,
    multiplier: bool = False,
    classic_alis: float = 0,
    classic_satis: float = 0,
) -> MarginRow:
    return MarginRow(
        symbol_key=symbol_key,
        display_name=display_name,
        category=category,
        alis_offset=Decimal(str(alis)),
        satis_offset=Decimal(str(satis)),
        sort_order=0,
        is_readonly=readonly,
        is_multiplier=multiplier,
        classic_alis_offset=Decimal(str(classic_alis)),
        classic_satis_offset=Decimal(str(classic_satis)),
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
    margins = [_margin("SARRAFIYE.KULCEALTIN", "Gram Altın", "ALTIN", -20, 20)]
    volatility = {"ALTIN": _vol("ALTIN", 500, -200, 300)}
    rows = compute_prices(sample_fiyatlar, margins, volatility)
    assert len(rows) == 1
    row = rows[0]
    assert row.using_volatility is False
    assert row.alis == 6800.00 - 20
    assert row.satis == 6828.94 + 20


def test_volatility_override_applied_when_fark_exceeds_threshold(volatile_fiyatlar):
    margins = [_margin("SARRAFIYE.KULCEALTIN", "Gram Altın", "ALTIN", -20, 20)]
    volatility = {"ALTIN": _vol("ALTIN", 500, -200, 300)}
    rows = compute_prices(volatile_fiyatlar, margins, volatility)
    row = rows[0]
    assert row.using_volatility is True
    assert row.alis == 6800.00 - 200
    assert row.satis == 7400.00 + 300


def test_volatility_disabled_falls_back_to_admin_offset(volatile_fiyatlar):
    margins = [_margin("SARRAFIYE.KULCEALTIN", "Gram Altın", "ALTIN", -20, 20)]
    volatility = {"ALTIN": _vol("ALTIN", 500, -200, 300, enabled=False)}
    rows = compute_prices(volatile_fiyatlar, margins, volatility)
    assert rows[0].using_volatility is False
    assert rows[0].alis == 6800.00 - 20


def test_readonly_row_returns_raw(sample_fiyatlar):
    margins = [_margin("MADEN.ALTIN_RO", "Has Altın (Ham)", "READONLY", 0, 0, readonly=True)]
    rows = compute_prices(sample_fiyatlar, margins, {})
    assert rows[0].alis == 6800.00
    assert rows[0].satis == 6828.94
    assert rows[0].is_readonly is True


def test_computed_kg_ons_altin(sample_fiyatlar):
    margins = [_margin("COMPUTED.KG_ONS_ALTIN_RO", "Kg Ons Altın", "READONLY", 0, 0, readonly=True)]
    rows = compute_prices(sample_fiyatlar, margins, {})
    assert abs(rows[0].alis - 4687.91 * 32.1507) < 0.01


def test_missing_symbol_skipped(sample_fiyatlar):
    margins = [
        _margin("SARRAFIYE.KULCEALTIN", "Gram Altın", "ALTIN", 0, 0),
        _margin("DOVIZ.NONEXISTENT", "Yok", "DOVIZ", 0, 0),
    ]
    rows = compute_prices(sample_fiyatlar, margins, {})
    assert len(rows) == 1


def test_volatility_only_applies_to_eligible_symbols(sample_fiyatlar):
    fake = dict(sample_fiyatlar)
    fake["SARRAFIYE"] = {"AYAR14": {"bid": 3500.00, "ask": 5000.00}}
    margins = [_margin("SARRAFIYE.AYAR14", "14 Ayar", "ALTIN", 0, 700)]
    volatility = {"ALTIN": _vol("ALTIN", 500, -200, 300)}
    rows = compute_prices(fake, margins, volatility)
    assert rows[0].using_volatility is False
    assert rows[0].alis == 3500.00


def test_multiplier_row_uses_gram_altin_display(sample_fiyatlar):
    """Multiplier satır: Gram Altın display × milyem ile hesaplanır."""
    margins = [
        _margin("SARRAFIYE.KULCEALTIN", "Gram Altın", "ALTIN", -10, 40),
        _margin("SARRAFIYE.CEYREK_YENI", "Yeni Çeyrek", "ALTIN", 1.62, 1.654, multiplier=True),
    ]
    rows = compute_prices(sample_fiyatlar, margins, {})
    gram = next(r for r in rows if r.symbol_key == "SARRAFIYE.KULCEALTIN")
    ceyrek = next(r for r in rows if r.symbol_key == "SARRAFIYE.CEYREK_YENI")
    assert gram.alis == 6800.00 - 10
    assert gram.satis == 6828.94 + 40
    assert abs(ceyrek.alis - 6790 * 1.62) < 0.01
    assert abs(ceyrek.satis - 6868.94 * 1.654) < 0.01


def test_multiplier_inherits_gram_altin_volatility(volatile_fiyatlar):
    """Gram Altın volatility aktifse multiplier satırlar da volatility göstergesi taşır."""
    margins = [
        _margin("SARRAFIYE.KULCEALTIN", "Gram Altın", "ALTIN", -10, 40),
        _margin("SARRAFIYE.CEYREK_YENI", "Yeni Çeyrek", "ALTIN", 1.62, 1.654, multiplier=True),
    ]
    volatility = {"ALTIN": _vol("ALTIN", 500, -200, 300)}
    rows = compute_prices(volatile_fiyatlar, margins, volatility)
    gram = next(r for r in rows if r.symbol_key == "SARRAFIYE.KULCEALTIN")
    ceyrek = next(r for r in rows if r.symbol_key == "SARRAFIYE.CEYREK_YENI")
    assert gram.using_volatility is True
    assert ceyrek.using_volatility is True
    # Gram Altın volatility değerleri: 6800-200=6600, 7400+300=7700
    assert abs(ceyrek.alis - 6600 * 1.62) < 0.01
    assert abs(ceyrek.satis - 7700 * 1.654) < 0.01


def test_kulcealtin_falls_back_to_maden_altin_when_zero():
    """API SARRAFIYE beslemesini durdurduğunda (bid/ask=0) MADEN.ALTIN'a düşmeli.
    Gram Altın satırı kaybolmamalı, multiplier zinciri ayakta kalmalı."""
    fiyatlar = {
        "MADEN": {"ALTIN": {"bid": 6637.18, "ask": 6690.98}},
        "SARRAFIYE": {"KULCEALTIN": {"bid": 0, "ask": 0}},
    }
    margins = [
        _margin("SARRAFIYE.KULCEALTIN", "Gram Altın", "ALTIN", -15, 40),
        _margin("SARRAFIYE.CEYREK_YENI", "Yeni Çeyrek", "ALTIN", 1.62, 1.654, multiplier=True),
    ]
    rows = compute_prices(fiyatlar, margins, {})
    by_key = {r.symbol_key: r for r in rows}
    assert "SARRAFIYE.KULCEALTIN" in by_key, "Gram Altın satırı fallback ile görünmeli"
    gram = by_key["SARRAFIYE.KULCEALTIN"]
    assert abs(gram.alis - (6637.18 - 15)) < 0.01
    assert abs(gram.satis - (6690.98 + 40)) < 0.01
    ceyrek = by_key["SARRAFIYE.CEYREK_YENI"]
    assert abs(ceyrek.alis - (6637.18 - 15) * 1.62) < 0.01


def test_classic_mode_uses_own_raw_and_tl_offset(sample_fiyatlar):
    """Classic mod: multiplier satır kendi raw'ına bakıp TL offset ekler."""
    margins = [
        _margin("SARRAFIYE.KULCEALTIN", "Gram Altın", "ALTIN", -10, 40),
        _margin(
            "SARRAFIYE.AYAR22",
            "Bilezik (22 Ayar)",
            "ALTIN",
            0.91,  # milyem (kullanılmaz classic mode'da)
            0.955,
            multiplier=True,
            classic_alis=-15,
            classic_satis=100,
        ),
    ]
    rows = compute_prices(sample_fiyatlar, margins, {}, pricing_mode="classic")
    bilezik = next(r for r in rows if r.symbol_key == "SARRAFIYE.AYAR22")
    # sample_fiyatlar SARRAFIYE.AYAR22 → bid=6184.27, ask=6486.01
    assert abs(bilezik.alis - (6184.27 - 15)) < 0.01
    assert abs(bilezik.satis - (6486.01 + 100)) < 0.01


def test_milyem_mode_still_uses_has_altin(sample_fiyatlar):
    """Milyem mod default davranışı korunmalı — multiplier × has_altin display."""
    margins = [
        _margin("SARRAFIYE.KULCEALTIN", "Gram Altın", "ALTIN", -10, 40),
        _margin(
            "SARRAFIYE.AYAR22",
            "Bilezik",
            "ALTIN",
            0.91,
            0.955,
            multiplier=True,
            classic_alis=-15,
            classic_satis=100,
        ),
    ]
    rows = compute_prices(sample_fiyatlar, margins, {}, pricing_mode="milyem")
    bilezik = next(r for r in rows if r.symbol_key == "SARRAFIYE.AYAR22")
    # has_altin alis = 6800 - 10 = 6790; satis = 6828.94 + 40 = 6868.94
    assert abs(bilezik.alis - 6790 * 0.91) < 0.01
    assert abs(bilezik.satis - 6868.94 * 0.955) < 0.01


def test_extract_pariteler(sample_fiyatlar):
    pariteler = extract_pariteler(sample_fiyatlar)
    assert len(pariteler) == 1
    assert pariteler[0]["symbol"] == "EURUSD"
