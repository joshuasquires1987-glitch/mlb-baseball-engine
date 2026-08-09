from dataclasses import dataclass
from typing import Optional

@dataclass(frozen=True)
class FrozenPredictionRecord:
    prediction_id:str
    timestamp_utc:str
    game_id:str
    game_date:str
    home_team:str
    away_team:str
    model_version:str
    home_win_probability:float
    away_win_probability:float
    confidence:float
    starter_light:str
    lineup_light:str
    bullpen_light:str
    weather_light:str
    roster_news_light:str
    umpire_light:str
    frozen:bool=True

@dataclass(frozen=True)
class ConfirmedWager:
    wager_id:str
    prediction_id:str
    confirmed_timestamp_utc:str
    game_id:str
    selected_side:str
    decimal_odds:float
    stake_cad:float
    model_version:str
    original_model_probability:float
    sportsbook:str="Bet365"
    status:str="open"

@dataclass(frozen=True)
class Settlement:
    wager_id:str
    result:str
    profit_loss_cad:float
    ending_status:str
    promotion_note:Optional[str]=None
