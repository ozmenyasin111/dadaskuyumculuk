"""altinapi düz dizi → finansveri iç içe format dönüşümü testleri."""

from app.services.altinapi import _to_ms, _transform


def test_transform_flat_array_to_nested():
    payload = {
        "data": [
            {"symbol": "KULCEALTIN", "category": "SARRAFIYE", "bid": 6003.7, "ask": 6086.8,
             "timestamp": "2026-06-30T16:13:14+03:00"},
            {"symbol": "USDTRY", "category": "DOVIZ", "bid": 46.4, "ask": 46.55,
             "timestamp": "2026-06-30T16:13:14+03:00"},
        ],
        "updatedAt": "2026-06-30T13:13:16.639Z",
        "stale": False,
    }
    out = _transform(payload)
    assert out["fiyatlar"]["SARRAFIYE"]["KULCEALTIN"]["bid"] == 6003.7
    assert out["fiyatlar"]["DOVIZ"]["USDTRY"]["ask"] == 46.55
    # +03:00 offset'li güvenilir timestamp korunmalı (timestamp_utc DEĞİL)
    assert out["fiyatlar"]["SARRAFIYE"]["KULCEALTIN"]["timestamp"] == "2026-06-30T16:13:14+03:00"
    assert out["guncellendi"] > 0


def test_transform_skips_incomplete_records():
    payload = {"data": [
        {"symbol": "X", "category": "DOVIZ", "bid": None, "ask": 1.0},  # bid yok → atla
        {"symbol": "Y", "bid": 1.0, "ask": 2.0},                        # category yok → atla
        {"category": "DOVIZ", "bid": 1.0, "ask": 2.0},                  # symbol yok → atla
        {"symbol": "USDTRY", "category": "DOVIZ", "bid": 46.4, "ask": 46.55},  # geçerli
    ], "updatedAt": "2026-06-30T13:13:16.639Z"}
    out = _transform(payload)
    assert "USDTRY" in out["fiyatlar"]["DOVIZ"]
    assert "X" not in out["fiyatlar"].get("DOVIZ", {})
    assert len(out["fiyatlar"]["DOVIZ"]) == 1


def test_to_ms_parses_iso():
    assert _to_ms("2026-06-30T13:13:16.639Z") == 1782825196639
    assert _to_ms(None) == 0
    assert _to_ms("garbage") == 0
