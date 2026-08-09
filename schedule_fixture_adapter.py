from official_source_registry import normalize_team_code

def normalize_schedule_fixture(rows):
    out=[]
    seen=set()
    for row in rows:
        away=normalize_team_code(row["away"])
        home=normalize_team_code(row["home"])
        key=(away,home,row["start_et"])
        if key in seen:
            raise ValueError(f"Duplicate schedule row: {key}")
        seen.add(key)
        out.append({
            "away_team":away,
            "home_team":home,
            "start_et":row["start_et"],
            "source":"MLB.com schedule",
            "game_date":row["game_date"],
        })
    return out

def validate_full_slate(rows,expected_games=None):
    norm=normalize_schedule_fixture(rows)
    teams=[x for r in norm for x in (r["away_team"],r["home_team"])]
    if len(teams) != len(set(teams)):
        raise ValueError("A team appears more than once; doubleheaders need explicit game IDs.")
    if expected_games is not None and len(norm) != int(expected_games):
        raise ValueError(f"Expected {expected_games} games, found {len(norm)}")
    return norm
