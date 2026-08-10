import json
from urllib.request import Request, urlopen

BASE = "https://statsapi.mlb.com/api/v1.1"

def fetch_json(url, timeout=30):
    req = Request(url, headers={
        "User-Agent": "mlb-baseball-engine/1.0",
        "Accept": "application/json",
    })
    with urlopen(req, timeout=timeout) as r:
        return json.loads(r.read().decode("utf-8"))

def live_feed_url(game_pk):
    return f"{BASE}/game/{game_pk}/feed/live"

def _team_lineup(team_box):
    order = team_box.get("battingOrder") or []
    return [str(x) for x in order if x is not None]

def _starter_id(team_box):
    for key, p in (team_box.get("players") or {}).items():
        stats = ((p.get("stats") or {}).get("pitching") or {})
        if int(stats.get("gamesStarted", 0) or 0) == 1:
            return str((p.get("person") or {}).get("id") or str(key).replace("ID", "", 1))
    pitchers = team_box.get("pitchers") or []
    return str(pitchers[0]) if pitchers else None

def extract_pregame_evidence(payload, game_pk=None):
    gd = payload.get("gameData", {})
    ld = payload.get("liveData", {})
    box = (ld.get("boxscore") or {}).get("teams", {})
    away_box = box.get("away", {})
    home_box = box.get("home", {})

    away_lineup = _team_lineup(away_box)
    home_lineup = _team_lineup(home_box)
    venue = (gd.get("venue") or {}).get("name")
    weather = gd.get("weather") or {}
    teams = gd.get("teams") or {}

    return {
        "game_pk": str(game_pk) if game_pk is not None else None,
        "away_team": (teams.get("away") or {}).get("abbreviation"),
        "home_team": (teams.get("home") or {}).get("abbreviation"),
        "away_starter_id": _starter_id(away_box),
        "home_starter_id": _starter_id(home_box),
        "away_lineup": away_lineup,
        "home_lineup": home_lineup,
        "lineup_confirmed": len(away_lineup) >= 9 and len(home_lineup) >= 9,
        "venue_name": venue,
        "weather_raw": {
            "condition": weather.get("condition"),
            "temp_f": weather.get("temp"),
            "wind": weather.get("wind"),
        },
        "provenance": {
            "starters": "MLB-live-feed",
            "lineups": "MLB-live-feed-boxscore-battingOrder",
            "venue": "MLB-live-feed-gameData",
            "weather_raw": "MLB-live-feed-gameData",
        },
    }

def fetch_pregame_evidence(game_pk, fetcher=fetch_json):
    return extract_pregame_evidence(fetcher(live_feed_url(game_pk)), game_pk)
