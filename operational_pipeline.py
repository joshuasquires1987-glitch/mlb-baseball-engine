from live_workflow import LiveWorkflow
from prediction_store import PredictionStore
from wager_ledger import WagerLedger
from settlement import settle_wager
from shadow_evaluation import evaluate_predictions
from validation_tracker import ValidationTracker
from promotion_gate import review_status

class OperationalPipeline:
    def __init__(self,repo_root=".",starting_bankroll_cad=1000):
        self.live=LiveWorkflow(repo_root)
        self.predictions=PredictionStore()
        self.wagers=WagerLedger(starting_bankroll_cad)
        self.validation=ValidationTracker()

    def analyze(self,game,price):
        record=self.live.analyze_game(game,price)
        prod=self.predictions.freeze(record,"production")
        shadow=self.predictions.freeze(record,"shadow")
        return record,prod,shadow

    def confirm_wager(self,prod_prediction,side,odds,stake,explicit_confirmation):
        return self.wagers.confirm(prod_prediction,side,odds,stake,explicit_confirmation)

    def settle(self,wager,result,promotion_early_payout=False):
        s=settle_wager(wager,result,promotion_early_payout)
        self.wagers.settlements[wager.wager_id]=s
        return s

    def validate_pair(self,prod,shadow,home_won,prod_odds=None,shadow_odds=None,
                      home_away="home",starter_context="unknown",clv=None,stake=None,pnl=None):
        self.validation.add_game(prod.game_id,prod.model_version,prod.home_win_probability,int(home_won),
                                 prod_odds,"home",home_away,prod.confidence,starter_context,clv,stake,pnl)
        self.validation.add_game(shadow.game_id,shadow.model_version,shadow.home_win_probability,int(home_won),
                                 shadow_odds,"home",home_away,shadow.confidence,starter_context,None,None,None)

    def rc1_gate(self,integrity_failures=0,calibration_ok=True,catastrophic=False,human_approval=False):
        p=self.validation.summary("v1.1")
        s=self.validation.summary("v1.2-RC1")
        if not p.get("n") or not s.get("n"):
            return {"status":"SHADOW_CONTINUES","review_eligible":False,"promoted":False,"automatic_promotion":False}
        return review_status(s["n"],integrity_failures,s["brier"],p["brier"],calibration_ok,
                             catastrophic,human_approval)
