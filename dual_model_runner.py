from pathlib import Path
import json
from model_core import weighted_probability
from execution_layer import production_decision

class DualModelRunner:
    def __init__(self,root="."):
        root=Path(root)
        self.v11=json.loads((root/"v1_1.json").read_text())
        self.rc1=json.loads((root/"v1_2_rc1.json").read_text())
        if self.v11["status"]!="production_frozen": raise RuntimeError("v1.1 must be frozen production")
        if not self.rc1["status_rules"]["shadow_only"]: raise RuntimeError("RC1 must remain shadow-only")
    def predict(self,inputs):
        p=weighted_probability(inputs,self.v11["model_version"],self.v11["weights"])
        s=weighted_probability(inputs,self.rc1["model_version"],self.rc1["weights"])
        return p,s
    def evaluate_prices(self,prod,shadow,prices):
        decision=production_decision(prod,prices,float(self.v11["min_edge_pp"]))
        return decision,{"model_version":shadow.model_version,"home_win_probability":shadow.home_win_probability,
                         "away_win_probability":shadow.away_win_probability,"confidence":shadow.confidence,
                         "controls_bets":False,"controls_stakes":False}
