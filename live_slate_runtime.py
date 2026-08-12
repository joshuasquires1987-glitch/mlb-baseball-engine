from urllib.parse import urlencode

from mlb_bulk_schedule_runtime import BASE, fetch_json


def live_schedule_url(game_date):
    q = urlencode({
        "sportId": 1,
        "date": str(game_date),
        "hydrate": "probablePitcher,team,venue",
    })
    return f"{BASE}/schedule?{q}"


def _person_id(obj):
    if not obj:
        return None
    value = obj.get("id")
    return str(value) if value is not None else None


def _extract_live_slate(payload):
    rows = []
    for block in payload.get("dates", []):
        for game in block.get("games", []):
            teams = game.get("teams") or {}
            home = teams.get("home") or {}
            away = teams.get("away") or {}
            status = game.get("status") or {}
            venue = game.get("venue") or {}

            rows.append({
                "game_pk": str(game["gamePk"]),
                "game_date": block.get("date"),
                "game_time_utc": game.get("gameDate"),
                "status_abstract": status.get("abstractGameState"),
                "status_detailed": status.get("detailedState"),
                "home_team_id": str(home["team"]["id"]),
                "away_team_id": str(away["team"]["id"]),
                "home_team_name": home["team"].get("name"),
                "away_team_name": away["team"].get("name"),
                "home_probable_starter_id": _person_id(home.get("probablePitcher")),
                "away_probable_starter_id": _person_id(away.get("probablePitcher")),
                "home_probable_starter_name": (
                    (home.get("probablePitcher") or {}).get("fullName")
                ),
                "away_probable_starter_name": (
                    (away.get("probablePitcher") or {}).get("fullName")
                ),
                "venue_id": (
                    str(venue.get("id")) if venue.get("id") is not None else None
                ),
                "venue_name": venue.get("name"),
            })
    return sorted(
        rows,
        key=lambda r: (r.get("game_time_utc") or "", r["game_pk"]),
    )


def live_slate(game_date, fetcher=fetch_json):
    return _extract_live_slate(fetcher(live_schedule_url(game_date)))
