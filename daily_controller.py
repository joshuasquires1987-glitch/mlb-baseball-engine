from daily_session import DailySession

class DailyController:
    def __init__(self,game_date):
        self.session=DailySession(game_date)

    def ingest_slate(self,games_with_prices):
        # Predictions without odds are incomplete; slate is defined by supplied Bet365 games only.
        for game_id in games_with_prices:
            self.session.register_game(game_id)

    def prediction_recorded(self,game_id,prediction_id,starter_fingerprint):
        return self.session.record_prediction(game_id,prediction_id,starter_fingerprint)

    def starter_change_requires_rerun(self,game_id,new_starter_fingerprint):
        return self.session.require_full_rerun(game_id,new_starter_fingerprint)

    def daily_status(self):
        return {
            "game_date":self.session.game_date,
            "games_total":len(self.session.games),
            "predicted":sum(g.status=="predicted" for g in self.session.games.values()),
            "reruns":sum(g.rerun_count for g in self.session.games.values()),
            "closed":self.session.closed,
        }
