import json
from pathlib import Path
from .models import run_weighted_model
from .execution import production_decision
class DualModelRunner:
    def __init__(self,config_dir):
        c=Path(config_dir); self.v11=json.loads((c/'v1_1.json').read_text()); self.rc1=json.loads((c/'v1_2_rc1.json').read_text())
    def predict(self,inputs):
        return run_weighted_model(inputs,self.v11['model_version'],self.v11['weights']), run_weighted_model(inputs,self.rc1['model_version'],self.rc1['weights'])
    def evaluate_prices(self,prod,shadow,prices):
        decision=production_decision(prod,prices,float(self.v11['min_edge_pp']))
        return decision,{'model_version':shadow.model_version,'home_win_probability':shadow.home_win_probability,'away_win_probability':shadow.away_win_probability,'controls_bets':False,'controls_stakes':False}
