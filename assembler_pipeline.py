from game_state_assembler import RealGameStateAssembler
from pregame_feature_builder import PregameFeatureBuilder

class AssemblerPipeline:
    def __init__(self, assembler=None, feature_builder=None):
        self.assembler = assembler or RealGameStateAssembler()
        self.feature_builder = feature_builder or PregameFeatureBuilder()

    def build_inputs(self, matchup, pitching_df, games_df):
        facts = self.assembler.assemble(
            matchup.game_id, matchup.game_date, matchup.home_team, matchup.away_team,
            matchup.home_starter_id, matchup.away_starter_id, pitching_df, games_df,
            matchup.home_starter_confirmed, matchup.away_starter_confirmed,
            matchup.lineup_confirmed, matchup.bullpen_current, matchup.weather_current,
            matchup.roster_news_clear, matchup.home_field_score, matchup.park_score,
            matchup.weather_score, matchup.travel_rest_score, matchup.platoon_score,
            matchup.umpire_known
        )
        return facts, self.feature_builder.build(facts)
