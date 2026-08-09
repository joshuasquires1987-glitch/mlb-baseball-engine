def build_daily_report(game_rows, validation_summary=None, gate_status=None):
    bets=[g for g in game_rows if g.get("production",{}).get("decision",{}).get("eligible")]
    return {
        "games_analyzed":len(game_rows),
        "production_candidates":len(bets),
        "candidates":[{
            "game_id":g["game_id"],
            "selected_side":g["production"]["decision"]["selected_side"],
            "edge_pp":g["production"]["decision"]["edge_pp"],
            "half_kelly_fraction":g["production"]["decision"]["half_kelly_fraction"],
            "v11_home_prob":g["production"]["home_prob"],
            "rc1_home_prob":g["shadow"]["home_win_probability"],
            "integrity":g["integrity"],
        } for g in bets],
        "validation":validation_summary or {},
        "rc1_gate":gate_status or {},
    }
