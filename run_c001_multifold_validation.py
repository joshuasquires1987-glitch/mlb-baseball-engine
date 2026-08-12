import json
import math
from pathlib import Path

from mlb_bulk_schedule_runtime import completed_games_chunked

REPORT = "c001_multifold_validation_report.json"
EPS = 1e-15

# Chronological, leakage-safe train -> validation folds.
FOLDS = [
    (2021, 2022),
    (2022, 2023),
    (2023, 2024),
    (2024, 2025),
]


def logit(p):
    p = min(1.0 - EPS, max(EPS, float(p)))
    return math.log(p / (1.0 - p))


def season_dates(year):
    # Wide MLB regular-season window. completed_games_chunked filters completed games.
    return f"{year}-03-15", f"{year}-10-05"


def summarize_home_results(games):
    n = wins = 0
    for g in games:
        hr, ar = g.get("home_runs"), g.get("away_runs")
        if hr is None or ar is None or float(hr) == float(ar):
            continue
        n += 1
        wins += float(hr) > float(ar)
    if not n:
        raise ValueError("no eligible completed games")
    rate = wins / n
    return {"n": n, "home_wins": wins, "home_win_rate": rate, "logit": logit(rate)}


def score_constant_probability(games, p):
    n = 0
    brier = 0.0
    log_loss = 0.0
    wins = 0
    for g in games:
        hr, ar = g.get("home_runs"), g.get("away_runs")
        if hr is None or ar is None or float(hr) == float(ar):
            continue
        y = 1.0 if float(hr) > float(ar) else 0.0
        wins += y
        n += 1
        brier += (p - y) ** 2
        pp = min(1.0 - EPS, max(EPS, p))
        log_loss += -(y * math.log(pp) + (1.0 - y) * math.log(1.0 - pp))
    return {
        "n": n,
        "actual_home_win_rate": wins / n,
        "mean_probability": p,
        "calibration_bias": p - wins / n,
        "brier": brier / n,
        "log_loss": log_loss / n,
    }


def main():
    folds = []
    for train_year, validation_year in FOLDS:
        ts, te = season_dates(train_year)
        vs, ve = season_dates(validation_year)
        train_games, train_chunks = completed_games_chunked(ts, te)
        validation_games, validation_chunks = completed_games_chunked(vs, ve)

        training = summarize_home_results(train_games)
        prior_p = training["home_win_rate"]

        c001 = score_constant_probability(validation_games, prior_p)
        neutral = score_constant_probability(validation_games, 0.5)

        folds.append({
            "train_year": train_year,
            "validation_year": validation_year,
            "training": training,
            "validation": {
                "n": c001["n"],
                "actual_home_win_rate": c001["actual_home_win_rate"],
            },
            "c001_prior_season_constant_home_probability": c001,
            "neutral_50pct_reference": neutral,
            "delta_c001_minus_neutral": {
                "brier": c001["brier"] - neutral["brier"],
                "log_loss": c001["log_loss"] - neutral["log_loss"],
            },
            "train_chunks": train_chunks,
            "validation_chunks": validation_chunks,
        })

    improved_brier = sum(
        f["delta_c001_minus_neutral"]["brier"] < 0 for f in folds
    )
    improved_logloss = sum(
        f["delta_c001_minus_neutral"]["log_loss"] < 0 for f in folds
    )

    report = {
        "experiment_id": "C001-MF",
        "status": "research-only",
        "production_model_changed": False,
        "sportsbook_prices_used": False,
        "purpose": (
            "Test temporal stability of prior-season MLB home advantage across "
            "multiple strictly chronological folds before any architecture decision."
        ),
        "folds": folds,
        "summary": {
            "fold_count": len(folds),
            "c001_brier_better_than_50pct_folds": improved_brier,
            "c001_logloss_better_than_50pct_folds": improved_logloss,
            "all_folds_brier_improved": improved_brier == len(folds),
            "all_folds_logloss_improved": improved_logloss == len(folds),
        },
        "governance": {
            "automatic_promotion_authorized": False,
            "v11_weight_change_authorized": False,
            "note": (
                "This experiment validates only the temporal stability of the home "
                "baseline concept. It does not by itself validate the complete C001 "
                "challenger against full structural model predictions in every season."
            ),
        },
    }
    Path(REPORT).write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
