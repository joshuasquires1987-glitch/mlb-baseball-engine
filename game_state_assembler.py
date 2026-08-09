from pregame_inputs import PregameFacts, ContextState
from starter_state_calculator import StarterStateCalculator
from team_state_calculator import TeamStateCalculator
from bullpen_state_calculator import BullpenStateCalculator
from state_bundle import build_starter_state, build_team_state
from retrosheet_adapters import starter_rows_from_pitching, bullpen_rows_from_pitching, team_rows_from_games

class RealGameStateAssembler:
    def __init__(self, starter_calc=None, team_calc=None, bullpen_calc=None):
        self.starter_calc = starter_calc or StarterStateCalculator()
        self.team_calc = team_calc or TeamStateCalculator()
        self.bullpen_calc = bullpen_calc or BullpenStateCalculator()

    def assemble(
        self, game_id, game_date, home_team, away_team,
        home_starter_id, away_starter_id, pitching_df, games_df,
        home_starter_confirmed, away_starter_confirmed,
        lineup_confirmed, bullpen_current, weather_current, roster_news_clear,
        home_field_score=0.10, park_score=0.0, weather_score=0.0,
        travel_rest_score=0.0, platoon_score=0.0, umpire_known=False
    ):
        home_sp = build_starter_state(
            self.starter_calc,
            starter_rows_from_pitching(pitching_df, home_starter_id),
            game_date, home_starter_id, home_starter_confirmed
        )
        away_sp = build_starter_state(
            self.starter_calc,
            starter_rows_from_pitching(pitching_df, away_starter_id),
            game_date, away_starter_id, away_starter_confirmed
        )
        home_state = build_team_state(
            self.team_calc, self.bullpen_calc,
            team_rows_from_games(games_df, home_team),
            bullpen_rows_from_pitching(pitching_df, home_team),
            game_date
        )
        away_state = build_team_state(
            self.team_calc, self.bullpen_calc,
            team_rows_from_games(games_df, away_team),
            bullpen_rows_from_pitching(pitching_df, away_team),
            game_date
        )

        return PregameFacts(
            game_id=game_id,
            game_date=str(game_date.date() if hasattr(game_date, "date") else game_date),
            home_team=home_team,
            away_team=away_team,
            home_starter=home_sp,
            away_starter=away_sp,
            home_team_state=home_state,
            away_team_state=away_state,
            context=ContextState(
                home_field_score=home_field_score,
                park_score=park_score,
                weather_score=weather_score,
                travel_rest_score=travel_rest_score,
                platoon_score=platoon_score,
            ),
            lineup_confirmed=lineup_confirmed,
            bullpen_current=bullpen_current,
            weather_current=weather_current,
            roster_news_clear=roster_news_clear,
            umpire_known=umpire_known,
        )
