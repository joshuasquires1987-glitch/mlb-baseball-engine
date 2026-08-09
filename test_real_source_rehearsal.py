import json
from pathlib import Path
from schedule_fixture_adapter import validate_full_slate
from rehearsal_audit import audit_live_slate
from official_source_registry import normalize_team_code

ROOT=Path(__file__).parent

def test_today_full_slate():
    rows=json.loads((ROOT/"live_slate_2026-08-09.json").read_text())
    norm=validate_full_slate(rows,expected_games=15)
    assert len(norm)==15
    assert len({x for r in norm for x in (r["away_team"],r["home_team"])})==30

def test_endpoints_of_slate():
    a=audit_live_slate(ROOT/"live_slate_2026-08-09.json")
    assert a["first_game"]=="CIN@WSH"
    assert a["last_game"]=="HOU@SD"
    assert a["schedule_structure_pass"] is True

def test_team_validation():
    assert normalize_team_code("tor")=="TOR"
    try:
        normalize_team_code("XXX")
        assert False
    except ValueError:
        pass
