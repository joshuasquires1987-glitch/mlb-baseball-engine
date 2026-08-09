import json
from urllib.request import urlopen,Request
from mlb_history_endpoints import player_game_log_url

def fetch_json(url,timeout=20):
    req=Request(url,headers={"User-Agent":"mlb-baseball-engine/1.0"})
    with urlopen(req,timeout=timeout) as r:
        return json.loads(r.read().decode("utf-8"))

def fetch_pitcher_game_log(player_id,season):
    url=player_game_log_url(player_id,season,"pitching")
    return {"player_id":str(player_id),"source_url":url,"payload":fetch_json(url)}

def extract_stat_splits(payload):
    stats=payload.get("stats",[])
    if not stats: return []
    return stats[0].get("splits",[])
