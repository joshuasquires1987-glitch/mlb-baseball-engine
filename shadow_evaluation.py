def brier(prob,outcome): return (float(prob)-float(outcome))**2

def evaluate_predictions(production_prediction,shadow_prediction,home_won):
    y=int(bool(home_won))
    return {
        "game_id":production_prediction.game_id,
        "production_version":production_prediction.model_version,
        "shadow_version":shadow_prediction.model_version,
        "production_brier":brier(production_prediction.home_win_probability,y),
        "shadow_brier":brier(shadow_prediction.home_win_probability,y),
        "production_home_probability":production_prediction.home_win_probability,
        "shadow_home_probability":shadow_prediction.home_win_probability,
        "home_won":y,
    }
