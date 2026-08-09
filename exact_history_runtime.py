import json
from urllib.request import Request,urlopen

def fetch_boxscore(game_pk,timeout=20):
    url=f"https://statsapi.mlb.com/api/v1/game/{game_pk}/boxscore"
    req=Request(url,headers={
        "User-Agent":"Mozilla/5.0 mlb-baseball-engine/1.0",
        "Accept":"application/json",
    })
    with urlopen(req,timeout=timeout) as resp:
        return {
            "source_url":url,
            "payload":json.loads(resp.read().decode("utf-8")),
        }
