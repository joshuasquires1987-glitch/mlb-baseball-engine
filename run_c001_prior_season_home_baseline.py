import json
import math
from pathlib import Path

from mlb_bulk_schedule_runtime import completed_games_chunked
from run_v11_structural_benchmark import load_jsonl, aggregate, calibration_table

INPUT = "v11_structural_default_scored_games.jsonl"
REPORT = "c001_prior_season_home_baseline_report.json"
LEDGER = "c001_prior_season_home_baseline_scored_games.jsonl"

TRAIN_START = "2024-03-20"
TRAIN_END = "2024-09-29"

BASELINE_HOME_FEATURE = 0.10
BASELINE_HOME_WEIGHT = 0.04
BASELINE_HOME_LOGIT_CONTRIBUTION = BASELINE_HOME_FEATURE * BASELINE_HOME_WEIGHT
EPS = 1e-15

def sigmoid(x):
    return 1.0 / (1.0 + math.exp(-max(-35.0, min(35.0, float(x)))))

def logit(p):
    p = min(1.0 - EPS, max(EPS, float(p)))
    return math.log(p / (1.0 - p))

def estimate_prior_season_home_intercept(games):
    wins = 0
    eligible = 0
    for g in games:
        hr = g.get("home_runs")
        ar = g.get("away_runs")
        if hr is None or ar is None or float(hr) == float(ar):
            continue
        eligible += 1
        if float(hr) > float(ar):
            wins += 1
    if eligible == 0:
        raise ValueError("no eligible prior-season games for home-intercept estimate")
    rate = wins / eligible
    return {
        "eligible_games": eligible,
        "home_wins": wins,
        "home_win_rate": rate,
        "home_logit_intercept": logit(rate),
    }

def apply_challenger(rows, home_intercept):
    out = []
    for r in rows:
        baseline_score = float(r["weighted_score"])
        challenger_score = (
            baseline_score
            - BASELINE_HOME_LOGIT_CONTRIBUTION
            + float(home_intercept)
        )
        p = sigmoid(challenger_score)
        y = float(r["home_win"])
        p_log = min(1.0 - EPS, max(EPS, p))
        brier = (p - y) ** 2
        ll = -(y * math.log(p_log) + (1.0 - y) * math.log(1.0 - p_log))
        predicted_home = p >= 0.5
        correct = (predicted_home and y == 1.0) or ((not predicted_home) and y == 0.0)

        out.append({
            **r,
            "challenger_id": "C001",
            "challenger_label": "prior-season-home-baseline",
            "baseline_home_win_probability": float(r["home_win_probability"]),
            "baseline_brier": float(r["brier"]),
            "baseline_log_loss": float(r["log_loss"]),
            "home_win_probability": p,
            "weighted_score": challenger_score,
            "brier": brier,
            "log_loss": ll,
            "correct_side": bool(correct),
            "probability_margin": abs(p - 0.5),
        })
    return out

def compare(baseline_rows, challenger_rows):
    baseline = aggregate(baseline_rows)
    challenger = aggregate(challenger_rows)
    _, base_ece = calibration_table(baseline_rows)
    _, chall_ece = calibration_table(challenger_rows)
    return {
        "baseline": {
            **baseline,
            "expected_calibration_error_5pp_bins": base_ece,
        },
        "challenger": {
            **challenger,
            "expected_calibration_error_5pp_bins": chall_ece,
        },
        "delta_challenger_minus_baseline": {
            "brier": challenger["brier"] - baseline["brier"],
            "log_loss": challenger["log_loss"] - baseline["log_loss"],
            "accuracy": challenger["accuracy"] - baseline["accuracy"],
            "calibration_bias": challenger["calibration_bias"] - baseline["calibration_bias"],
            "ece_5pp_bins": chall_ece - base_ece,
        },
    }

def write_jsonl(rows, path):
    with open(path, "w", encoding="utf-8") as f:
        for row in rows:
            f.write(json.dumps(row, separators=(",", ":")) + "\n")

def main():
    baseline_rows = load_jsonl(INPUT)
    train_games, train_chunks = completed_games_chunked(TRAIN_START, TRAIN_END)
    training = estimate_prior_season_home_intercept(train_games)
    challenger_rows = apply_challenger(baseline_rows, training["home_logit_intercept"])
    comparison = compare(baseline_rows, challenger_rows)

    report = {
        "challenger_id": "C001",
        "challenger_label": "prior-season-home-baseline",
        "status": "research-only",
        "production_model_changed": False,
        "sportsbook_prices_used": False,
        "training_period": {
            "start": TRAIN_START,
            "end": TRAIN_END,
            "source": "MLB completed games",
            "training_only": True,
            **training,
            "chunks": train_chunks,
        },
        "validation_period": {
            "season": 2025,
            "games": len(baseline_rows),
            "identical_games_to_BT_0088": True,
            "2025_outcomes_used_for_parameter_estimation": False,
        },
        "method": {
            "description": (
                "Replace only the current structural home-field logit contribution "
                "with a home intercept estimated from 2024 completed-game outcomes."
            ),
            "baseline_home_feature": BASELINE_HOME_FEATURE,
            "baseline_home_weight": BASELINE_HOME_WEIGHT,
            "baseline_home_logit_contribution_removed": BASELINE_HOME_LOGIT_CONTRIBUTION,
            "other_features_and_weights_unchanged": True,
        },
        "comparison": comparison,
        "promotion_decision": "NOT_AUTOMATIC",
        "decision_rule": (
            "C001 may inform future architecture only if Brier/log loss/calibration "
            "improve on held-out 2025 without material subgroup degradation. "
            "No production mutation is authorized by this run."
        ),
    }

    write_jsonl(challenger_rows, LEDGER)
    Path(REPORT).write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps(report, indent=2))

if __name__ == "__main__":
    main()
