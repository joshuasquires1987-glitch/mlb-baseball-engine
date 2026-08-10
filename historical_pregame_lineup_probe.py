def _order_from_team(team):
    raw=(team or {}).get("battingOrder") or []
    out=[]
    for value in raw:
        try:
            out.append(int(value))
        except Exception:
            return []
    return out

def extract_starting_orders(timecoded_state):
    live=(timecoded_state or {}).get("liveData") or {}
    box=(live.get("boxscore") or {}).get("teams") or {}
    return {
        "away":_order_from_team(box.get("away")),
        "home":_order_from_team(box.get("home")),
    }

def valid_nine(order):
    return len(order)==9 and len(set(order))==9

def probe_result(game,pregame_payload):
    if pregame_payload is None:
        return {
            "game_pk":str(game["game_pk"]),
            "game_date":game.get("game_date"),
            "recoverable":False,
            "reason":"no-pregame-timecode",
        }

    orders=extract_starting_orders(pregame_payload["state"])
    away_ok=valid_nine(orders["away"])
    home_ok=valid_nine(orders["home"])

    return {
        "game_pk":str(game["game_pk"]),
        "game_date":game.get("game_date"),
        "recoverable":away_ok and home_ok,
        "reason":None if away_ok and home_ok else "pregame-orders-incomplete",
        "timecode":pregame_payload["timecode"],
        "scheduled_game_time_utc":game.get("game_time_utc"),
        "away_order_count":len(orders["away"]),
        "home_order_count":len(orders["home"]),
        "away_order":orders["away"] if away_ok else [],
        "home_order":orders["home"] if home_ok else [],
        "source":"MLB-StatsAPI-timecoded-live-feed",
        "captured_before_scheduled_first_pitch":True,
    }

def summarize(results):
    total=len(results)
    good=sum(1 for r in results if r.get("recoverable"))
    reasons={}
    for r in results:
        if not r.get("recoverable"):
            key=r.get("reason") or "unknown"
            reasons[key]=reasons.get(key,0)+1
    return {
        "games_probed":total,
        "recoverable_games":good,
        "recoverable_rate":good/total if total else 0.0,
        "failure_reasons":reasons,
        "promising_for_650_gate":good/max(total,1) >= 0.30,
    }
