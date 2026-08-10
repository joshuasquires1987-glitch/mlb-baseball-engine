import json
from datetime import datetime, timedelta, timezone
from urllib.parse import urlencode
from urllib.request import Request, urlopen

BASE="https://statsapi.mlb.com/api/v1.1"

def fetch_json(url,timeout=30):
    req=Request(url,headers={
        "User-Agent":"mlb-baseball-engine/1.0",
        "Accept":"application/json",
    })
    with urlopen(req,timeout=timeout) as r:
        return json.loads(r.read().decode("utf-8"))

def timestamps_url(game_pk):
    return f"{BASE}/game/{game_pk}/feed/live/timestamps"

def timecoded_feed_url(game_pk,timecode):
    q=urlencode({"timecode":timecode})
    return f"{BASE}/game/{game_pk}/feed/live?{q}"

def parse_timecode(value):
    return datetime.strptime(str(value),"%Y%m%d_%H%M%S").replace(tzinfo=timezone.utc)

def parse_utc(value):
    dt=datetime.fromisoformat(str(value).replace("Z","+00:00"))
    if dt.tzinfo is None:
        dt=dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc)

def safe_pregame_timecode(timestamps,scheduled_game_time_utc,safety_seconds=60):
    cutoff=parse_utc(scheduled_game_time_utc)-timedelta(seconds=safety_seconds)
    eligible=[]
    for raw in timestamps or []:
        try:
            dt=parse_timecode(raw)
        except Exception:
            continue
        if dt <= cutoff:
            eligible.append((dt,str(raw)))
    if not eligible:
        return None
    eligible.sort()
    return eligible[-1][1]

def fetch_pregame_state(game_pk,scheduled_game_time_utc,fetcher=fetch_json,safety_seconds=60):
    timestamps=fetcher(timestamps_url(game_pk))
    code=safe_pregame_timecode(
        timestamps,
        scheduled_game_time_utc,
        safety_seconds=safety_seconds,
    )
    if code is None:
        return None
    state=fetcher(timecoded_feed_url(game_pk,code))
    return {
        "game_pk":str(game_pk),
        "timecode":code,
        "scheduled_game_time_utc":scheduled_game_time_utc,
        "safety_seconds":int(safety_seconds),
        "state":state,
    }
