import json
from pathlib import Path
from mlb_bulk_schedule_runtime import completed_games
from pregame_snapshot_registry import PregameSnapshotRegistry
from context_static_registries import FrozenRegistry
from park_factor_registry import PointInTimeParkRegistry
from bulk_context_dataset_runner import BulkContextDatasetRunner
from mlb_pregame_evidence import fetch_json,live_feed_url
from historical_weather_parser import parse_pregame_weather
from rc2_context_calibration import chronological_split,evaluate
from context_calibration_gate import calibration_gate
def weather_provider(pk):
 try: return parse_pregame_weather(fetch_json(live_feed_url(pk)).get("gameData",{}))
 except Exception: return None
games=completed_games("2025-03-27","2025-09-28")
runner=BulkContextDatasetRunner(weather_provider,PointInTimeParkRegistry.from_json("park_factor_registry.json"),FrozenRegistry.from_json("venue_timezone_registry.json",key="venue_id"),PregameSnapshotRegistry.from_jsonl("pregame_lineup_snapshots.jsonl"))
rows=runner.run(games)["rows"]; train,hold=chronological_split(rows)
intercept,c,ll,ll0,br,br0=evaluate(train,hold); delta=ll-ll0
gate=calibration_gate(len(train),len(hold),c,delta)
report={"version":"BT-0083","research_only":True,"training_games":len(train),"holdout_games":len(hold),"training_first_date":train[0]["game_date"],"training_last_date":train[-1]["game_date"],"holdout_first_date":hold[0]["game_date"],"holdout_last_date":hold[-1]["game_date"],"intercept":intercept,"coefficients":c,"holdout_log_loss":ll,"zero_context_holdout_log_loss":ll0,"holdout_logloss_delta":delta,"holdout_brier":br,"zero_context_holdout_brier":br0,"gate":gate}
Path("rc2_context_calibration_report.json").write_text(json.dumps(report,indent=2))
Path("context_coefficients_rc2_fitted.json").write_text(json.dumps({"version":"v1.2-RC2-context-research","controls_bets":False,"controls_stakes":False,"coefficients":c,"training_games":len(train),"holdout_games":len(hold),"holdout_logloss_delta":delta,"eligible_for_shadow_review":gate["eligible_for_shadow_review"],"production_promotion_allowed":False},indent=2))
print(json.dumps(report,indent=2))
