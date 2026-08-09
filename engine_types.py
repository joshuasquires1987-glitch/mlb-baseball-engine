from dataclasses import dataclass
from typing import Dict, Optional
VALID_LIGHTS={"green","yellow","red"}

@dataclass(frozen=True)
class IntegrityState:
    starter:str; lineup:str; bullpen:str; weather:str; roster_news:str; umpire:str="yellow"
    def __post_init__(self):
        for name,value in self.__dict__.items():
            if value.lower() not in VALID_LIGHTS:
                raise ValueError(f"{name} must be green/yellow/red")
    def unresolved_red(self):
        return any(getattr(self,k).lower()=="red" for k in ("starter","lineup","bullpen","weather","roster_news"))

@dataclass(frozen=True)
class BaseballInputs:
    game_id:str; game_date:str; home_team:str; away_team:str; features:Dict[str,float]; integrity:IntegrityState

@dataclass(frozen=True)
class ModelPrediction:
    game_id:str; model_version:str; home_win_probability:float; away_win_probability:float
    confidence:Optional[float]; integrity:IntegrityState; frozen:bool=True

@dataclass(frozen=True)
class PriceInput:
    home_decimal:float; away_decimal:float; snapshot_label:str; source:str="Bet365 user screenshot"

@dataclass(frozen=True)
class ExecutionDecision:
    production_model_version:str; selected_side:Optional[str]; edge_pp:float
    eligible:bool; half_kelly_fraction:float; note:str=""
