from dataclasses import dataclass
from typing import Optional

@dataclass(frozen=True)
class StarterState:
    pitcher_id:str
    talent_score:float
    expected_outs:float
    confirmed:bool

@dataclass(frozen=True)
class TeamState:
    team_strength:float
    offense_score:float
    defense_score:float
    bullpen_score:float

@dataclass(frozen=True)
class ContextState:
    home_field_score:float
    park_score:float
    weather_score:float=0.0
    travel_rest_score:float=0.0
    platoon_score:float=0.0

@dataclass(frozen=True)
class PregameFacts:
    game_id:str
    game_date:str
    home_team:str
    away_team:str
    home_starter:StarterState
    away_starter:StarterState
    home_team_state:TeamState
    away_team_state:TeamState
    context:ContextState
    lineup_confirmed:bool
    bullpen_current:bool
    weather_current:bool
    roster_news_clear:bool
    umpire_known:bool=False
