from pathlib import Path
from engine_types import BaseballInputs,IntegrityState,PriceInput
from operational_pipeline import OperationalPipeline
from daily_report import build_daily_report

ROOT=Path(__file__).parent

def game():
    return BaseballInputs("DRY1","2026-08-09","HOME","AWAY",
      {"starting_pitcher":.5,"underlying_team_strength":.25,"bullpen":.15,
       "confirmed_lineup_offense":.15,"platoon_matchup_fit":.05,"defense":.05,
       "home_field":.1,"park":0,"weather":0,"travel_rest_circadian":0,
       "starting_pitcher_talent_state":.5,"bullpen_talent_state":.15,
       "expected_starter_depth":.1,"bullpen_exposure_quality":.1},
      IntegrityState("green","green","green","green","green","yellow"))

def test_full_pipeline():
    p=OperationalPipeline(ROOT,1000)
    record,prod,shadow=p.analyze(game(),PriceInput(2.20,1.70,"first"))
    assert prod.model_version=="v1.1"
    assert shadow.model_version=="v1.2-RC1"
    assert prod.frozen and shadow.frozen
    assert record["shadow"]["controls_bets"] is False

    # Explicit confirmation is required.
    try:
        p.confirm_wager(prod,"home",2.20,50,False)
        assert False
    except PermissionError:
        pass

    wager=p.confirm_wager(prod,"home",2.20,50,True)
    assert wager.original_model_probability==prod.home_win_probability
    settlement=p.settle(wager,"win")
    assert settlement.profit_loss_cad==60.0
    assert p.wagers.bankroll()==1060.0

    p.validate_pair(prod,shadow,True,2.20,2.20,stake=50,pnl=60)
    assert p.validation.summary("v1.1")["n"]==1
    assert p.validation.summary("v1.2-RC1")["n"]==1
    gate=p.rc1_gate()
    assert gate["status"]=="SHADOW_CONTINUES"
    assert gate["automatic_promotion"] is False

def test_report():
    p=OperationalPipeline(ROOT)
    record,prod,shadow=p.analyze(game(),PriceInput(2.20,1.70,"first"))
    report=build_daily_report([record])
    assert report["games_analyzed"]==1

def test_shadow_cannot_bet():
    p=OperationalPipeline(ROOT)
    record,prod,shadow=p.analyze(game(),PriceInput(2.20,1.70,"first"))
    try:
        p.confirm_wager(shadow,"home",2.20,50,True)
        assert False
    except ValueError:
        pass
