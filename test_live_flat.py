from pathlib import Path
from engine_types import BaseballInputs,IntegrityState,PriceInput
from live_workflow import LiveWorkflow,information_status
from price_snapshots import DailyPriceStore
ROOT=Path(__file__).parent
def game(i=None):
    return BaseballInputs("G1","2026-08-09","HOME","AWAY",
      {"starting_pitcher":.4,"underlying_team_strength":.2,"bullpen":.1,"confirmed_lineup_offense":.1,"home_field":.1,
       "starting_pitcher_talent_state":.4,"bullpen_talent_state":.1,"expected_starter_depth":.1,"bullpen_exposure_quality":.1},
      i or IntegrityState("green","yellow","green","green","green","yellow"))
def test_dual():
    r=LiveWorkflow(ROOT).analyze_game(game(),PriceInput(2.1,1.8,"first"))
    assert r["production"]["version"]=="v1.1" and r["shadow"]["model_version"]=="v1.2-RC1"
    assert not r["shadow"]["controls_bets"] and not r["shadow"]["controls_stakes"]
def test_red_blocks():
    r=LiveWorkflow(ROOT).analyze_game(game(IntegrityState("red","green","green","green","green")),PriceInput(2.5,1.6,"first"))
    assert not r["production"]["decision"]["eligible"]
def test_umpire_nonblocking():
    i=IntegrityState("green","green","green","green","green","red")
    assert not i.unresolved_red()
def test_requires_price():
    try: LiveWorkflow(ROOT).analyze_game(game(),None); assert False
    except ValueError: pass
def test_snapshots():
    s=DailyPriceStore()
    s.add("G",PriceInput(2.0,1.8,"1")); s.add("G",PriceInput(2.1,1.75,"2")); s.add("G",PriceInput(2.2,1.7,"4"))
    assert s.get("G")["first"]["snapshot_label"]=="1"
    assert s.get("G")["latest"]["snapshot_label"]=="4"
    assert len(s.export_rows())==2
def test_lights():
    x=information_status(IntegrityState("green","yellow","red","green","yellow"))
    assert "starter" in x["green"] and "lineup" in x["yellow"] and "bullpen" in x["red"]
