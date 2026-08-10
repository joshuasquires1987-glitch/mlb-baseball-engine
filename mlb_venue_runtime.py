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
    return f"{BASE}/venues/{venue_id}"

def fetch_venue(venue_id, fetcher=fetch_json):
    payload = fetcher(venue_url(venue_id))
    venues = payload.get("venues") or []
    if not venues:
        raise ValueError(f"MLB returned no venue for {venue_id}")
    return venues[0]

def timezone_record_from_venue(venue, venue_id=None):
    tz = venue.get("timeZone") or venue.get("timezone") or {}
    offset = tz.get("offset")
    tz_id = tz.get("id")
    tz_abbr = tz.get("tz")

    if offset is None:
        raise ValueError(f"venue {venue_id or venue.get('id')} missing MLB timezone offset")

    return {
        "venue_id": str(venue_id or venue.get("id")),
        "venue_name": venue.get("name"),
        "timezone_id": tz_id,
        "timezone_abbreviation": tz_abbr,
        "utc_offset_hours": float(offset),
        "source": "MLB-StatsAPI-venue",
    }
