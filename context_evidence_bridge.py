def qualification_context_from_evidence(evidence, score_inputs=None):
    score_inputs = score_inputs or {}
    provenance = score_inputs.get("provenance", {})
    return {
        "park_score": score_inputs.get("park_score"),
        "weather_score": score_inputs.get("weather_score"),
        "travel_rest_score": score_inputs.get("travel_rest_score"),
        "platoon_score": score_inputs.get("platoon_score"),
        "provenance": {
            "park_score": provenance.get("park_score", "unverified"),
            "weather_score": provenance.get("weather_score", "unverified"),
            "travel_rest_score": provenance.get("travel_rest_score", "unverified"),
            "platoon_score": provenance.get("platoon_score", "unverified"),
        },
        "evidence": {
            "lineup_confirmed": bool(evidence.get("lineup_confirmed")),
            "venue_name": evidence.get("venue_name"),
            "weather_raw": evidence.get("weather_raw"),
            "source_provenance": evidence.get("provenance", {}),
        },
    }
