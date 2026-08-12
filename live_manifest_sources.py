import json
from datetime import datetime, timedelta, timezone
from urllib.parse import urlencode
from urllib.request import Request, urlopen

from mlb_bulk_schedule_runtime import BASE as MLB_BASE, fetch_json


def game_feed_url(game_pk):
    return f"https://statsapi.mlb.com/api/v1.1/game/{game_pk}/feed/live"


def venue_url(venue_id, hydrate=False):
    url = f"{MLB_BASE}/venues/{venue_id}"
    if hydrate:
        url += "?" + urlencode({"hydrate": "location"})
    return url


def roster_url(team_id, game_date, roster_type="active"):
    q = urlencode({"rosterType": roster_type, "date": str(game_date)})
    return f"{MLB_BASE}/teams/{team_id}/roster?{q}"


def transactions_url(team_id, start_date, end_date):
    q = urlencode({
        "teamId": str(team_id),
        "startDate": str(start_date),
        "endDate": str(end_date),
    })
    return f"{MLB_BASE}/transactions?{q}"


def open_meteo_url(latitude, longitude, game_date):
    hourly = ",".join([
        "temperature_2m",
        "relative_humidity_2m",
        "precipitation_probability",
        "precipitation",
        "surface_pressure",
        "wind_speed_10m",
        "wind_direction_10m",
    ])
    q = urlencode({
        "latitude": latitude,
        "longitude": longitude,
        "hourly": hourly,
        "timezone": "UTC",
        "start_date": str(game_date),
        "end_date": str(game_date),
    })
    return f"https://api.open-meteo.com/v1/forecast?{q}"


def fetch_external_json(url, timeout=30):
    req = Request(
        url,
        headers={
            "User-Agent": "mlb-baseball-engine/1.0",
            "Accept": "application/json",
        },
    )
    with urlopen(req, timeout=timeout) as response:
        return json.loads(response.read().decode("utf-8"))


def fetched_at_utc():
    return datetime.now(timezone.utc).isoformat()


def _coordinates_from_location(location):
    location = location or {}
    candidates = [
        location.get("defaultCoordinates") or {},
        location.get("coordinates") or {},
        location,
    ]
    for obj in candidates:
        lat = obj.get("latitude")
        lon = obj.get("longitude")
        if lon is None:
            lon = obj.get("longitude")
        if lat is not None and lon is not None:
            return float(lat), float(lon)
    return None


def venue_coordinates(payload):
    venues = payload.get("venues") or []
    if not venues:
        return None
    venue = venues[0] or {}
    return _coordinates_from_location(venue.get("location"))


def feed_venue_coordinates(feed):
    venue = ((feed.get("gameData") or {}).get("venue") or {})
    return _coordinates_from_location(venue.get("location"))


def lineup_from_feed(feed):
    teams = (((feed.get("liveData") or {}).get("boxscore") or {}).get("teams") or {})
    result = {}
    for side in ("home", "away"):
        team = teams.get(side) or {}
        order = [str(x) for x in (team.get("battingOrder") or [])]
        result[side] = order
    return result


def probable_starters_from_feed(feed):
    probable = ((feed.get("gameData") or {}).get("probablePitchers") or {})
    result = {}
    for side in ("home", "away"):
        obj = probable.get(side) or {}
        result[side] = {
            "id": str(obj["id"]) if obj.get("id") is not None else None,
            "name": obj.get("fullName"),
        }
    return result


def active_roster_ids(payload):
    ids = []
    for row in payload.get("roster") or []:
        person = row.get("person") or {}
        if person.get("id") is not None:
            ids.append(str(person["id"]))
    return sorted(set(ids))


def transaction_count(payload):
    return len(payload.get("transactions") or [])


def closest_hourly_weather(payload, game_time_utc):
    hourly = payload.get("hourly") or {}
    times = hourly.get("time") or []
    if not times:
        return None

    target = datetime.fromisoformat(str(game_time_utc).replace("Z", "+00:00"))
    candidates = []
    for i, value in enumerate(times):
        dt = datetime.fromisoformat(str(value))
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        candidates.append((abs((dt - target).total_seconds()), i, dt))
    _, idx, dt = min(candidates)

    def value(name):
        xs = hourly.get(name) or []
        return xs[idx] if idx < len(xs) else None

    return {
        "forecast_hour_utc": dt.isoformat(),
        "temperature_2m_c": value("temperature_2m"),
        "relative_humidity_2m_pct": value("relative_humidity_2m"),
        "precipitation_probability_pct": value("precipitation_probability"),
        "precipitation_mm": value("precipitation"),
        "surface_pressure_hpa": value("surface_pressure"),
        "wind_speed_10m_kmh": value("wind_speed_10m"),
        "wind_direction_10m_deg": value("wind_direction_10m"),
    }


def recent_window(game_date, days=7):
    d = datetime.fromisoformat(str(game_date)).date()
    return (d - timedelta(days=days)).isoformat(), d.isoformat()
