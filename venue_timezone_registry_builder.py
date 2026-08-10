import json
from datetime import datetime, timezone
from pathlib import Path
from mlb_venue_runtime import fetch_venue, venue_coordinates

def unique_venue_ids(games):
    vals = {
        str(g["venue_id"])
        for g in games
        if g.get("venue_id") is not None
    }
    return sorted(vals, key=lambda x: int(x) if x.isdigit() else x)

def build_registry(games, venue_fetcher=fetch_venue, timezone_lookup=None):
    if timezone_lookup is None:
        from timezonefinder import TimezoneFinder
        tf = TimezoneFinder()
        timezone_lookup = lambda lat, lon: tf.timezone_at(lat=lat, lng=lon)

    rows = []
    errors = []

    for vid in unique_venue_ids(games):
        try:
            venue = venue_fetcher(vid)
            lat, lon = venue_coordinates(venue, vid)
            timezone_id = timezone_lookup(lat, lon)
            if not timezone_id:
                raise ValueError(f"no IANA timezone found for venue {vid}")

            rows.append({
                "venue_id": vid,
                "venue_name": venue.get("name"),
                "latitude": lat,
                "longitude": lon,
                "timezone_id": timezone_id,
                "source_coordinates": "MLB-StatsAPI-venue-location",
                "source_timezone": "timezonefinder-coordinate-lookup",
            })
        except Exception as e:
            errors.append({
                "venue_id": vid,
                "error": f"{type(e).__name__}: {e}",
            })

    return {
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "rows": rows,
        "errors": errors,
        "complete": len(errors) == 0,
    }

def write_registry(registry, path="venue_timezone_registry.json"):
    p = Path(path)
    p.write_text(json.dumps(registry, indent=2, sort_keys=True))
    return p
