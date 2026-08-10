import json
from datetime import datetime, timezone
from pathlib import Path
from mlb_venue_runtime import fetch_venue, timezone_record_from_venue

def unique_venue_ids(games):
    vals = {
        str(g["venue_id"])
        for g in games
        if g.get("venue_id") is not None
    }
    return sorted(vals, key=lambda x: int(x) if x.isdigit() else x)

def build_registry(games, venue_fetcher=fetch_venue):
    rows = []
    errors = []
    for vid in unique_venue_ids(games):
        try:
            venue = venue_fetcher(vid)
            rows.append(timezone_record_from_venue(venue, vid))
        except Exception as e:
            errors.append({
                "venue_id": vid,
                "error": f"{type(e).__name__}: {e}",
            })

    return {
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "source": "MLB-StatsAPI-venue",
        "rows": rows,
        "errors": errors,
        "complete": len(errors) == 0,
    }

def write_registry(registry, path="venue_timezone_registry.json"):
    p = Path(path)
    p.write_text(json.dumps(registry, indent=2, sort_keys=True))
    return p
