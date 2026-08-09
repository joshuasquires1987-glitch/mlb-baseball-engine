from dataclasses import dataclass
from typing import Optional

@dataclass(frozen=True)
class HistoryField:
    value:float
    provenance:str  # exact | derived | estimated
    source_name:str
    source_url:Optional[str]=None

    @property
    def production_exact(self):
        return self.provenance=="exact"

@dataclass(frozen=True)
class PitchingHistoryRow:
    date:str
    innings_outs:HistoryField
    runs_allowed:HistoryField
    batters_faced:HistoryField

    @property
    def production_ready(self):
        return (
            self.innings_outs.production_exact
            and self.runs_allowed.production_exact
            and self.batters_faced.production_exact
        )
