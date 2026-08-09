from dataclasses import dataclass, field

@dataclass(frozen=True)
class GameRef:
    game_pk:str
    game_date:str
    away_team:str
    home_team:str

@dataclass
class BackfillManifest:
    target_game_key:str
    target_date:str
    starter_ids:dict
    teams:tuple
    historical_games:list=field(default_factory=list)

    def add_game(self,game_pk,game_date,away_team,home_team):
        self.historical_games.append(GameRef(str(game_pk),str(game_date),away_team,home_team))

    def game_pks(self):
        return [g.game_pk for g in self.historical_games]
