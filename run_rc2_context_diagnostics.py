import json
from pathlib import Path
from mlb_bulk_schedule_runtime import completed_games
from pregame_snapshot_registry import PregameSnapshotRegistry
from context_static_registries import FrozenRegistry
from park_factor_registry import PointInTimeParkRegistry
from bulk_context_dataset_runner import BulkContextDatasetRunner
from mlb_pregame_evidence import fetch_json,live_feed_url
from historical_weather_parser import parse_pregame_weather
from rc2_context_diagnostics import diagnostics
def weather_provider(pk):
 try:return parse_pregame_weather(fetch_json(live_feed_url(pk)).get("gameData",{}))
 except Exception:return None
games=completed_games("2025-03-27","2025-09-28")
rows=BulkContextDatasetRunner(weather_provider,PointInTimeParkRegistry.from_json("park_factor_registry.json"),FrozenRegistry.from_json("venue_timezone_registry.json",key="venue_id"),PregameSnapshotRegistry.from_jsonl("pregame_lineup_snapshots.jsonl")).run(games)["rows"]
results=diagnostics(rows)
report={"version":"BT-0084","research_only":True,"games":len(rows),"method":"4 expanding chronological folds; group ablations","results":results}
Path("rc2_context_diagnostics_report.json").write_text(json.dumps(report,indent=2))
print(json.dumps(report,indent=2))
