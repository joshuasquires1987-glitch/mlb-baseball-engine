import pandas as pd

def pitching_frame(bundle):
    rows=bundle.get("pitching_rows",[])
    required={"date","id","team","p_gs","p_bfp","p_r","p_ipouts","source_exact"}
    for i,r in enumerate(rows):
        missing=required-set(r)
        if missing: raise ValueError(f"pitching row {i} missing {sorted(missing)}")
        if r["source_exact"] is not True: raise ValueError("non-exact pitching row")
    df=pd.DataFrame(rows)
    if not df.empty:
        df["id"]=df["id"].astype(str)
        df["team"]=df["team"].astype(str)
    return df

def games_frame(bundle):
    rows=bundle.get("team_games",[])
    required={"date","team","opponent","runs_for","runs_against"}
    for i,r in enumerate(rows):
        missing=required-set(r)
        if missing: raise ValueError(f"team row {i} missing {sorted(missing)}")

    # Existing assembler expects Retrosheet-style canonical game rows:
    # date, hometeam, visteam, hruns, vruns.
    # The exact bundle currently stores team-perspective rows and does NOT
    # preserve venue. We therefore fail closed instead of guessing home/away.
    if rows:
        raise RuntimeError(
            "Exact team-game bundle lacks explicit home/away venue fields; "
            "cannot safely convert to assembler game rows."
        )
    return pd.DataFrame(columns=["date","hometeam","visteam","hruns","vruns"])
