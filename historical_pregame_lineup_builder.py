import json
from concurrent.futures import ThreadPoolExecutor, as_completed
from mlb_historical_timecode_runtime import fetch_pregame_state
from historical_pregame_lineup_probe import extract_starting_orders, valid_nine

def build_one(game, fetcher=None, safety_seconds=60):
    kwargs={"safety_seconds":safety_seconds}
    if fetcher is not None:
        kwargs["fetcher"]=fetcher
    payload=fetch_pregame_state(game["game_pk"],game["game_time_utc"],**kwargs)
    if payload is None:
        return None,{"game_pk":str(game["game_pk"]),"game_date":game.get("game_date"),"reason":"no-pregame-timecode"}
    orders=extract_starting_orders(payload["state"])
    if not valid_nine(orders["away"]) or not valid_nine(orders["home"]):
        return None,{"game_pk":str(game["game_pk"]),"game_date":game.get("game_date"),"reason":"pregame-orders-incomplete","timecode":payload["timecode"],"away_order_count":len(orders["away"]),"home_order_count":len(orders["home"])}
    return {
        "game_pk":str(game["game_pk"]),
        "game_date":game.get("game_date"),
        "scheduled_game_time_utc":game.get("game_time_utc"),
        "captured_before_first_pitch":True,
        "capture_basis":"MLB historical timecode at least 60s before scheduled game time",
        "timecode":payload["timecode"],
        "safety_seconds":int(safety_seconds),
        "away_team_id":str(game["away_team_id"]),
        "home_team_id":str(game["home_team_id"]),
        "away_batting_order":orders["away"],
        "home_batting_order":orders["home"],
        "source":"MLB-StatsAPI-timecoded-live-feed",
        "source_policy":"no-current-feed-or-final-boxscore-lineup-fallback",
        "platoon_lineup_delta":None,
        "feature_status":"raw-certified-lineup-only",
    },None

def build_all(games,max_workers=16,safety_seconds=60,fetcher=None):
    rows=[]; failures=[]
    ordered=sorted(games,key=lambda g:(g.get("game_time_utc") or "",str(g["game_pk"])))
    def task(g):
        try:
            return build_one(g,fetcher=fetcher,safety_seconds=safety_seconds)
        except Exception as e:
            return None,{"game_pk":str(g["game_pk"]),"game_date":g.get("game_date"),"reason":f"request-error:{type(e).__name__}","detail":str(e)[:300]}
    with ThreadPoolExecutor(max_workers=max_workers) as pool:
        futures=[pool.submit(task,g) for g in ordered]
        for i,f in enumerate(as_completed(futures),1):
            row,err=f.result()
            if row is not None: rows.append(row)
            if err is not None: failures.append(err)
            if i % 100 == 0 or i == len(futures):
                print(f"processed={i}/{len(futures)} recovered={len(rows)} failures={len(failures)}",flush=True)
    rows.sort(key=lambda r:(r.get("scheduled_game_time_utc") or "",r["game_pk"]))
    failures.sort(key=lambda r:(r.get("game_date") or "",r["game_pk"]))
    return rows,failures

def write_jsonl(rows,path):
    with open(path,"w",encoding="utf-8") as f:
        for row in rows:
            f.write(json.dumps(row,separators=(",",":"))+"\n")
