import json
from mlb_bulk_schedule_runtime import completed_games
from venue_timezone_registry_builder import build_registry, write_registry

def main(start_date="2025-03-27", end_date="2025-09-28"):
    games = completed_games(start_date, end_date)
    registry = build_registry(games)
    write_registry(registry)

    print(json.dumps({
        "venues_found": len(registry["rows"]),
        "errors": registry["errors"],
        "complete": registry["complete"],
    }, indent=2))

    if not registry["complete"]:
        raise SystemExit(2)
    return registry

if __name__ == "__main__":
    main()
