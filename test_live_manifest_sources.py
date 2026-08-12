from live_manifest_sources import (
    active_roster_ids,
    closest_hourly_weather,
    lineup_from_feed,
    probable_starters_from_feed,
    venue_coordinates,
)


def test_venue_coordinates():
    payload = {
        "venues": [{
            "location": {
                "defaultCoordinates": {
                    "latitude": 40.1,
                    "longitude": -73.9,
                }
            }
        }]
    }
    assert venue_coordinates(payload) == (40.1, -73.9)


def test_lineup_and_probable_starter_parsers():
    feed = {
        "gameData": {
            "probablePitchers": {
                "home": {"id": 10, "fullName": "H"},
                "away": {"id": 20, "fullName": "A"},
            }
        },
        "liveData": {
            "boxscore": {
                "teams": {
                    "home": {"battingOrder": list(range(1, 10))},
                    "away": {"battingOrder": list(range(11, 20))},
                }
            }
        },
    }
    starters = probable_starters_from_feed(feed)
    lineup = lineup_from_feed(feed)
    assert starters["home"]["id"] == "10"
    assert starters["away"]["id"] == "20"
    assert len(lineup["home"]) == 9
    assert len(lineup["away"]) == 9


def test_active_roster_ids():
    payload = {
        "roster": [
            {"person": {"id": 10}},
            {"person": {"id": 20}},
            {"person": {"id": 10}},
        ]
    }
    assert active_roster_ids(payload) == ["10", "20"]


def test_closest_weather_hour():
    payload = {
        "hourly": {
            "time": ["2026-08-12T17:00", "2026-08-12T18:00"],
            "temperature_2m": [20, 21],
            "relative_humidity_2m": [50, 55],
            "precipitation_probability": [5, 10],
            "precipitation": [0, 0],
            "surface_pressure": [1010, 1009],
            "wind_speed_10m": [10, 12],
            "wind_direction_10m": [180, 190],
        }
    }
    weather = closest_hourly_weather(payload, "2026-08-12T17:40:00Z")
    assert weather["forecast_hour_utc"].startswith("2026-08-12T18:00")
    assert weather["temperature_2m_c"] == 21
