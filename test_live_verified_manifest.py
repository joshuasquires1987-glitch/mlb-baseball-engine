import pytest

from live_verified_manifest import (
    assert_manifest_matches_slate,
    parse_verified_manifest,
)


def payload():
    return {
        "game_pk": "123",
        "verified_at_utc": "2026-08-12T12:00:00Z",
        "home_starter_id": "10",
        "away_starter_id": "20",
        "lights": {
            "starter": "green",
            "lineup": "green",
            "bullpen": "green",
            "weather": "green",
            "roster_news": "green",
            "umpire": "yellow",
        },
        "evidence": {
            "starter": "source-a",
            "lineup": "source-b",
            "bullpen": "source-c",
            "weather": "source-d",
            "roster_news": "source-e",
        },
        "context": {
            "home_field_score": 0.10,
            "park_score": 0.0,
            "weather_score": 0.0,
            "travel_rest_score": 0.0,
            "platoon_score": 0.0,
        },
    }


def test_verified_manifest_requires_all_green():
    p = payload()
    p["lights"]["lineup"] = "yellow"
    with pytest.raises(RuntimeError, match="lineup"):
        parse_verified_manifest(p)


def test_verified_manifest_requires_evidence():
    p = payload()
    p["evidence"]["weather"] = ""
    with pytest.raises(ValueError, match="weather"):
        parse_verified_manifest(p)


def test_starter_change_forces_failure():
    m = parse_verified_manifest(payload())
    game = {
        "game_pk": "123",
        "home_probable_starter_id": "999",
        "away_probable_starter_id": "20",
    }
    with pytest.raises(RuntimeError, match="home starter changed"):
        assert_manifest_matches_slate(m, game)
