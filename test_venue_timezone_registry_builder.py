import pytest
from mlb_venue_runtime import timezone_record_from_venue
from venue_timezone_registry_builder import build_registry, unique_venue_ids
from venue_registry_audit import audit_registry

def games():
    return [
        {"venue_id":"31"},
        {"venue_id":"31"},
        {"venue_id":"10"},
    ]

def fake_fetch(vid):
    return {
        "id": int(vid),
        "name": f"Park {vid}",
        "timeZone": {"id":"America/New_York","offset":-4,"tz":"EDT"},
    }

def test_unique_venues():
    assert unique_venue_ids(games()) == ["10","31"]

def test_timezone_record_uses_mlb_offset():
    r = timezone_record_from_venue(fake_fetch("31"), "31")
    assert r["utc_offset_hours"] == -4
    assert r["source"] == "MLB-StatsAPI-venue"

def test_missing_offset_fails_closed():
    with pytest.raises(ValueError):
        timezone_record_from_venue({"id":31,"timeZone":{}}, "31")

def test_registry_complete():
    reg = build_registry(games(), venue_fetcher=fake_fetch)
    assert reg["complete"]
    assert len(reg["rows"]) == 2
    assert audit_registry(games(), reg)["complete"]

def test_registry_records_fetch_errors():
    def broken(vid):
        if vid == "31":
            raise RuntimeError("boom")
        return fake_fetch(vid)
    reg = build_registry(games(), venue_fetcher=broken)
    assert not reg["complete"]
    assert reg["errors"][0]["venue_id"] == "31"
