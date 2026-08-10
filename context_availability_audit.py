REQUIRED = (
    "final_outcome",
    "game_time",
    "venue",
    "pregame_weather",
    "park_factor",
    "venue_timezone",
    "prior_schedule_state",
    "pregame_lineup_snapshot",
)

def audit_game(game, weather, park_record, venue_record, prior_state, lineup_snapshot):
    checks={
        "final_outcome": game.get("home_runs") is not None and game.get("away_runs") is not None
                         and game.get("home_runs") != game.get("away_runs"),
        "game_time": game.get("game_time_utc") is not None,
        "venue": game.get("venue_id") is not None,
        "pregame_weather": weather is not None,
        "park_factor": park_record is not None and park_record.get("park_factor") is not None
                       and park_record.get("frozen_through_date") is not None,
        "venue_timezone": venue_record is not None and venue_record.get("utc_offset_hours") is not None,
        "prior_schedule_state": prior_state is not None
                                and prior_state.get("home") is not None
                                and prior_state.get("away") is not None,
        "pregame_lineup_snapshot": lineup_snapshot is not None
                                   and lineup_snapshot.get("captured_before_first_pitch") is True
                                   and lineup_snapshot.get("platoon_lineup_delta") is not None,
    }
    missing=[k for k,v in checks.items() if not v]
    return {"usable":not missing,"checks":checks,"missing":missing}

def summarize_audit(results):
    counts={k:0 for k in REQUIRED}
    usable=0
    for r in results:
        if r["usable"]:
            usable+=1
        for k in r["missing"]:
            counts[k]+=1
    total=len(results)
    return {
        "games_audited":total,
        "usable_games":usable,
        "usable_rate":(usable/total if total else 0.0),
        "missing_counts":counts,
        "meets_650_game_target":usable>=650,
    }
