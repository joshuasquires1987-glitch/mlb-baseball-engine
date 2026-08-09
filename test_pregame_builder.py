from pregame_inputs import StarterState,TeamState,ContextState,PregameFacts
from pregame_feature_builder import PregameFeatureBuilder

def facts(home_sp="HSP",away_sp="ASP",confirmed=True):
    return PregameFacts(
        "G1","2026-08-09","HOME","AWAY",
        StarterState(home_sp,.7,18,confirmed),
        StarterState(away_sp,.4,15,confirmed),
        TeamState(.6,.7,.55,.65),
        TeamState(.5,.5,.50,.45),
        ContextState(.10,.00,.00,.00,.05),
        lineup_confirmed=False,bullpen_current=True,weather_current=True,
        roster_news_clear=True,umpire_known=False
    )

def test_build_contains_both_model_feature_sets():
    b=PregameFeatureBuilder()
    x=b.build(facts())
    assert "starting_pitcher" in x.features
    assert "starting_pitcher_talent_state" in x.features
    assert "expected_starter_depth" in x.features
    assert "bullpen_exposure_quality" in x.features

def test_directionality():
    b=PregameFeatureBuilder()
    x=b.build(facts())
    assert x.features["starting_pitcher"]>0
    assert x.features["underlying_team_strength"]>0
    assert x.features["bullpen"]>0

def test_lineup_uncertainty_is_yellow_not_red():
    b=PregameFeatureBuilder()
    x=b.build(facts())
    assert x.integrity.lineup=="yellow"
    assert x.integrity.starter=="green"
    assert not x.integrity.unresolved_red()

def test_unconfirmed_starter_is_red():
    b=PregameFeatureBuilder()
    x=b.build(facts(confirmed=False))
    assert x.integrity.starter=="red"
    assert x.integrity.unresolved_red()

def test_starter_change_detected():
    b=PregameFeatureBuilder()
    f1=facts()
    b.build(f1)
    f2=facts(home_sp="NEW")
    assert b.starter_changed(f2)

def test_same_starter_not_changed():
    b=PregameFeatureBuilder()
    f1=facts()
    b.build(f1)
    assert not b.starter_changed(f1)
