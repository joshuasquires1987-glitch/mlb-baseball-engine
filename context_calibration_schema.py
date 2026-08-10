REQUIRED_FEATURES = (
    "park_factor_delta",
    "temperature_delta_f",
    "wind_out_mph",
    "wind_in_mph",
    "travel_timezone_delta_hours",
    "rest_days_delta",
    "platoon_lineup_delta",
)

def validate_training_row(row):
    required = {"game_id", "game_date", "home_win"} | set(REQUIRED_FEATURES)
    missing = required - set(row)
    if missing:
        raise ValueError(f"training row missing {sorted(missing)}")
    if row["home_win"] not in (0, 1):
        raise ValueError("home_win must be 0 or 1")
    for key in REQUIRED_FEATURES:
        float(row[key])
    return True
