from live_manifest_generator import (
    FROZEN_V11_CONTEXT,
    lineup_evidence,
    starter_evidence,
    weather_evidence,
)


def game():
    return {
        "home_probable_starter_id": "10",
        "away_probable_starter_id": "20",
    }


def feed_starters():
    return {
        "home": {"id": "10", "name": "H"},
        "away": {"id": "20", "name": "A"},
    }


def test_mlb_only_starter_evidence_is_yellow_not_green():
    ev = starter_evidence(game(), feed_starters())
    assert ev["light"] == "yellow"


def test_independent_matching_secondary_starter_evidence_is_green():
    ev = starter_evidence(
        game(),
        feed_starters(),
        {
            "home_starter_id": "10",
            "away_starter_id": "20",
            "source": "second reliable source",
        },
    )
    assert ev["light"] == "green"


def test_complete_lineups_are_green():
    ev = lineup_evidence({
        "home": [str(x) for x in range(9)],
        "away": [str(x) for x in range(9, 18)],
    })
    assert ev["light"] == "green"


def test_complete_weather_is_green():
    ev = weather_evidence({
        "temperature_2m_c": 20,
        "relative_humidity_2m_pct": 55,
        "wind_speed_10m_kmh": 10,
        "wind_direction_10m_deg": 180,
    })
    assert ev["light"] == "green"


def test_bt0093_does_not_invent_unvalidated_context_scores():
    assert FROZEN_V11_CONTEXT == {
        "home_field_score": 0.10,
        "park_score": 0.0,
        "weather_score": 0.0,
        "travel_rest_score": 0.0,
        "platoon_score": 0.0,
    }
