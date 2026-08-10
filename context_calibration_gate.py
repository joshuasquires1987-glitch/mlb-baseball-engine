MIN_TRAIN_GAMES = 500
MIN_HOLDOUT_GAMES = 150
MAX_ABS_COEF = 1.0

def calibration_gate(training_games, holdout_games, coefficients, holdout_logloss_delta):
    issues = []

    if int(training_games) < MIN_TRAIN_GAMES:
        issues.append("insufficient-training-games")
    if int(holdout_games) < MIN_HOLDOUT_GAMES:
        issues.append("insufficient-holdout-games")

    for name, value in coefficients.items():
        if abs(float(value)) > MAX_ABS_COEF:
            issues.append(f"coefficient-out-of-bounds:{name}")

    # Challenger must improve holdout log loss versus the same model
    # with context terms zeroed. Negative delta means lower/better log loss.
    if float(holdout_logloss_delta) >= 0:
        issues.append("no-holdout-logloss-improvement")

    return {
        "eligible_for_shadow_review": not issues,
        "issues": issues,
        "production_promotion_allowed": False,
    }
