"""Bayatlık (staleness) bazlı failover testleri."""

from datetime import datetime, timedelta, timezone

import pytest

from app.services import failover
from app.services.failover import apply_failover, check_total_freeze


def _iso(now: datetime, age_sec: float) -> str:
    return (now - timedelta(seconds=age_sec)).isoformat().replace("+00:00", "Z")


@pytest.fixture(autouse=True)
def _reset():
    failover.reset_state()
    yield
    failover.reset_state()


def _payload(now, kulce_age, ds_kulce_age, kulce_bid=6000.0, ds_bid=6001.0):
    return {
        "SARRAFIYE": {
            "KULCEALTIN": {"bid": kulce_bid, "ask": kulce_bid + 90, "timestamp": _iso(now, kulce_age)},
        },
        "DOVIZ": {
            "DS_KULCEALTIN": {"bid": ds_bid, "ask": ds_bid + 90, "timestamp": _iso(now, ds_kulce_age)},
        },
    }


def test_fresh_primary_no_switch():
    now = datetime.now(timezone.utc)
    f = _payload(now, kulce_age=5, ds_kulce_age=5)
    events = apply_failover(f, now)
    assert events == []
    # ana kaynak değeri dokunulmadan kalır
    assert f["SARRAFIYE"]["KULCEALTIN"]["bid"] == 6000.0


def test_stale_primary_switches_to_alternative():
    now = datetime.now(timezone.utc)
    # KULCEALTIN 4 dk donuk (eşik 180sn), alternatif taze
    f = _payload(now, kulce_age=240, ds_kulce_age=5, kulce_bid=6000.0, ds_bid=6001.0)
    events = apply_failover(f, now)
    switch = [e for e in events if e["primary"] == "SARRAFIYE.KULCEALTIN"]
    assert len(switch) == 1
    assert switch[0]["type"] == "switch"
    assert switch[0]["alt"] == "DOVIZ.DS_KULCEALTIN"
    assert switch[0]["old_bid"] == 6000.0
    assert switch[0]["new_bid"] == 6001.0
    # fiyatlar ana kaynağı artık alternatif değerini gösterir
    assert f["SARRAFIYE"]["KULCEALTIN"]["bid"] == 6001.0


def test_no_duplicate_switch_event_on_consecutive_ticks():
    now = datetime.now(timezone.utc)
    f1 = _payload(now, kulce_age=240, ds_kulce_age=5)
    ev1 = apply_failover(f1, now)
    assert any(e["type"] == "switch" for e in ev1)
    # ikinci tick: hâlâ donuk → tekrar bildirim ATMAMALI
    f2 = _payload(now, kulce_age=300, ds_kulce_age=5)
    ev2 = apply_failover(f2, now)
    assert ev2 == []
    # ama değer yine alternatifle değiştirilmiş olmalı
    assert f2["SARRAFIYE"]["KULCEALTIN"]["bid"] == 6001.0


def test_recover_event_when_primary_fresh_again():
    now = datetime.now(timezone.utc)
    apply_failover(_payload(now, kulce_age=240, ds_kulce_age=5), now)
    # ana kaynak tazelendi
    f = _payload(now, kulce_age=2, ds_kulce_age=5)
    events = apply_failover(f, now)
    rec = [e for e in events if e["primary"] == "SARRAFIYE.KULCEALTIN"]
    assert len(rec) == 1
    assert rec[0]["type"] == "recover"


def test_no_switch_when_alternative_also_stale():
    now = datetime.now(timezone.utc)
    # her ikisi de donuk → değişiklik yok, değer korunur
    f = _payload(now, kulce_age=240, ds_kulce_age=400)
    events = apply_failover(f, now)
    assert [e for e in events if e["primary"] == "SARRAFIYE.KULCEALTIN"] == []
    assert f["SARRAFIYE"]["KULCEALTIN"]["bid"] == 6000.0


def test_scaled_alternative_divided_by_1000():
    now = datetime.now(timezone.utc)
    f = {
        "MADEN": {"PARUSD": {"bid": 129.5, "ask": 130.0, "timestamp": _iso(now, 240)}},
        "DOVIZ": {"DS_PARUSD": {"bid": 129500.0, "ask": 130000.0, "timestamp": _iso(now, 5)}},
    }
    apply_failover(f, now)
    # 129500 / 1000 = 129.5
    assert abs(f["MADEN"]["PARUSD"]["bid"] - 129.5) < 1e-6


def test_doviz_uses_5min_threshold():
    now = datetime.now(timezone.utc)
    # USDTRY 4 dk donuk: döviz eşiği 5 dk olduğu için HENÜZ donuk sayılmamalı
    f = {
        "DOVIZ": {
            "USDTRY": {"bid": 46.4, "ask": 46.6, "timestamp": _iso(now, 240)},
            "DS_USDTRY": {"bid": 46.41, "ask": 46.61, "timestamp": _iso(now, 5)},
        },
    }
    events = apply_failover(f, now)
    assert [e for e in events if e["primary"] == "DOVIZ.USDTRY"] == []
    assert f["DOVIZ"]["USDTRY"]["bid"] == 46.4  # dokunulmadı


def test_usd_sar_use_20min_threshold():
    now = datetime.now(timezone.utc)
    # USDTRY 10 dk donuk: özel eşik 20 dk olduğu için HENÜZ geçiş YAPILMAMALI
    f = {
        "DOVIZ": {
            "USDTRY": {"bid": 46.4, "ask": 46.6, "timestamp": _iso(now, 600)},
            "DS_USDTRY": {"bid": 46.41, "ask": 46.61, "timestamp": _iso(now, 5)},
            "SARTRY": {"bid": 12.2, "ask": 12.5, "timestamp": _iso(now, 600)},
            "DS_SARTRY": {"bid": 12.21, "ask": 12.53, "timestamp": _iso(now, 5)},
        },
    }
    events = apply_failover(f, now)
    assert [e for e in events if e["primary"] in ("DOVIZ.USDTRY", "DOVIZ.SARTRY")] == []
    assert f["DOVIZ"]["USDTRY"]["bid"] == 46.4  # dokunulmadı
    # 21 dk olunca (20 dk eşiği aşınca) geçmeli
    f["DOVIZ"]["USDTRY"]["timestamp"] = _iso(now, 1260)
    events2 = apply_failover(f, now)
    assert any(e["primary"] == "DOVIZ.USDTRY" and e["type"] == "switch" for e in events2)


def test_total_freeze_alarm_when_everything_stale():
    now = datetime.now(timezone.utc)
    # Hem ana hem alternatif 11 dk donuk (eşik 10 dk) → toptan donma
    f = _payload(now, kulce_age=660, ds_kulce_age=660)
    ev = check_total_freeze(f, now)
    assert ev is not None and ev["type"] == "total_freeze_start"


def test_no_total_freeze_when_one_source_fresh():
    now = datetime.now(timezone.utc)
    # Ana donuk ama alternatif taze → toptan donma DEĞİL (failover kurtarır)
    f = _payload(now, kulce_age=660, ds_kulce_age=5)
    assert check_total_freeze(f, now) is None


def test_total_freeze_recover_event():
    now = datetime.now(timezone.utc)
    check_total_freeze(_payload(now, kulce_age=660, ds_kulce_age=660), now)
    # her şey tazelendi
    ev = check_total_freeze(_payload(now, kulce_age=5, ds_kulce_age=5), now)
    assert ev is not None and ev["type"] == "total_freeze_recover"


def test_total_freeze_no_duplicate_alarm():
    now = datetime.now(timezone.utc)
    e1 = check_total_freeze(_payload(now, kulce_age=660, ds_kulce_age=660), now)
    assert e1 is not None and e1["type"] == "total_freeze_start"
    # hâlâ donuk → tekrar alarm ATMAMALI
    e2 = check_total_freeze(_payload(now, kulce_age=700, ds_kulce_age=700), now)
    assert e2 is None
