from pathlib import Path
from game_log_importer import innings_to_outs,import_pitching_row
from production_history_gate import exact_history_status,starter_history_to_calculator_rows
from history_snapshot_loader import load_snapshot

ROOT=Path(__file__).parent

def test_innings_not_decimal():
    assert innings_to_outs("5.2")==17
    assert innings_to_outs("4.1")==13
    assert innings_to_outs("6.0")==18

def test_missing_bf_blocks_production():
    r=import_pitching_row("2026-08-04","6.0",2,None,"source")
    assert not r.production_ready
    assert not exact_history_status([r])["ready"]

def test_exact_bf_allows_production():
    r=import_pitching_row("2026-08-04","6.0",2,25,"source")
    assert r.production_ready
    rows=starter_history_to_calculator_rows([r])
    assert rows[0]["outs"]==18 and rows[0]["batters_faced"]==25

def test_real_snapshot_is_research_ready_but_not_production_exact():
    x=load_snapshot(ROOT/"nym_pit_starter_history_snapshot_2026-08-09.json")
    assert len(x["Sean Manaea"])>=5
    assert len(x["Jared Jones"])>=5
    assert not exact_history_status(x["Sean Manaea"])["ready"]
    assert not exact_history_status(x["Jared Jones"])["ready"]

def test_gate_raises_on_approximation():
    r=import_pitching_row("2026-08-04","4.0",3,None,"source")
    try:
        starter_history_to_calculator_rows([r])
        assert False
    except ValueError:
        pass
