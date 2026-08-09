import json
from pathlib import Path
from mlb_schedule_runtime import completed_games_for_team
from exact_history_runtime import fetch_boxscore
from game_summary_runtime import fetch_linescore_summary
from exact_backfill_executor import ExactBackfillExecutor
from nym_pit_backfill_plan import *

def run(output_path="nym_pit_exact_history_bundle.json"):
    nym=completed_games_for_team(NYM_TEAM_ID,BACKFILL_START_DATE,BACKFILL_END_DATE)
    pit=completed_games_for_team(PIT_TEAM_ID,BACKFILL_START_DATE,BACKFILL_END_DATE)
    refs=dedupe_game_refs(nym,pit)

    exe=ExactBackfillExecutor(fetch_boxscore,fetch_linescore_summary)
    exe.ingest_many(refs)
    ready=exe.readiness(
        TARGET_DATE,AWAY_TEAM,HOME_TEAM,AWAY_STARTER_ID,HOME_STARTER_ID
    )
    bundle=exe.export_bundle()
    bundle["readiness"]=ready
    Path(output_path).write_text(json.dumps(bundle,indent=2))
    if not ready["ready"]:
        raise RuntimeError(f"Exact history coverage incomplete: {ready}")
    return bundle

if __name__=="__main__":
    x=run()
    print(json.dumps(x["readiness"],indent=2))
