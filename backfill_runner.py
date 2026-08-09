from historical_boxscore_store import HistoricalBoxscoreStore
from team_game_exact_adapter import team_game_rows_from_linescore
from coverage_gate import full_history_gate

class ExactBackfillRunner:
    def __init__(self,fetch_boxscore,fetch_game_summary):
        self.fetch_boxscore=fetch_boxscore
        self.fetch_game_summary=fetch_game_summary
        self.pitching_store=HistoricalBoxscoreStore()
        self.team_games=[]

    def ingest_game(self,game_pk,game_date):
        box=self.fetch_boxscore(game_pk)
        payload=box["payload"] if isinstance(box,dict) and "payload" in box else box
        self.pitching_store.ingest(game_pk,game_date,payload)

        summary=self.fetch_game_summary(game_pk)
        sp=summary["payload"] if isinstance(summary,dict) and "payload" in summary else summary
        self.team_games.extend(team_game_rows_from_linescore(sp,game_date))

    def readiness(self,target_date,away_team,home_team,away_starter_id,home_starter_id,
                  min_starts=5,min_relief_rows=15,min_team_games=10):
        return full_history_gate(
            self.pitching_store.pitching_rows,self.team_games,target_date,
            away_team,home_team,away_starter_id,home_starter_id,
            min_starts,min_relief_rows,min_team_games
        )
