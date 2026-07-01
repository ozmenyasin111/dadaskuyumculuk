"""Sağlayıcı (finansveri ↔ altinapi) failover testleri."""

from datetime import datetime, timedelta, timezone

import pytest

from app.services import altinapi, finansveri, provider
from app.services.provider import AllProvidersDown, fetch_prices_with_failover


@pytest.fixture(autouse=True)
def _reset():
    provider.reset_state()
    yield
    provider.reset_state()


def _fresh_payload(now, age_sec=5):
    """Sağlayıcı sağlığı sembol timestamp'ından (freshest_mapped_age) ölçülür; bu yüzden
    haritadaki bir sembolü verilen yaşla üretiyoruz."""
    ts = (now - timedelta(seconds=age_sec)).isoformat().replace("+00:00", "Z")
    return {
        "fiyatlar": {"SARRAFIYE": {"KULCEALTIN": {"bid": 6000.0, "ask": 6090.0, "timestamp": ts}}},
        "guncellendi": int((now.timestamp() - age_sec) * 1000),
    }


async def test_uses_finansveri_when_fresh(monkeypatch):
    now = datetime.now(timezone.utc)
    async def fv(**kw): return _fresh_payload(now, 5)
    monkeypatch.setattr(finansveri, "fetch_prices", fv)
    payload, prov, events = await fetch_prices_with_failover(now)
    assert prov == "finansveri"
    assert events == []


async def test_switches_to_altinapi_when_finansveri_down(monkeypatch):
    now = datetime.now(timezone.utc)
    async def fv(**kw): raise finansveri.FinansveriError("down")
    async def aa(): return _fresh_payload(now, 2)
    monkeypatch.setattr(finansveri, "fetch_prices", fv)
    monkeypatch.setattr(altinapi, "fetch_prices", aa)
    payload, prov, events = await fetch_prices_with_failover(now)
    assert prov == "altinapi"
    assert len(events) == 1 and events[0]["type"] == "switch"
    assert events[0]["reason"] == "yanıt vermedi"


async def test_switches_to_altinapi_when_finansveri_stale(monkeypatch):
    now = datetime.now(timezone.utc)
    # finansveri 200 ama guncellendi 10 dk eski (eşik 3 dk) → donuk
    async def fv(**kw): return _fresh_payload(now, 600)
    async def aa(): return _fresh_payload(now, 2)
    monkeypatch.setattr(finansveri, "fetch_prices", fv)
    monkeypatch.setattr(altinapi, "fetch_prices", aa)
    payload, prov, events = await fetch_prices_with_failover(now)
    assert prov == "altinapi"
    assert events[0]["type"] == "switch" and events[0]["reason"] == "tüm veri donuk"


async def test_recovers_to_finansveri(monkeypatch):
    now = datetime.now(timezone.utc)
    # önce altinapi'ye düş
    async def fv_down(**kw): raise finansveri.FinansveriError("down")
    async def aa(): return _fresh_payload(now, 2)
    monkeypatch.setattr(finansveri, "fetch_prices", fv_down)
    monkeypatch.setattr(altinapi, "fetch_prices", aa)
    await fetch_prices_with_failover(now)
    assert provider.active_provider() == "altinapi"
    # finansveri düzeldi
    async def fv_up(**kw): return _fresh_payload(now, 3)
    monkeypatch.setattr(finansveri, "fetch_prices", fv_up)
    payload, prov, events = await fetch_prices_with_failover(now)
    assert prov == "finansveri"
    assert len(events) == 1 and events[0]["type"] == "recover"


async def test_all_providers_down_raises(monkeypatch):
    now = datetime.now(timezone.utc)
    async def fv(**kw): raise finansveri.FinansveriError("down")
    async def aa(): raise altinapi.AltinapiError("down")
    monkeypatch.setattr(finansveri, "fetch_prices", fv)
    monkeypatch.setattr(altinapi, "fetch_prices", aa)
    with pytest.raises(AllProvidersDown):
        await fetch_prices_with_failover(now)


async def test_no_duplicate_switch_event(monkeypatch):
    now = datetime.now(timezone.utc)
    async def fv(**kw): raise finansveri.FinansveriError("down")
    async def aa(): return _fresh_payload(now, 2)
    monkeypatch.setattr(finansveri, "fetch_prices", fv)
    monkeypatch.setattr(altinapi, "fetch_prices", aa)
    _, _, ev1 = await fetch_prices_with_failover(now)
    assert len(ev1) == 1  # ilk geçiş
    _, _, ev2 = await fetch_prices_with_failover(now)
    assert ev2 == []  # zaten altinapi'de → tekrar bildirim yok
