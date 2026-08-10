import pytest
from historical_context_dataset import build_training_row,rest_days
from historical_weather_parser import parse_wind,parse_pregame_weather
from chronological_split import chronological_split,assert_no_date_overlap

def game():
    return {
      "game_id":"g1","game_date":"2025-07-01","game_time_utc":"2025-07-01T23:00:00Z",
      "home_team":"PIT","away_team":"NYM",
      "home_runs":4,"away_runs":2,
      "home_venue_utc_offset_hours":-4,
      "pregame_weather":{"temp_f":80,"wind_out_mph":8,"wind_in_mph":0},
    }

def prior():
    return {
      "PIT":{"previous_game_time_utc":"2025-06-30T17:00:00Z","previous_venue_utc_offset_hours":-4},
      "NYM":{"previous_game_time_utc":"2025-06-29T17:00:00Z","previous_venue_utc_offset_hours":-7},
    }

def snap():
    return {"captured_before_first_pitch":True,"platoon_lineup_delta":0.25}

def test_build_row_direction_and_label():
    r=build_training_row(game(),prior(),0.96,snap())
    assert r["home_win"]==1
    assert r["park_factor_delta"]==pytest.approx(-0.04)
    assert r["temperature_delta_f"]==10
    assert r["travel_timezone_delta_hours"]==3
    assert r["rest_days_delta"]<0

def test_completed_game_without_pregame_lineup_snapshot_is_rejected():
    with pytest.raises(ValueError,match="pregame lineup snapshot"):
        build_training_row(game(),prior(),0.96,None)

def test_rest_days_uses_only_prior_timestamp():
    assert rest_days("2025-06-30T23:00:00Z","2025-07-01T23:00:00Z")==0
    assert rest_days("2025-06-29T23:00:00Z","2025-07-01T23:00:00Z")==1

def test_wind_parser():
    assert parse_wind("8 mph, Out To RF")==(8.0,0.0)
    assert parse_wind("12 mph, In From LF")==(0.0,12.0)
    assert parse_wind("5 mph, L To R")==(0.0,0.0)

def test_weather_parser_requires_usable_observation():
    assert parse_pregame_weather({"weather":{"temp":78,"wind":"9 mph, Out To CF"}})["wind_out_mph"]==9
    assert parse_pregame_weather({"weather":{"wind":"9 mph, Out To CF"}}) is None

def test_chronological_split():
    rows=[{"game_id":str(i),"game_date":f"2025-07-{i:02d}"} for i in range(1,11)]
    tr,ho=chronological_split(rows,3)
    assert len(tr)==7 and len(ho)==3
    assert assert_no_date_overlap(tr,ho)
