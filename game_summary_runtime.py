import json
from urllib.request import Request,urlopen

BASE="https://statsapi.mlb.com/api/v1"

def fetch_json(url,timeout=30):
    req=Request(url,headers={"User-Agent":"mlb-baseball-engine/1.0","Accept":"application/json"})
    with urlopen(req,timeout=timeout) as r:
        return json.loads(r.read().decode("utf-8"))

def linescore_url(game_pk):
    return f"{BASE}/game/{game_pk}/linescore"

def fetch_linescore_summary(game_pk,fetcher=fetch_json):
    p=fetcher(linescore_url(game_pk))
    return {
        "teams":{
            "away":{
                "team":{"abbreviation":p.get("teams",{}).get("away",{}).get("team",{}).get("abbreviation")},
                "score":p.get("teams",{}).get("away",{}).get("runs"),
            },
            "home":{
                "team":{"abbreviation":p.get("teams",{}).get("home",{}).get("team",{}).get("abbreviation")},
                "score":p.get("teams",{}).get("home",{}).get("runs"),
            },
        }
    }
