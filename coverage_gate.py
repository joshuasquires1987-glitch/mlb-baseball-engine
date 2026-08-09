from collections import Counter

def starter_coverage(rows,starter_id,target_date,min_starts=5):
    starts=[r for r in rows if str(r.get("id"))==str(starter_id)
            and int(r.get("p_gs",0))==1 and str(r.get("date")) < str(target_date)]
    exact=[r for r in starts if r.get("source_exact") is True
           and r.get("p_bfp") is not None and r.get("p_ipouts") is not None and r.get("p_r") is not None]
    return {
        "starts":len(exact),
        "required":int(min_starts),
        "ready":len(exact)>=int(min_starts),
    }

def bullpen_coverage(rows,team,target_date,min_relief_rows=15):
    rel=[r for r in rows if r.get("team")==team and int(r.get("p_gs",0))==0
         and str(r.get("date")) < str(target_date) and r.get("source_exact") is True]
    return {"rows":len(rel),"required":int(min_relief_rows),"ready":len(rel)>=int(min_relief_rows)}

def team_game_coverage(team_games,team,target_date,min_games=10):
    games=[r for r in team_games if r.get("team")==team and str(r.get("date")) < str(target_date)]
    return {"games":len(games),"required":int(min_games),"ready":len(games)>=int(min_games)}

def full_history_gate(pitching_rows,team_games,target_date,away_team,home_team,
                      away_starter_id,home_starter_id,
                      min_starts=5,min_relief_rows=15,min_team_games=10):
    checks={
        "away_starter":starter_coverage(pitching_rows,away_starter_id,target_date,min_starts),
        "home_starter":starter_coverage(pitching_rows,home_starter_id,target_date,min_starts),
        "away_bullpen":bullpen_coverage(pitching_rows,away_team,target_date,min_relief_rows),
        "home_bullpen":bullpen_coverage(pitching_rows,home_team,target_date,min_relief_rows),
        "away_team":team_game_coverage(team_games,away_team,target_date,min_team_games),
        "home_team":team_game_coverage(team_games,home_team,target_date,min_team_games),
    }
    return {"checks":checks,"ready":all(x["ready"] for x in checks.values())}
