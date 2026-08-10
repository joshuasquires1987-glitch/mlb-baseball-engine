from datetime import datetime, timezone
from context_calibration_schema import validate_training_row

def _dt(x):
    if isinstance(x, datetime):
        v=x
    else:
        v=datetime.fromisoformat(str(x).replace("Z","+00:00"))
    if v.tzinfo is None:
        v=v.replace(tzinfo=timezone.utc)
    return v.astimezone(timezone.utc)

def rest_days(previous_game_time, current_game_time):
    if previous_game_time is None:
        return None
    hours=(_dt(current_game_time)-_dt(previous_game_time)).total_seconds()/3600.0
    return max(0, int(hours//24)-1)

def build_training_row(game, prior_state, park_factor, pregame_snapshot):
    home_runs=game.get("home_runs")
    away_runs=game.get("away_runs")
    if home_runs is None or away_runs is None or home_runs==away_runs:
        raise ValueError("completed non-tie outcome required")

    if not pregame_snapshot or pregame_snapshot.get("captured_before_first_pitch") is not True:
        raise ValueError("leakage-safe pregame lineup snapshot required")
    if pregame_snapshot.get("platoon_lineup_delta") is None:
        raise ValueError("pregame platoon_lineup_delta required")

    game_time=game["game_time_utc"]
    home_prev=prior_state.get(game["home_team"],{}).get("previous_game_time_utc")
    away_prev=prior_state.get(game["away_team"],{}).get("previous_game_time_utc")

    home_rest=rest_days(home_prev,game_time)
    away_rest=rest_days(away_prev,game_time)
    if home_rest is None or away_rest is None:
        raise ValueError("prior schedule state required for both teams")

    home_tz=float(game["home_venue_utc_offset_hours"])
    away_prev_tz=float(prior_state[game["away_team"]]["previous_venue_utc_offset_hours"])
    home_prev_tz=float(prior_state[game["home_team"]]["previous_venue_utc_offset_hours"])

    travel_timezone_delta_hours = abs(away_prev_tz-home_tz) - abs(home_prev_tz-home_tz)
    rest_days_delta = home_rest-away_rest

    weather=game.get("pregame_weather") or {}
    temp=weather.get("temp_f")
    wind_out=weather.get("wind_out_mph")
    wind_in=weather.get("wind_in_mph")
    if None in (temp,wind_out,wind_in):
        raise ValueError("pregame weather observation required")

    row={
        "game_id":str(game["game_id"]),
        "game_date":str(game["game_date"]),
        "home_win":1 if float(home_runs)>float(away_runs) else 0,
        "park_factor_delta":float(park_factor)-1.0,
        "temperature_delta_f":float(temp)-70.0,
        "wind_out_mph":float(wind_out),
        "wind_in_mph":float(wind_in),
        "travel_timezone_delta_hours":float(travel_timezone_delta_hours),
        "rest_days_delta":float(rest_days_delta),
        "platoon_lineup_delta":float(pregame_snapshot["platoon_lineup_delta"]),
    }
    validate_training_row(row)
    return row
