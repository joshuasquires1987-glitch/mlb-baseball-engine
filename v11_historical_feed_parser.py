def innings_to_outs(value):
    s = str(value or "0.0")
    if "." not in s:
        return int(float(s)) * 3
    whole, frac = s.split(".", 1)
    return int(whole) * 3 + int(frac[:1] or 0)

def parse_team_pitching(team_box, team_id, game_time_utc):
    players = team_box.get("players") or {}
    pitcher_ids = [str(x) for x in (team_box.get("pitchers") or [])]
    rows = []
    for i, pid in enumerate(pitcher_ids):
        p = players.get(f"ID{pid}") or players.get(pid) or {}
        stats = ((p.get("stats") or {}).get("pitching") or {})
        if not stats:
            continue
        rows.append({
            "date": game_time_utc,
            "id": str(pid),
            "team": str(team_id),
            "p_gs": 1 if i == 0 else 0,
            "p_bfp": float(stats.get("battersFaced", 0) or 0),
            "p_r": float(stats.get("runs", 0) or 0),
            "p_ipouts": float(innings_to_outs(stats.get("inningsPitched", "0.0"))),
            "p_so": float(stats.get("strikeOuts", 0) or 0),
            "p_bb": float(stats.get("baseOnBalls", 0) or 0),
            "p_hr": float(stats.get("homeRuns", 0) or 0),
            "p_hbp": float(stats.get("hitBatsmen", 0) or 0),
            "source_exact": True,
        })
    return rows

def parse_final_feed(game, feed):
    box = (((feed.get("liveData") or {}).get("boxscore") or {}).get("teams") or {})
    pitching = []
    pitching += parse_team_pitching(
        box.get("away") or {},
        game["away_team_id"],
        game["game_time_utc"],
    )
    pitching += parse_team_pitching(
        box.get("home") or {},
        game["home_team_id"],
        game["game_time_utc"],
    )
    return {
        "game_pk": str(game["game_pk"]),
        "game_date": game["game_date"],
        "game_time_utc": game["game_time_utc"],
        "home_team_id": str(game["home_team_id"]),
        "away_team_id": str(game["away_team_id"]),
        "home_runs": game.get("home_runs"),
        "away_runs": game.get("away_runs"),
        "pitching_rows": pitching,
    }
