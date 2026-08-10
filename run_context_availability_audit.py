import json
from pathlib import Path
from mlb_bulk_schedule_runtime import completed_games
from pregame_snapshot_registry import PregameSnapshotRegistry
from context_static_registries import FrozenRegistry
from bulk_context_dataset_runner import BulkContextDatasetRunner
from mlb_pregame_evidence import fetch_json,live_feed_url
from historical_weather_parser import parse_pregame_weather

def weather_provider(game_pk):
    try:
        payload=fetch_json(live_feed_url(game_pk))
        return parse_pregame_weather(payload.get("gameData",{}))
    except Exception:
        return None

def main(start_date="2025-03-27",end_date="2025-09-28"):
    games=completed_games(start_date,end_date)
    parks=FrozenRegistry.from_json("park_factor_registry.json",key="venue_id")
    venues=FrozenRegistry.from_json("venue_timezone_registry.json",key="venue_id")
    snaps=PregameSnapshotRegistry.from_jsonl("pregame_lineup_snapshots.jsonl")
    runner=BulkContextDatasetRunner(weather_provider,parks,venues,snaps)
    result=runner.run(games)

    Path("context_availability_report.json").write_text(json.dumps({
        "availability":result["availability"],
        "manifest":result["manifest"],
    },indent=2))
    Path("context_availability_audit.json").write_text(json.dumps(result["audit"],indent=2))
    print(json.dumps(result["availability"],indent=2))
    return result

if __name__=="__main__":
    main()
