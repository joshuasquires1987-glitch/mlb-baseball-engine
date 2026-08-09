from daily_controller import DailyController
from retrospective import build_retrospective
from hypothesis_ledger import DEFAULT_HYPOTHESES

def test_slate_only_priced_games():
    d=DailyController("2026-08-09")
    d.ingest_slate(["G1","G2"])
    assert set(d.session.games)=={"G1","G2"}

def test_first_and_latest_prediction_ids():
    d=DailyController("2026-08-09")
    d.prediction_recorded("G","P1","SP_A")
    d.prediction_recorded("G","P2","SP_A")
    s=d.session.games["G"]
    assert s.first_prediction_id=="P1"
    assert s.latest_prediction_id=="P2"

def test_starter_change_forces_rerun():
    d=DailyController("2026-08-09")
    d.prediction_recorded("G","P1","SP_A")
    assert d.starter_change_requires_rerun("G","SP_B")
    d.prediction_recorded("G","P2","SP_B")
    assert d.session.games["G"].rerun_count==1

def test_same_starter_no_rerun():
    d=DailyController("2026-08-09")
    d.prediction_recorded("G","P1","SP_A")
    assert not d.starter_change_requires_rerun("G","SP_A")

def test_retrospective_no_mutation():
    r=build_retrospective("A","B",3,normal_variance=True)
    assert r["model_mutation_allowed"] is False

def test_h6_not_production_rule():
    h=next(x for x in DEFAULT_HYPOTHESES if x.hypothesis_id=="H6")
    assert h.status=="validated_challenger" and h.production_rule is False
