def lineup_status_from_boxscore(payload,team_side):
    return bool(payload.get("teams",{}).get(team_side,{}).get("battingOrder") or [])
def both_lineups_confirmed(payload):
    return lineup_status_from_boxscore(payload,"home") and lineup_status_from_boxscore(payload,"away")
