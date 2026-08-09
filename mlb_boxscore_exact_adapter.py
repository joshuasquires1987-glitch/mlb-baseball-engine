from datetime import datetime

def innings_to_outs(ip):
    s=str(ip)
    if "." in s:
        whole, frac=s.split(".",1)
        frac=int(frac)
    else:
        whole, frac=s, 0
    if frac not in (0,1,2):
        raise ValueError(f"Invalid baseball innings notation: {ip}")
    return int(whole)*3 + frac

def _player_id_from_key(key):
    return str(key).replace("ID","",1)

def exact_pitching_rows(boxscore_payload, game_date, team_code):
    rows=[]
    teams=boxscore_payload.get("teams",{})
    for side in ("away","home"):
        t=teams.get(side,{})
        if t.get("team",{}).get("abbreviation") != team_code:
            continue
        players=t.get("players",{})
        probable=t.get("probablePitcher",{})
        starter_id=str(probable.get("id")) if probable.get("id") is not None else None
        for key,p in players.items():
            stats=p.get("stats",{}).get("pitching")
            if not stats:
                continue
            pid=str(p.get("person",{}).get("id") or _player_id_from_key(key))
            bf=stats.get("battersFaced")
            ip=stats.get("inningsPitched")
            runs=stats.get("runs")
            if bf is None or ip is None or runs is None:
                continue
            rows.append({
                "date":game_date,
                "id":pid,
                "team":team_code,
                "p_gs":1 if starter_id and pid==starter_id else 0,
                "p_bfp":float(bf),
                "p_r":float(runs),
                "p_ipouts":float(innings_to_outs(ip)),
                "source_exact":True,
            })
    return rows

def exact_starter_row(boxscore_payload, game_date, team_code, pitcher_id):
    rows=exact_pitching_rows(boxscore_payload,game_date,team_code)
    matches=[r for r in rows if r["id"]==str(pitcher_id)]
    if not matches:
        raise KeyError(f"No exact pitching row for {pitcher_id}")
    row=matches[0]
    if row["p_gs"] != 1:
        raise ValueError(f"Pitcher {pitcher_id} was not the recorded starter")
    return row

def exact_relief_rows(boxscore_payload,game_date,team_code):
    return [r for r in exact_pitching_rows(boxscore_payload,game_date,team_code) if r["p_gs"]==0]
