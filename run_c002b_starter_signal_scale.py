import json
import math
from pathlib import Path

from run_v11_structural_benchmark import aggregate, calibration_table, load_jsonl
from v11_structural_replay import sigmoid

INPUT = "c002a_starter_talent_v2_scored_games.jsonl"
REPORT = "c002b_starter_signal_scale_report.json"
SCORED = "c002b_starter_signal_scale_scored_games.jsonl"

SP_WEIGHT = 0.25
EPS = 1e-15

# Strict chronological split. Scale is selected only on early 2025.
TRAIN_END = "2025-06-30"
VALID_START = "2025-07-01"

SCALE_CANDIDATES = [round(x * 0.05, 2) for x in range(0, 31)]  # 0.00 to 1.50


def baseline_score(row):
    """
    Recover the untouched BT-0088 structural weighted score from the C002a row.
    C002a stored:
        c002_score = baseline_score - .25*baseline_sp + .25*c002_sp
    """
    return (
        float(row["weighted_score"])
        + SP_WEIGHT * float(row["baseline_starting_pitcher_feature"])
        - SP_WEIGHT * float(row["c002_starting_pitcher_feature"])
    )


def score_with_scale(row, scale):
    base = baseline_score(row)
    baseline_sp = float(row["baseline_starting_pitcher_feature"])
    c002_sp = float(row["c002_starting_pitcher_feature"])

    weighted_score = (
        base
        - SP_WEIGHT * baseline_sp
        + SP_WEIGHT * float(scale) * c002_sp
    )
    p = sigmoid(weighted_score)
    y = float(row["home_win"])
    pp = min(1.0 - EPS, max(EPS, p))
    brier = (p - y) ** 2
    log_loss = -(y * math.log(pp) + (1.0 - y) * math.log(1.0 - pp))
    correct = (p >= 0.5 and y == 1.0) or (p < 0.5 and y == 0.0)

    return {
        **row,
        "challenger_id": "C002b",
        "challenger_label": "starter-event-rate-v2-scaled",
        "c002b_scale": float(scale),
        "c002a_unscaled_home_win_probability": float(row["home_win_probability"]),
        "home_win_probability": p,
        "away_win_probability": 1.0 - p,
        "weighted_score": weighted_score,
        "brier": brier,
        "log_loss": log_loss,
        "correct_side": bool(correct),
        "probability_margin": abs(p - 0.5),
    }


def evaluate(rows, scale):
    scored = [score_with_scale(r, scale) for r in rows]
    stats = aggregate(scored)
    _, ece = calibration_table(scored)
    return {
        "scale": float(scale),
        "n": len(scored),
        "brier": stats["brier"],
        "log_loss": stats["log_loss"],
        "accuracy": stats["accuracy"],
        "calibration_bias": stats["calibration_bias"],
        "ece_5pp_bins": ece,
        "mean_probability_margin": stats["mean_probability_margin"],
    }, scored


def baseline_view(rows):
    out = []
    for r in rows:
        y = float(r["home_win"])
        p = float(r["baseline_home_win_probability"])
        pp = min(1.0 - EPS, max(EPS, p))
        out.append({
            **r,
            "home_win_probability": p,
            "brier": (p - y) ** 2,
            "log_loss": -(y * math.log(pp) + (1.0 - y) * math.log(1.0 - pp)),
            "correct_side": bool(
                (p >= 0.5 and y == 1.0) or (p < 0.5 and y == 0.0)
            ),
            "probability_margin": abs(p - 0.5),
        })
    return out


def c002a_view(rows):
    # INPUT rows already contain the unscaled C002a probability/metrics.
    return [dict(r) for r in rows]


def summarize(rows):
    stats = aggregate(rows)
    _, ece = calibration_table(rows)
    return {
        **stats,
        "expected_calibration_error_5pp_bins": ece,
    }


def select_scale(train_rows):
    candidates = []
    for scale in SCALE_CANDIDATES:
        result, _ = evaluate(train_rows, scale)
        candidates.append(result)

    # Primary criterion is Brier; log loss is deterministic tiebreaker.
    selected = min(candidates, key=lambda x: (x["brier"], x["log_loss"]))
    return selected, candidates


def write_jsonl(rows, path):
    with open(path, "w", encoding="utf-8") as f:
        for row in rows:
            f.write(json.dumps(row, separators=(",", ":")) + "\n")


def main():
    rows = load_jsonl(INPUT)
    train_rows = [r for r in rows if str(r["game_date"]) <= TRAIN_END]
    valid_rows = [r for r in rows if str(r["game_date"]) >= VALID_START]

    if not train_rows or not valid_rows:
        raise RuntimeError("C002b chronological split produced an empty partition")

    selected, candidates = select_scale(train_rows)
    selected_scale = selected["scale"]

    challenger_valid_summary, challenger_valid_rows = evaluate(
        valid_rows, selected_scale
    )

    baseline_valid_rows = baseline_view(valid_rows)
    raw_c002a_valid_rows = c002a_view(valid_rows)

    baseline_valid = summarize(baseline_valid_rows)
    raw_c002a_valid = summarize(raw_c002a_valid_rows)

    report = {
        "challenger_id": "C002b",
        "challenger_label": "starter-event-rate-v2-scaled",
        "status": "research-only",
        "production_model_changed": False,
        "sportsbook_prices_used": False,
        "purpose": (
            "Test whether C002a's pitcher talent signal was useful but over-scaled "
            "when inserted into the structural win-probability model."
        ),
        "frozen_inputs": {
            "c002a_pitcher_talent_model_refit": False,
            "c002a_event_rate_coefficients_changed": False,
            "v11_other_features_changed": False,
            "v11_weights_changed": False,
        },
        "chronological_design": {
            "scale_selection_period_end": TRAIN_END,
            "held_out_validation_period_start": VALID_START,
            "selection_games": len(train_rows),
            "held_out_games": len(valid_rows),
            "2025_late_outcomes_used_for_scale_selection": False,
        },
        "scale_selection": {
            "candidate_min": min(SCALE_CANDIDATES),
            "candidate_max": max(SCALE_CANDIDATES),
            "candidate_step": 0.05,
            "candidate_count": len(SCALE_CANDIDATES),
            "selected": selected,
            "all_candidates": candidates,
            "criterion": "minimum early-2025 Brier, log-loss tiebreaker",
        },
        "held_out_validation": {
            "baseline_BT_0088": baseline_valid,
            "raw_C002a_scale_1_0": raw_c002a_valid,
            "C002b_selected_scale": challenger_valid_summary,
            "delta_C002b_minus_baseline": {
                "brier": challenger_valid_summary["brier"] - baseline_valid["brier"],
                "log_loss": (
                    challenger_valid_summary["log_loss"]
                    - baseline_valid["log_loss"]
                ),
                "accuracy": (
                    challenger_valid_summary["accuracy"]
                    - baseline_valid["accuracy"]
                ),
                "ece_5pp_bins": (
                    challenger_valid_summary["ece_5pp_bins"]
                    - baseline_valid["expected_calibration_error_5pp_bins"]
                ),
            },
            "delta_C002b_minus_raw_C002a": {
                "brier": challenger_valid_summary["brier"] - raw_c002a_valid["brier"],
                "log_loss": (
                    challenger_valid_summary["log_loss"]
                    - raw_c002a_valid["log_loss"]
                ),
                "accuracy": (
                    challenger_valid_summary["accuracy"]
                    - raw_c002a_valid["accuracy"]
                ),
                "ece_5pp_bins": (
                    challenger_valid_summary["ece_5pp_bins"]
                    - raw_c002a_valid["expected_calibration_error_5pp_bins"]
                ),
            },
        },
        "governance": {
            "automatic_promotion_authorized": False,
            "v11_weight_change_authorized": False,
            "interpretation_rule": (
                "C002b only survives if the selected scale improves held-out late-2025 "
                "Brier/log loss versus both BT-0088 and raw C002a without material "
                "calibration degradation."
            ),
        },
    }

    Path(REPORT).write_text(json.dumps(report, indent=2), encoding="utf-8")
    write_jsonl(challenger_valid_rows, SCORED)
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
