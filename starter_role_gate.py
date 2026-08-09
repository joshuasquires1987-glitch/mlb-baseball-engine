NORMAL_STARTER_ROLES={"starter"}
AMBIGUOUS_ROLES={"opener","bullpen_game","opener_or_bullpen_game","unknown"}

def starter_role_status(role,confidence):
    role=str(role).lower()
    confidence=str(confidence).lower()
    if role in NORMAL_STARTER_ROLES and confidence=="green":
        return "green"
    if role in AMBIGUOUS_ROLES:
        return "red"
    return "yellow"

def matchup_role_ready(away,home):
    return (
        starter_role_status(away.get("role"),away.get("role_confidence"))=="green"
        and starter_role_status(home.get("role"),home.get("role_confidence"))=="green"
    )

def choose_clean_rehearsal_matchup(matchups):
    for game_key,data in matchups.items():
        if matchup_role_ready(data["away"],data["home"]):
            return game_key
    return None
