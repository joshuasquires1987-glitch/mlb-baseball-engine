import json
from pathlib import Path
from starter_role_gate import matchup_role_ready,choose_clean_rehearsal_matchup
from history_readiness import history_readiness,probability_allowed
from history_runtime_fetcher import extract_stat_splits

ROOT=Path(__file__).parent

def data():
    return json.loads((ROOT/"live_starter_role_audit_2026-08-09.json").read_text())

def test_lord_blocks_normal_start():
    d=data()
    assert not matchup_role_ready(d["CIN@WSH"]["away"],d["CIN@WSH"]["home"])

def test_manaea_jones_clean_candidate():
    d=data()
    assert matchup_role_ready(d["NYM@PIT"]["away"],d["NYM@PIT"]["home"])
    assert choose_clean_rehearsal_matchup(d)=="NYM@PIT"

def test_history_gate_requires_all_three():
    x=history_readiness({"starter_history":[1],"team_history":[1],"bullpen_history":[]})
    assert not x["ready"] and "bullpen_history" in x["missing"]

def test_probability_allowed_only_when_role_and_history_ready():
    b={"starter_history":[1],"team_history":[1],"bullpen_history":[1]}
    assert probability_allowed(True,b)
    assert not probability_allowed(False,b)

def test_statsapi_split_parser():
    p={"stats":[{"splits":[{"date":"2026-08-01"}]}]}
    assert extract_stat_splits(p)==[{"date":"2026-08-01"}]
