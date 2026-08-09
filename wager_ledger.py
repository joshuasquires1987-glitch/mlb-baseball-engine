from uuid import uuid4
from datetime import datetime,timezone
from records import ConfirmedWager

class WagerLedger:
    def __init__(self,starting_bankroll_cad=1000.0):
        self.starting_bankroll=float(starting_bankroll_cad)
        self.wagers={}
        self.settlements={}
    def confirm(self,prediction,selected_side,decimal_odds,stake_cad,explicit_confirmation):
        if explicit_confirmation is not True:
            raise PermissionError("Wager may only be recorded after explicit user confirmation.")
        if prediction.model_version!="v1.1":
            raise ValueError("Shadow/challenger predictions cannot create confirmed wagers.")
        side=selected_side.lower()
        if side not in ("home","away"):
            raise ValueError("selected_side must be home or away")
        prob=prediction.home_win_probability if side=="home" else prediction.away_win_probability
        wager=ConfirmedWager(
            wager_id=str(uuid4()),prediction_id=prediction.prediction_id,
            confirmed_timestamp_utc=datetime.now(timezone.utc).isoformat(),
            game_id=prediction.game_id,selected_side=side,decimal_odds=float(decimal_odds),
            stake_cad=float(stake_cad),model_version=prediction.model_version,
            original_model_probability=float(prob),status="open"
        )
        self.wagers[wager.wager_id]=wager
        return wager
    def bankroll(self):
        return self.starting_bankroll + sum(s.profit_loss_cad for s in self.settlements.values())
