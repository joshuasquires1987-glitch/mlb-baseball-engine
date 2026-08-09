from dataclasses import dataclass
from typing import Optional

@dataclass(frozen=True)
class SourceStamp:
    source_name:str
    fetched_at_utc:str
    source_url:Optional[str]=None

@dataclass(frozen=True)
class StarterInfo:
    pitcher_id:str; pitcher_name:str; confirmed:bool; source:SourceStamp

@dataclass(frozen=True)
class LineupInfo:
    confirmed:bool; source:SourceStamp

@dataclass(frozen=True)
class WeatherInfo:
    current:bool; weather_score:float; source:SourceStamp

@dataclass(frozen=True)
class RosterNewsInfo:
    clear:bool; source:SourceStamp

@dataclass(frozen=True)
class ParkInfo:
    park_name:str; park_score:float

@dataclass(frozen=True)
class CurrentGameRecord:
    game_id:str; game_date:object; home_team:str; away_team:str
    home_starter:StarterInfo; away_starter:StarterInfo
    lineup:LineupInfo; weather:WeatherInfo; roster_news:RosterNewsInfo; park:ParkInfo
    bullpen_current:bool=True; home_field_score:float=.10; travel_rest_score:float=0.0
    platoon_score:float=0.0; umpire_known:bool=False
