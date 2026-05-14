import pytest


@pytest.fixture
def sample_fiyatlar() -> dict:
    """Has Altın + Bilezik + USD/TRY içeren minimal API yanıtı.

    Has Altın: fark = 28.94 (<500 → admin offset).
    """
    return {
        "MADEN": {
            "ALTIN": {"bid": 6800.00, "ask": 6828.94, "timestamp": "2026-05-14T00:00:00Z"},
            "XAUUSD": {"bid": 4687.91, "ask": 4688.54, "timestamp": "2026-05-14T00:00:00Z"},
            "XAGUSD": {"bid": 87.462, "ask": 87.524, "timestamp": "2026-05-14T00:00:00Z"},
            "XAUXAG": {"bid": 51.89, "ask": 55.85, "timestamp": "2026-05-14T00:00:00Z"},
            "GUMUSD": {"bid": 2.68, "ask": 2.87, "timestamp": "2026-05-14T00:00:00Z"},
        },
        "SARRAFIYE": {
            "AYAR22": {"bid": 6184.27, "ask": 6486.01, "timestamp": "2026-05-14T00:00:00Z"},
        },
        "DOVIZ": {
            "USDTRY": {"bid": 45.27, "ask": 45.46, "timestamp": "2026-05-14T00:00:00Z"},
        },
        "PARITE": {
            "EURUSD": {"bid": 1.1679, "ask": 1.1711, "timestamp": "2026-05-14T00:00:00Z"},
        },
    }


@pytest.fixture
def volatile_fiyatlar() -> dict:
    """Has Altın'da fark = 600 (≥500 → volatility override aktif)."""
    return {
        "MADEN": {
            "ALTIN": {"bid": 6800.00, "ask": 7400.00, "timestamp": "2026-05-14T00:00:00Z"},
            "XAUUSD": {"bid": 4687.91, "ask": 4688.54, "timestamp": "2026-05-14T00:00:00Z"},
        },
        "DOVIZ": {
            "USDTRY": {"bid": 45.27, "ask": 545.46, "timestamp": "2026-05-14T00:00:00Z"},  # fark>500
        },
    }
