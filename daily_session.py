from dataclasses import dataclass, field
from datetime import datetime,timezone

@dataclass
class DailyGameState:
    game_id:str
    first_prediction_id:str|None=None
    latest_prediction_id:str|None=None
    starter_fingerprint:str|None=None
    rerun_count:int=0
    status:str="pending"

@dataclass
class DailySession:
    game_date:str
    games:dict=field(default_factory=dict)
    closed:bool=False

    def register_game(self,game_id):
        if self.closed: raise RuntimeError("Session closed")
        self.games.setdefault(game_id,DailyGameState(game_id))
        return self.games[game_id]

    def record_prediction(self,game_id,prediction_id,starter_fingerprint):
        s=self.register_game(game_id)
        if s.first_prediction_id is None:
            s.first_prediction_id=prediction_id
        s.latest_prediction_id=prediction_id
        if s.starter_fingerprint is not None and s.starter_fingerprint!=starter_fingerprint:
            s.rerun_count+=1
        s.starter_fingerprint=starter_fingerprint
        s.status="predicted"
        return s

    def require_full_rerun(self,game_id,new_starter_fingerprint):
        s=self.register_game(game_id)
        return s.starter_fingerprint is not None and s.starter_fingerprint!=new_starter_fingerprint

    def close(self):
        self.closed=True
