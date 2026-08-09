from historical_boxscore_store import HistoricalBoxscoreStore
from team_game_exact_adapter_v2 import team_game_rows_from_game
from coverage_gate import full_history_gate

class ExactBackfillExecutor:
    def __init__(self,boxscore_fetcher,summary_fetcher):
        self.boxscore_fetcher=boxscore_fetcher; self.summary_fetcher=summary_fetcher
        self.pitching_store=HistoricalBoxscoreStore(); self.team_games=[]; self.canonical_team_games=[]; self.processed=set()
    def ingest_game(self,game_pk,game_date):
        key=str(game_pk)
        if key in self.processed: return
        box=self.boxscore_fetcher(game_pk); payload=box["payload"] if isinstance(box,dict) and "payload" in box else box
        self.pitching_store.ingest(game_pk,game_date,payload)
        summary=self.summary_fetcher(game_pk); sp=summary["payload"] if isinstance(summary,dict) and "payload" in summary else summary
        canonical,perspectives=team_game_rows_from_game(sp,game_date)
        self.canonical_team_games.append(canonical); self.team_games.extend(perspectives); self.processed.add(key)
    def ingest_many(self,refs):
        for g in sorted(refs,key=lambda x:x["game_date"]): self.ingest_game(g["game_pk"],g["game_date"])
    def readiness(self,target_date,away_team,home_team,away_starter_id,home_starter_id,min_starts=5,min_relief_rows=15,min_team_games=10):
        return full_history_gate(self.pitching_store.pitching_rows,self.team_games,target_date,away_team,home_team,away_starter_id,home_starter_id,min_starts,min_relief_rows,min_team_games)
    def export_bundle(self):
        return {"pitching_rows":self.pitching_store.pitching_rows,"team_games":self.team_games,"canonical_team_games":self.canonical_team_games,"processed_game_pks":sorted(self.processed)}
