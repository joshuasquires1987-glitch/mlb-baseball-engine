from dataclasses import dataclass
from typing import Optional

@dataclass(frozen=True)
class LiveProbable:
    game_key:str
    away_team:str
    home_team:str
    away_pitcher_name:Optional[str]
    home_pitcher_name:Optional[str]
    away_pitcher_id:Optional[str]=None
    home_pitcher_id:Optional[str]=None
    source_name:str="external"
    fetched_at_utc:str=""
    notes:str=""

    @property
    def both_named(self):
        return bool(self.away_pitcher_name and self.home_pitcher_name)

    @property
    def both_ids(self):
        return bool(self.away_pitcher_id and self.home_pitcher_id)

    @property
    def fully_resolved(self):
        return self.both_named and self.both_ids
