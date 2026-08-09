import sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]; sys.path.insert(0,str(ROOT/'src'))
from baseball_engine.types import BaseballInputs,IntegrityState,PriceInput
from baseball_engine.runner import DualModelRunner
def test_shadow_never_controls_bet():
    r=DualModelRunner(ROOT/'config'); i=BaseballInputs('X','H','A',{'starting_pitcher':.2,'underlying_team_strength':.1,'bullpen':.1,'confirmed_lineup_offense':.1,'home_field':.1,'starting_pitcher_talent_state':.2,'bullpen_talent_state':.1,'expected_starter_depth':.1,'bullpen_exposure_quality':.1},IntegrityState('green','green','green','green','green')); p,s=r.predict(i); d,v=r.evaluate_prices(p,s,PriceInput(1.95,1.95)); assert d.production_model_version=='v1.1' and not v['controls_bets'] and not v['controls_stakes']
def test_red_integrity_blocks_production():
    r=DualModelRunner(ROOT/'config'); i=BaseballInputs('Y','H','A',{'starting_pitcher':3},IntegrityState('red','green','green','green','green')); p,s=r.predict(i); d,_=r.evaluate_prices(p,s,PriceInput(2.2,1.7)); assert not d.eligible
