def _clip(x, lo=-3.0, hi=3.0):
    return max(lo, min(hi, float(x)))

def scores_from_calibrated_features(features, coefficients):
    required = (
        "park_factor_delta",
        "temperature_delta_f",
        "wind_out_mph",
        "wind_in_mph",
        "travel_timezone_delta_hours",
        "rest_days_delta",
        "platoon_lineup_delta",
    )
    missing = [k for k in required if k not in features]
    if missing:
        raise ValueError(f"missing calibrated context features: {missing}")

    c = coefficients

    park = _clip(float(features["park_factor_delta"]) * float(c["park_factor_delta"]))

    weather_raw = (
        float(features["temperature_delta_f"]) * float(c["temperature_delta_f"])
        + float(features["wind_out_mph"]) * float(c["wind_out_mph"])
        + float(features["wind_in_mph"]) * float(c["wind_in_mph"])
    )
    weather = _clip(weather_raw)

    travel_raw = (
        float(features["travel_timezone_delta_hours"]) * float(c["travel_timezone_delta_hours"])
        + float(features["rest_days_delta"]) * float(c["rest_days_delta"])
    )
    travel_rest = _clip(travel_raw)

    platoon = _clip(
        float(features["platoon_lineup_delta"]) * float(c["platoon_lineup_delta"])
    )

    return {
        "park_score": park,
        "weather_score": weather,
        "travel_rest_score": travel_rest,
        "platoon_score": platoon,
        "provenance": {
            "park_score": "calibrated-challenger",
            "weather_score": "calibrated-challenger",
            "travel_rest_score": "calibrated-challenger",
            "platoon_score": "calibrated-challenger",
        },
    }
