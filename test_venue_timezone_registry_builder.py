import pytest

from mlb_venue_runtime import venue_coordinates, venue_url
from venue_timezone_registry_builder import build_registry
from venue_registry_audit import audit_registry
from venue_time_at_game import utc_offset_hours_at_game


def games():
    return [
        {"venue_id": "31"},
        {"venue_id": "31"},
        {"venue_id": "10"},
    ]


def fake_fetch(vid):
    coords = {
        "31": (40.4469, -80.0057),
        "10": (43.6414, -79.3894),
    }
    lat, lon = coords[str(vid)]
    return {
        "id": int(vid),
        "name": f"Park {vid}",
        "location": {
            "defaultCoordinates": {
                "latitude": lat,
                "longitude": lon,
            }
        },
    }


def fake_lookup(lat, lon):
    if lat > 42:
        return "America/Toronto"
    return "America/New_York"


def test_location_hydration_is_requested():
    assert "hydrate=location" in venue_url("31")


def test_coordinates_are_read_from_mlb_location():
    lat, lon = venue_coordinates(fake_fetch("31"), "31")
    assert lat == pytest.approx(40.4469)
    assert lon == pytest.approx(-80.0057)


def test_registry_stores_iana_timezone():
    reg = build_registry(games(), venue_fetcher=fake_fetch, timezone_lookup=fake_lookup)
    assert reg["complete"]
    assert len(reg["rows"]) == 2
    assert all(row.get("timezone_id") for row in reg["rows"])
    assert all("utc_offset_hours" not in row for row in reg["rows"])


def test_registry_audit_accepts_timezone_ids():
    reg = build_registry(games(), venue_fetcher=fake_fetch, timezone_lookup=fake_lookup)
    audit = audit_registry(games(), reg)
    assert audit["complete"]


def test_offset_is_resolved_at_game_time():
    assert utc_offset_hours_at_game(
        "America/New_York", "2025-07-01T23:00:00Z"
    ) == -4
    assert utc_offset_hours_at_game(
        "America/New_York", "2025-12-01T23:00:00Z"
    ) == -5
