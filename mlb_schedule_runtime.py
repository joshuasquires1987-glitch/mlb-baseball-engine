import json
from urllib.request import Request,urlopen
from urllib.parse import urlencode

BASE="https://statsapi.mlb.com/api/v1"

def fetch_json(url,timeout=30):
    req=Request(url,headers={"User-Agent":"mlb-baseball-engine/1.0","Accept":"application/json"})
    with urlopen(req,timeout=timeout) as r:
        return json.loads(r.read().decode("utf-8"))

def schedule_url(team_id,start_date,end_date):
    q=urlencode({
        "sportId":1,
        "teamId":team_id,
        "startDate":start_date,
        "endDate":end_date,
    })
    return f"{BASE}/schedule?{q}"

def completed_games_for_team(team_id,start_date,end_date,fetcher=fetch_json):
    payload=fetcher(schedule_url(team_id,start_date,end_date))
    rows=[]
    for block in payload.get("dates",[]):
        for g in block.get("games",[]):
            state=g.get("status",{}).get("abstractGameState","")
            detailed=g.get("status",{}).get("detailedState","")
            if state!="Final" and "Final" not in detailed:
                continue
            rows.append({
                "game_pk":str(g["gamePk"]),
                "game_date":block.get("date"),
                "away_team_id":str(g["teams"]["away"]["team"]["id"]),
                "home_team_id":str(g["teams"]["home"]["team"]["id"]),
            })
    return rows
