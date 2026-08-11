import json
from calendar import monthrange
from datetime import date, datetime, timedelta
from urllib.request import Request, urlopen
from urllib.parse import urlencode

BASE="https://statsapi.mlb.com/api/v1"

def fetch_json(url,timeout=30):
    req=Request(
        url,
        headers={
            "User-Agent":"mlb-baseball-engine/1.0",
            "Accept":"application/json",
        },
    )
    with urlopen(req,timeout=timeout) as r:
        return json.loads(r.read().decode("utf-8"))

def schedule_url(start_date,end_date):
    q=urlencode({
        "sportId":1,
        "startDate":start_date,
        "endDate":end_date,
    })
    return f"{BASE}/schedule?{q}"

def _parse_date(value):
    if isinstance(value,date) and not isinstance(value,datetime):
        return value
    return date.fromisoformat(str(value))

def _extract_completed(payload):
    out=[]
    for block in payload.get("dates",[]):
        for g in block.get("games",[]):
            state=g.get("status",{}).get("abstractGameState","")
            detailed=g.get("status",{}).get("detailedState","")
            if state!="Final" and "Final" not in detailed:
                continue

            away_runs=g["teams"]["away"].get("score")
            home_runs=g["teams"]["home"].get("score")

            # Historical replay state must only consume games with an actual
            # final score. MLB can occasionally expose a Final-status schedule
            # record without populated score fields; those records are not
            # valid completed-game observations for model-state reconstruction.
            if away_runs is None or home_runs is None:
                continue

            out.append({
                "game_pk":str(g["gamePk"]),
                "game_date":block.get("date"),
                "game_time_utc":g.get("gameDate"),
                "away_team_id":str(g["teams"]["away"]["team"]["id"]),
                "home_team_id":str(g["teams"]["home"]["team"]["id"]),
                "away_runs":away_runs,
                "home_runs":home_runs,
                "venue_id":(
                    str((g.get("venue") or {}).get("id"))
                    if (g.get("venue") or {}).get("id") is not None
                    else None
                ),
            })
    return out

def completed_games(start_date,end_date,fetcher=fetch_json):
    payload=fetcher(schedule_url(start_date,end_date))
    return _extract_completed(payload)

def month_chunks(start_date,end_date):
    start=_parse_date(start_date)
    end=_parse_date(end_date)
    if end < start:
        raise ValueError("end_date precedes start_date")

    cur=start
    while cur <= end:
        last=date(cur.year,cur.month,monthrange(cur.year,cur.month)[1])
        chunk_end=min(last,end)
        yield cur.isoformat(),chunk_end.isoformat()
        cur=chunk_end+timedelta(days=1)

def completed_games_chunked(start_date,end_date,fetcher=fetch_json):
    by_pk={}
    chunk_stats=[]

    for chunk_start,chunk_end in month_chunks(start_date,end_date):
        payload=fetcher(schedule_url(chunk_start,chunk_end))
        games=_extract_completed(payload)
        chunk_stats.append({
            "start_date":chunk_start,
            "end_date":chunk_end,
            "completed_games":len(games),
        })
        for g in games:
            by_pk[str(g["game_pk"])]=g

    ordered=sorted(
        by_pk.values(),
        key=lambda g:(
            g.get("game_time_utc") or "",
            str(g["game_pk"]),
        ),
    )
    return ordered,chunk_stats
