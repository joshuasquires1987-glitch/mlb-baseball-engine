import pytest
from mlb_venue_runtime import venue_coordinates, venue_url
from venue_timezone_registry_builder import build_registry
from venue_time_at_game import utc_offset_hours_at_game

def games():
    return [{"venue_id":"31"}, {"venue_id":"31"}]

def fake_fetch(vid):
    return {
        "id":31,
        "name":"PNC Park",
        "location":{
            "defaultCoordinates":{
                "latitude":40.4469,
                "longitude":-80.0057,
            }
        },
    }

def fake_lookup(lat, lon):
    return "America/New_York"

def test_hydrates_location():
    assert "hydrate=location" in venue_url("31")

def test_coordinates_from_mlb():
    assert venue_coordinates(fake_fetch("31"), "31") == pytest.approx(
        (40.4469, -80.0057)
    )

def test_registry_stores_iana_zone_not_fixed_offset():
    r = build_registry(games(), fake_fetch, fake_lookup)
    assert r["complete"]
    row = r["rows"][0]
    assert row["timezone_id"] == "America/New_York"
    assert "utc_offset_hours" not in row

def test_dst_offset_is_game_date_specific():
    assert utc_offset_hours_at_game(
        "America/New_York", "2025-07-01T23:00:00Z"
    ) == -4
    assert utc_offset_hours_at_game(
        "America/New_York", "2025-12-01T23:00:00Z"
    ) == -5
