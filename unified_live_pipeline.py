from current_game_ingestor import CurrentGameIngestor
from assembler_pipeline import AssemblerPipeline
from operational_pipeline import OperationalPipeline

class UnifiedLivePipeline:
    def __init__(self,repo_root="."):
        self.ingestor=CurrentGameIngestor()
        self.assembler=AssemblerPipeline()
        self.ops=OperationalPipeline(repo_root)

    def build_matchup(self,schedule_row,lineup_confirmed,lineup_source,
                      weather_score,weather_source,roster_clear,roster_source,
                      park_score=0.0,now_utc=None,bullpen_current=True,
                      home_field_score=.10,travel_rest_score=0.0,
                      platoon_score=0.0,umpire_known=False):
        rec=self.ingestor.build_record(
            schedule_row,lineup_confirmed,lineup_source,
            weather_score,weather_source,roster_clear,roster_source,
            park_score,now_utc,bullpen_current,home_field_score,
            travel_rest_score,platoon_score,umpire_known
        )
        return rec,self.ingestor.to_matchup_definition(rec)

    def build_model_inputs(self,matchup,pitching_df,games_df):
        return self.assembler.build_inputs(matchup,pitching_df,games_df)

    def analyze_with_prices(self,model_inputs,price_input):
        # This is the first point where sportsbook prices enter.
        return self.ops.analyze(model_inputs,price_input)

    def full_run(self,schedule_row,lineup_confirmed,lineup_source,
                 weather_score,weather_source,roster_clear,roster_source,
                 pitching_df,games_df,price_input,park_score=0.0,now_utc=None,
                 bullpen_current=True,home_field_score=.10,
                 travel_rest_score=0.0,platoon_score=0.0,umpire_known=False):
        current_record,matchup=self.build_matchup(
            schedule_row,lineup_confirmed,lineup_source,
            weather_score,weather_source,roster_clear,roster_source,
            park_score,now_utc,bullpen_current,home_field_score,
            travel_rest_score,platoon_score,umpire_known
        )
        facts,inputs=self.build_model_inputs(matchup,pitching_df,games_df)
        analysis,prod,shadow=self.analyze_with_prices(inputs,price_input)
        return {
            "current_game_record":current_record,
            "matchup":matchup,
            "pregame_facts":facts,
            "model_inputs":inputs,
            "analysis":analysis,
            "production_prediction":prod,
            "shadow_prediction":shadow,
        }
