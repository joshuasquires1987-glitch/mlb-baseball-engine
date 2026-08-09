from dataclasses import asdict
from datetime import datetime,timezone
from dual_model_runner import DualModelRunner
from price_snapshots import DailyPriceStore

class LiveWorkflow:
    def __init__(self,repo_root="."):
        self.runner=DualModelRunner(repo_root); self.prices=DailyPriceStore()
    def analyze_game(self,game,price):
        if price is None: raise ValueError("Bet365 price required; predictions without odds are incomplete.")
        self.prices.add(game.game_id,price)
        prod,shadow=self.runner.predict(game)
        decision,shadow_view=self.runner.evaluate_prices(prod,shadow,price)
        return {"timestamp_utc":datetime.now(timezone.utc).isoformat(),"game_id":game.game_id,
                "game_date":game.game_date,"home_team":game.home_team,"away_team":game.away_team,
                "production":{"version":prod.model_version,"home_prob":prod.home_win_probability,
                              "away_prob":prod.away_win_probability,"confidence":prod.confidence,
                              "decision":asdict(decision)},
                "shadow":shadow_view,"integrity":asdict(game.integrity),"price":asdict(price)}

def information_status(integrity):
    return {c:[k for k,v in integrity.__dict__.items() if v==c] for c in ("green","yellow","red")}
