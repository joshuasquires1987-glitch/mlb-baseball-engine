import json
from pathlib import Path
from schedule_fixture_adapter import validate_full_slate

def audit_live_slate(path):
    rows=json.loads(Path(path).read_text())
    norm=validate_full_slate(rows,expected_games=15)
    return {
        "game_date":norm[0]["game_date"] if norm else None,
        "games":len(norm),
        "teams":len({x for r in norm for x in (r["away_team"],r["home_team"])}),
        "first_game":f'{norm[0]["away_team"]}@{norm[0]["home_team"]}' if norm else None,
        "last_game":f'{norm[-1]["away_team"]}@{norm[-1]["home_team"]}' if norm else None,
        "schedule_structure_pass":True,
    }
