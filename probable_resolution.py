def normalize_name(name):
    if name is None: return None
    return " ".join(str(name).replace("’","'").strip().lower().split())

def resolve_probable_ids(probable,name_to_id):
    away_id=name_to_id.get(normalize_name(probable.away_pitcher_name)) if probable.away_pitcher_name else None
    home_id=name_to_id.get(normalize_name(probable.home_pitcher_name)) if probable.home_pitcher_name else None
    return {
        "game_key":probable.game_key,
        "away_pitcher_name":probable.away_pitcher_name,
        "home_pitcher_name":probable.home_pitcher_name,
        "away_pitcher_id":away_id,
        "home_pitcher_id":home_id,
        "starter_integrity":"green" if away_id and home_id else "red",
        "resolution_complete":bool(away_id and home_id),
    }
