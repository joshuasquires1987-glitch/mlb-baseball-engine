import json
from urllib.request import Request, urlopen

BASE = "https://statsapi.mlb.com/api/v1"


def fetch_json(url, timeout=30):
    req = Request(
        url,
        headers={
            "User-Agent": "mlb-baseball-engine/1.0",
            "Accept": "application/json",
        },
    )
    with urlopen(req, timeout=timeout) as r:
        return json.loads(r.read().decode("utf-8"))


def live_feed_url(game_pk):
    return f"{BASE}.1/game/{game_pk}/feed/live"


def fetch_linescore_summary(game_pk, fetcher=fetch_json):
    # The /linescore endpoint reliably exposes runs but does not reliably
    # include team abbreviation metadata. The live feed contains both:
    #   gameData.teams.*.abbreviation
    #   liveData.linescore.teams.*.runs
    p = fetcher(live_feed_url(game_pk))

    game_teams = p.get("gameData", {}).get("teams", {})
    line_teams = p.get("liveData", {}).get("linescore", {}).get("teams", {})

    away_abbr = game_teams.get("away", {}).get("abbreviation")
    home_abbr = game_teams.get("home", {}).get("abbreviation")
    away_runs = line_teams.get("away", {}).get("runs")
    home_runs = line_teams.get("home", {}).get("runs")

    if None in (away_abbr, home_abbr, away_runs, home_runs):
        raise ValueError(
            f"Missing exact team/score fields for game {game_pk}: "
            f"away={away_abbr}/{away_runs}, home={home_abbr}/{home_runs}"
        )

    return {
        "teams": {
            "away": {
                "team": {"abbreviation": away_abbr},
                "score": away_runs,
            },
            "home": {
                "team": {"abbreviation": home_abbr},
                "score": home_runs,
            },
        }
    }
