def apply_evidence_to_matchup_flags(evidence, expected_away_starter, expected_home_starter):
    return {
        "away_starter_confirmed": str(evidence.get("away_starter_id")) == str(expected_away_starter),
        "home_starter_confirmed": str(evidence.get("home_starter_id")) == str(expected_home_starter),
        "lineup_confirmed": bool(evidence.get("lineup_confirmed")),
        "weather_observation_available": all(
            evidence.get("weather_raw", {}).get(k) is not None
            for k in ("condition", "temp_f", "wind")
        ),
    }
