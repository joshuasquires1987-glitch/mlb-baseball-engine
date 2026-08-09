def brier(prob,outcome): return (float(prob)-float(outcome))**2
def score_shadow_record(record,home_won):
    out=int(bool(home_won))
    return {"game_id":record["game_id"],"production_version":record["production"]["version"],
            "shadow_version":record["shadow"]["model_version"],
            "production_home_prob":record["production"]["home_prob"],
            "shadow_home_prob":record["shadow"]["home_win_probability"],"home_won":out,
            "production_brier":brier(record["production"]["home_prob"],out),
            "shadow_brier":brier(record["shadow"]["home_win_probability"],out)}
