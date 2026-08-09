from bundle_probability_gate import assert_bundle_ready,assert_probability_integrity
from probability_only_runner import ProbabilityOnlyRunner

class ProductionProbabilityBridge:
    def __init__(self,assembler_pipeline,repo_root="."):
        self.assembler=assembler_pipeline
        self.probability=ProbabilityOnlyRunner(repo_root)

    def run(self,bundle,matchup,pitching_df,games_df):
        assert_bundle_ready(bundle)
        facts,inputs=self.assembler.build_inputs(matchup,pitching_df,games_df)
        assert_probability_integrity(inputs)
        result=self.probability.predict(inputs)
        return {
            "pregame_facts":facts,
            "model_inputs":inputs,
            **result,
        }
