from dataclasses import dataclass

@dataclass(frozen=True)
class MatchupDefinition:
    game_id: str
    game_date: object
    home_team: str
    away_team: str
    home_starter_id: str
    away_starter_id: str
    home_starter_confirmed: bool
    away_starter_confirmed: bool
    lineup_confirmed: bool = False
    bullpen_current: bool = True
    weather_current: bool = True
    roster_news_clear: bool = True
    home_field_score: float = 0.10
    park_score: float = 0.0
    weather_score: float = 0.0
    travel_rest_score: float = 0.0
    platoon_score: float = 0.0
    umpire_known: bool = False
