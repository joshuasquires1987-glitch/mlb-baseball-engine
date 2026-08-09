from pathlib import Path
from starter_lineup_rehearsal import load_probables,audit_probables

ROOT=Path(__file__).parent

def test_fixture_real_world_shape():
    rows=load_probables(ROOT/"live_probables_2026-08-09.json")
    assert len(rows)==4
    assert sum(x.both_named for x in rows)==3
    ath=next(x for x in rows if x.game_key=="ATH@BOS")
    assert ath.home_pitcher_name is None

def test_names_without_ids_not_production_ready():
    rows=audit_probables(ROOT/"live_probables_2026-08-09.json")
    assert all(not r["starter_ids_resolved"] for r in rows)
    assert all(r["starter_integrity"]=="red" for r in rows)

def test_resolved_ids_make_three_model_ready_not_ambiguous_boston():
    ids={
        "brady singer":"SINGER_ID","brad lord":"LORD_ID",
        "sean manaea":"MANAEA_ID","jared jones":"JONES_ID",
        "shane bieber":"BIEBER_ID","jesús luzardo":"LUZARDO_ID",
        "j.t. ginn":"GINN_ID",
    }
    rows=audit_probables(ROOT/"live_probables_2026-08-09.json",ids)
    assert sum(r["model_ready"] for r in rows)==3
    assert not next(r for r in rows if r["game_key"]=="ATH@BOS")["model_ready"]

def test_lineups_gate_bet_readiness():
    ids={
        "brady singer":"1","brad lord":"2",
        "sean manaea":"3","jared jones":"4",
        "shane bieber":"5","jesús luzardo":"6",
    }
    lineups={"CIN@WSH":(True,True),"NYM@PIT":(False,False),"TOR@PHI":(True,False)}
    rows=audit_probables(ROOT/"live_probables_2026-08-09.json",ids,lineups)
    assert next(r for r in rows if r["game_key"]=="CIN@WSH")["bet_ready"]
    assert not next(r for r in rows if r["game_key"]=="NYM@PIT")["bet_ready"]
