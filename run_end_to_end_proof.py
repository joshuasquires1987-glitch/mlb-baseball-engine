from exact_bundle_frames import pitching_frame
from canonical_bundle_frames import canonical_games_frame
from bundle_probability_gate import assert_bundle_ready
from production_probability_bridge import ProductionProbabilityBridge
from assembler_pipeline import AssemblerPipeline
from proof_artifact import write_probability_proof

def run(bundle,matchup,output_path,repo_root="."):
    assert_bundle_ready(bundle)
    pitching_df=pitching_frame(bundle)
    games_df=canonical_games_frame(bundle)
    bridge=ProductionProbabilityBridge(AssemblerPipeline(),repo_root)
    result=bridge.run(bundle,matchup,pitching_df,games_df)
    proof=write_probability_proof(
        output_path,
        f"{matchup.away_team}@{matchup.home_team}",
        str(matchup.game_date),
        result,
        bundle["readiness"],
    )
    if proof["prices_seen"]:
        raise RuntimeError("Market leakage detected.")
    return proof
