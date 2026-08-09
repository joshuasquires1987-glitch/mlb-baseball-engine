from dataclasses import dataclass
from typing import Dict, Optional
@dataclass(frozen=True)
class IntegrityState:
    starter:str; lineup:str; bullpen:str; weather:str; roster_news:str
    def unresolved_red(self): return any(v.lower()=='red' for v in (self.starter,self.lineup,self.bullpen,self.weather,self.roster_news))
@dataclass(frozen=True)
class BaseballInputs:
    game_id:str; home_team:str; away_team:str; features:Dict[str,float]; integrity:IntegrityState
@dataclass(frozen=True)
class ModelPrediction:
    game_id:str; model_version:str; home_win_probability:float; away_win_probability:float; confidence:Optional[float]; integrity:IntegrityState; frozen:bool=True
@dataclass(frozen=True)
class PriceInput:
    home_decimal:float; away_decimal:float; source:str='Bet365 user screenshot'
@dataclass(frozen=True)
class ExecutionDecision:
    production_model_version:str; selected_side:Optional[str]; edge_pp:float; eligible:bool; half_kelly_fraction:float; note:str=''
