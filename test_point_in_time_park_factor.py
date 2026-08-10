import pytest
from point_in_time_park_factor import (
    build_point_in_time_records,
    shrink_to_neutral,
)
from park_factor_registry import PointInTimeParkRegistry

def g(pk,date,venue,h,a):
    return {
        "game_pk":str(pk),
        "game_time_utc":date,
        "venue_id":str(venue),
        "home_runs":h,
        "away_runs":a,
    }

def test_current_game_is_not_in_its_own_factor():
    games=[
        g(1,"2025-01-01T18:00:00Z",31,5,5),
        g(2,"2025-01-02T18:00:00Z",31,4,4),
        g(3,"2025-01-03T18:00:00Z",31,100,100),
    ]
    r=build_point_in_time_records(
        games,"2025-01-03","2025-01-03",
        min_venue_games=2,lookback_days=365,shrink_games=0,
    )
    rec=r["records"][0]
    assert rec["venue_mean_total_runs"]==9.0
    assert rec["league_mean_total_runs"]==9.0
    assert rec["park_factor"]==1.0

def test_factor_uses_prior_venue_vs_prior_league():
    games=[
        g(1,"2025-01-01T18:00:00Z",31,6,6), # 12
        g(2,"2025-01-01T19:00:00Z",10,3,3), # 6
        g(3,"2025-01-02T18:00:00Z",31,5,5), # 10
        g(4,"2025-01-02T19:00:00Z",10,4,4), # 8
        g(5,"2025-01-03T18:00:00Z",31,0,0),
    ]
    r=build_point_in_time_records(
        games,"2025-01-03","2025-01-03",
        min_venue_games=2,lookback_days=365,shrink_games=0,
    )
    rec=r["records"][0]
    assert rec["venue_mean_total_runs"]==11
    assert rec["league_mean_total_runs"]==9
    assert rec["park_factor"]==pytest.approx(11/9)

def test_minimum_prior_games_fails_closed():
    r=build_point_in_time_records(
        [g(1,"2025-01-01T18:00:00Z",31,4,4)],
        "2025-01-01","2025-01-01",min_venue_games=20,
    )
    assert not r["records"]
    assert r["skipped"][0]["reason"]=="insufficient-prior-venue-games"

def test_shrinkage_moves_factor_toward_one():
    assert shrink_to_neutral(1.2,40,40)==pytest.approx(1.1)

def test_registry_is_game_specific():
    reg=PointInTimeParkRegistry([{
        "game_pk":"99","venue_id":"31","park_factor":1.03,
        "frozen_through_utc":"2025-01-01T00:00:00+00:00"
    }])
    assert reg.get_for_game("99","31")["park_factor"]==1.03
    assert reg.get("31") is None
    with pytest.raises(ValueError):
        reg.get_for_game("99","10")
