import pandas as pd

def canonical_games_frame(bundle):
    rows=bundle.get("canonical_team_games",[])
    required={"date","hometeam","visteam","hruns","vruns","source_exact"}
    for i,r in enumerate(rows):
        missing=required-set(r)
        if missing: raise ValueError(f"canonical game row {i} missing {sorted(missing)}")
        if r["source_exact"] is not True: raise ValueError("non-exact canonical game row")
    return pd.DataFrame(rows)
