import json
from urllib.request import Request, urlopen

BASE = "https://statsapi.mlb.com/api/v1"

def fetch_json(url, timeout=30):
    req = Request(url, headers={
        "User-Agent": "mlb-baseball-engine/1.0",
        "Accept": "application/json",
    })
    with urlopen(req, timeout=timeout) as r:
        return json.loads(r.read().decode("utf-8"))

def venue_url(venue_id):
    # Location hydration is required because the plain venue response
    # does not reliably expose timezone metadata.
    return f"{BASE}/venues/{venue_id}?hydrate=location"

def fetch_venue(venue_id, fetcher=fetch_json):
    payload = fetcher(venue_url(venue_id))
    venues = payload.get("venues") or []
    if not venues:
        raise ValueError(f"MLB returned no venue for {venue_id}")
    return venues[0]

def venue_coordinates(venue, venue_id=None):
    loc = venue.get("location") or {}
    coords = (
        loc.get("defaultCoordinates")
        or venue.get("defaultCoordinates")
        or {}
    )
    lat = coords.get("latitude")
    lon = coords.get("longitude")
    if lat is None or lon is None:
        raise ValueError(
            f"venue {venue_id or venue.get('id')} missing MLB coordinates"
        )
    return float(lat), float(lon)
