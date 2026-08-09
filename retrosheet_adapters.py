import pandas as pd

def starter_rows_from_pitching(df,pitcher_id):
    q=df[(df["id"]==pitcher_id) & (pd.to_numeric(df["p_gs"],errors="coerce").fillna(0)>0)].copy()
    q["date"]=pd.to_datetime(q["date"].astype(str))
    return [{
        "date":r.date,
        "batters_faced":float(getattr(r,"p_bfp",0) or 0),
        "runs_allowed":float(getattr(r,"p_r",0) or 0),
        "outs":float(getattr(r,"p_ipouts",0) or 0),
    } for r in q.itertuples(index=False)]

def bullpen_rows_from_pitching(df,team):
    q=df[(df["team"]==team) & (pd.to_numeric(df["p_gs"],errors="coerce").fillna(0)==0)].copy()
    q["date"]=pd.to_datetime(q["date"].astype(str))
    return [{
        "date":r.date,
        "batters_faced":float(getattr(r,"p_bfp",0) or 0),
        "runs_allowed":float(getattr(r,"p_r",0) or 0),
    } for r in q.itertuples(index=False)]

def team_rows_from_games(df,team):
    q=df[(df["hometeam"]==team)|(df["visteam"]==team)].copy()
    q["date"]=pd.to_datetime(q["date"])
    rows=[]
    for r in q.itertuples(index=False):
        if r.hometeam==team:
            rf,ra=float(r.hruns),float(r.vruns)
        else:
            rf,ra=float(r.vruns),float(r.hruns)
        rows.append({"date":r.date,"runs_for":rf,"runs_against":ra})
    return rows
