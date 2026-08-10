import json
from urllib.request import Request,urlopen
from urllib.parse import urlencode

BASE="https://statsapi.mlb.com/api/v1"

def fetch_json(url,timeout=30):
    req=Request(url,headers={"User-Agent":"mlb-baseball-engine/1.0","Accept":"application/json"})
    with urlopen(req,timeout=timeout) as r:
        return json.loads(r.read().decode("utf-8"))

def schedule_url(start_date,end_date):
    q=urlencode({"sportId":1,"startDate":start_date,"endDate":end_date})
    return f"{BASE}/schedule?{q}"

def completed_games(start_date,end_date,fetcher=fetch_json):
    payload=fetcher(schedule_url(start_date,end_date))
    out=[]
    for block in payload.get("dates",[]):
        for g in block.get("games",[]):
            state=g.get("status",{}).get("abstractGameState","")
            detailed=g.get("status",{}).get("detailedState","")
            if state!="Final" and "Final" not in detailed:
                continue
            out.append({
                "game_pk":str(g["gamePk"]),
                "game_date":block.get("date"),
                "game_time_utc":g.get("gameDate"),
                "away_team_id":str(g["teams"]["away"]["team"]["id"]),
                "home_team_id":str(g["teams"]["home"]["team"]["id"]),
                "away_runs":g["teams"]["away"].get("score"),
                "home_runs":g["teams"]["home"].get("score"),
                "venue_id":str((g.get("venue") or {}).get("id")) if (g.get("venue") or {}).get("id") is not None else None,
            })
    return out
