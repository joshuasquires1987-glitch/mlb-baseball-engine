import pandas as pd

def pitching_frame(bundle):
    rows=bundle.get("pitching_rows",[])
    required={"date","id","team","p_gs","p_bfp","p_r","p_ipouts","source_exact"}
    for i,r in enumerate(rows):
        missing=required-set(r)
        if missing: raise ValueError(f"pitching row {i} missing {sorted(missing)}")
        if r["source_exact"] is not True: raise ValueError("non-exact pitching row")
    return pd.DataFrame(rows)

def games_frame(bundle):
    rows=bundle.get("team_games",[])
    # Convert team-perspective rows into one canonical game row per date/opponent pair when possible.
    if not rows: return pd.DataFrame()
    required={"date","team","opponent","runs_for","runs_against"}
    for i,r in enumerate(rows):
        missing=required-set(r)
        if missing: raise ValueError(f"team row {i} missing {sorted(missing)}")
    seen=set(); out=[]
    for r in rows:
        key=(r["date"], tuple(sorted((r["team"],r["opponent"]))))
        if key in seen: continue
        seen.add(key)
        if r["runs_for"] > r["runs_against"]:
            # Venue is not inferred. The assembler's team-strength path can consume normalized
            # perspective rows via adapter below; canonical home/away conversion is forbidden.
            pass
        out.append(dict(r))
    return pd.DataFrame(out)
