def manifest(rows, skipped):
    dates=sorted(r["game_date"] for r in rows)
    return {
        "usable_games":len(rows),
        "skipped_games":len(skipped),
        "first_game_date":dates[0] if dates else None,
        "last_game_date":dates[-1] if dates else None,
        "skip_reasons":_counts(skipped),
        "leakage_policy":"pregame-snapshot-only-for-lineup-platoon",
    }

def _counts(skipped):
    out={}
    for s in skipped:
        reason=s.get("reason","unknown")
        out[reason]=out.get(reason,0)+1
    return out
