from datetime import datetime,timedelta
from starter_state_calculator import StarterStateCalculator
from team_state_calculator import TeamStateCalculator
from bullpen_state_calculator import BullpenStateCalculator

D=datetime(2026,8,9)

def test_starter_prior_only_and_better_pitcher_positive():
    rows=[
        {"date":D-timedelta(days=10),"batters_faced":25,"runs_allowed":1,"outs":18},
        {"date":D-timedelta(days=5),"batters_faced":25,"runs_allowed":2,"outs":19},
        {"date":D+timedelta(days=1),"batters_faced":25,"runs_allowed":20,"outs":3},
    ]
    x=StarterStateCalculator().calculate(rows,D)
    assert x["starts_prior"]==2
    assert x["talent_score"]>0
    assert x["expected_outs"]>16

def test_team_state_direction():
    rows=[
        {"date":D-timedelta(days=2),"runs_for":8,"runs_against":2},
        {"date":D-timedelta(days=1),"runs_for":7,"runs_against":3},
    ]
    x=TeamStateCalculator(prior_games=1).calculate(rows,D)
    assert x["offense_score"]>0
    assert x["defense_score"]>0
    assert x["team_strength"]>0

def test_bullpen_direction():
    rows=[
        {"date":D-timedelta(days=3),"batters_faced":20,"runs_allowed":0},
        {"date":D-timedelta(days=1),"batters_faced":20,"runs_allowed":1},
    ]
    x=BullpenStateCalculator(prior_bf=20).calculate(rows,D)
    assert x["bullpen_score"]>0

def test_empty_history_neutral():
    assert StarterStateCalculator().calculate([],D)["talent_score"]==0
    assert TeamStateCalculator().calculate([],D)["team_strength"]==0
    assert BullpenStateCalculator().calculate([],D)["bullpen_score"]==0

def test_future_rows_do_not_leak():
    rows=[{"date":D+timedelta(days=1),"runs_for":20,"runs_against":0}]
    x=TeamStateCalculator().calculate(rows,D)
    assert x["games_prior"]==0 and x["team_strength"]==0
