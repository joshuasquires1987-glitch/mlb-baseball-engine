import pandas as pd
import pytest

import live_verified_probability as live


def manifest():
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


def test_find_game_requires_exact_game_pk(monkeypatch):
    monkeypatch.setattr(
        live,
        "live_slate",
        lambda d: [{"game_pk": "123"}],
    )
    assert live._find_game("2026-08-12", "123")["game_pk"] == "123"
    with pytest.raises(RuntimeError):
        live._find_game("2026-08-12", "999")
