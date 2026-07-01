"""Bayatlık (staleness) bazlı failover testleri."""

from datetime import datetime, timedelta, timezone

import pytest

from app.services import failover
from app.services.failover import (
    apply_failover,
    check_total_freeze,
    freshest_mapped_age,
    patch_from_secondary,
    resolve_fresh,
    unfilled_primaries,
)


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
    # KULCEALTIN 12 dk donuk (eşik 600sn), alternatif taze
    f = _payload(now, kulce_age=720, ds_kulce_age=5, kulce_bid=6000.0, ds_bid=6001.0)
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
    f1 = _payload(now, kulce_age=720, ds_kulce_age=5)
    ev1 = apply_failover(f1, now)
    assert any(e["type"] == "switch" for e in ev1)
    # ikinci tick: hâlâ donuk → tekrar bildirim ATMAMALI
    f2 = _payload(now, kulce_age=780, ds_kulce_age=5)
    ev2 = apply_failover(f2, now)
    assert ev2 == []
    # ama değer yine alternatifle değiştirilmiş olmalı
    assert f2["SARRAFIYE"]["KULCEALTIN"]["bid"] == 6001.0


def test_recover_event_when_primary_fresh_again():
    now = datetime.now(timezone.utc)
    apply_failover(_payload(now, kulce_age=720, ds_kulce_age=5), now)
    # ana kaynak tazelendi
    f = _payload(now, kulce_age=2, ds_kulce_age=5)
    events = apply_failover(f, now)
    rec = [e for e in events if e["primary"] == "SARRAFIYE.KULCEALTIN"]
    assert len(rec) == 1
    assert rec[0]["type"] == "recover"


def test_no_switch_when_alternative_also_stale():
    now = datetime.now(timezone.utc)
    # her ikisi de donuk → değişiklik yok, değer korunur
    f = _payload(now, kulce_age=720, ds_kulce_age=900)
    events = apply_failover(f, now)
    assert [e for e in events if e["primary"] == "SARRAFIYE.KULCEALTIN"] == []
    assert f["SARRAFIYE"]["KULCEALTIN"]["bid"] == 6000.0


def test_scaled_alternative_divided_by_1000():
    now = datetime.now(timezone.utc)
    f = {
        "MADEN": {"PARUSD": {"bid": 129.5, "ask": 130.0, "timestamp": _iso(now, 720)}},
        "DOVIZ": {"DS_PARUSD": {"bid": 129500.0, "ask": 130000.0, "timestamp": _iso(now, 5)}},
    }
    apply_failover(f, now)
    # 129500 / 1000 = 129.5
    assert abs(f["MADEN"]["PARUSD"]["bid"] - 129.5) < 1e-6


def test_doviz_uses_10min_threshold():
    now = datetime.now(timezone.utc)
    # EURTRY 8 dk donuk: genel döviz eşiği 10 dk olduğu için HENÜZ donuk sayılmamalı
    # (USDTRY/SARTRY özel 20 dk eşikte; genel eşiği doğru ölçmek için EURTRY kullanılır).
    f = {
        "DOVIZ": {
            "EURTRY": {"bid": 48.4, "ask": 48.6, "timestamp": _iso(now, 480)},
            "DS_EURTRY": {"bid": 48.41, "ask": 48.61, "timestamp": _iso(now, 5)},
        },
    }
    events = apply_failover(f, now)
    assert [e for e in events if e["primary"] == "DOVIZ.EURTRY"] == []
    assert f["DOVIZ"]["EURTRY"]["bid"] == 48.4  # dokunulmadı
    # 11 dk olunca (10 dk eşiği aşınca) ikize geçmeli
    f["DOVIZ"]["EURTRY"]["timestamp"] = _iso(now, 660)
    events2 = apply_failover(f, now)
    assert any(e["primary"] == "DOVIZ.EURTRY" and e["type"] == "switch" for e in events2)
    assert f["DOVIZ"]["EURTRY"]["bid"] == 48.41


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


def test_unfilled_when_primary_and_alt_both_stale():
    now = datetime.now(timezone.utc)
    # KULCEALTIN ve ikizi ikisi de donuk → unfilled listesinde olmalı
    f = _payload(now, kulce_age=720, ds_kulce_age=720)
    uf = unfilled_primaries(f, now)
    assert ("Gram Altın", "SARRAFIYE.KULCEALTIN") in uf


def test_not_unfilled_when_alt_fresh():
    now = datetime.now(timezone.utc)
    # primary donuk ama ikiz taze → finansveri içinde çözülür, unfilled DEĞİL
    f = _payload(now, kulce_age=720, ds_kulce_age=5)
    uf = unfilled_primaries(f, now)
    assert ("Gram Altın", "SARRAFIYE.KULCEALTIN") not in uf


def test_patch_from_secondary_fills_only_unfilled():
    now = datetime.now(timezone.utc)
    # finansveri: KULCEALTIN + ikizi donuk
    primary = _payload(now, kulce_age=720, ds_kulce_age=720, kulce_bid=6000.0)
    # altinapi (secondary): KULCEALTIN taze
    secondary = _payload(now, kulce_age=2, ds_kulce_age=2, kulce_bid=6010.0)
    uf = unfilled_primaries(primary, now)
    events = patch_from_secondary(primary, secondary, uf, now)
    assert any(e["primary"] == "SARRAFIYE.KULCEALTIN" and e["type"] == "cross_provider" for e in events)
    # finansveri verisi artık altinapi değerini gösterir
    assert primary["SARRAFIYE"]["KULCEALTIN"]["bid"] == 6010.0


def test_patch_skips_when_secondary_also_stale():
    now = datetime.now(timezone.utc)
    primary = _payload(now, kulce_age=720, ds_kulce_age=720, kulce_bid=6000.0)
    secondary = _payload(now, kulce_age=720, ds_kulce_age=720, kulce_bid=6010.0)  # altinapi de donuk
    uf = unfilled_primaries(primary, now)
    events = patch_from_secondary(primary, secondary, uf, now)
    assert events == []
    assert primary["SARRAFIYE"]["KULCEALTIN"]["bid"] == 6000.0  # dokunulmadı


def test_freshest_mapped_age():
    now = datetime.now(timezone.utc)
    f = _payload(now, kulce_age=120, ds_kulce_age=300)  # en taze 120sn
    age = freshest_mapped_age(f, now)
    assert age is not None and 115 <= age <= 125


def test_resolve_fresh_prefers_primary_then_alt():
    now = datetime.now(timezone.utc)
    f = _payload(now, kulce_age=5, ds_kulce_age=5, kulce_bid=6000.0, ds_bid=6001.0)
    assert resolve_fresh(f, "SARRAFIYE.KULCEALTIN", now) == (6000.0, 6090.0)
    # primary donuk → ikize düşer
    f2 = _payload(now, kulce_age=720, ds_kulce_age=5, kulce_bid=6000.0, ds_bid=6001.0)
    assert resolve_fresh(f2, "SARRAFIYE.KULCEALTIN", now) == (6001.0, 6091.0)


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
