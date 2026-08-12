import json
import math
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
from pathlib import Path

import numpy as np

from feature_normalization import advantage
from mlb_bulk_schedule_runtime import completed_games_chunked
from mlb_historical_timecode_runtime import fetch_json
from run_v11_structural_benchmark import aggregate, calibration_table, load_jsonl
from run_v11_structural_default_replay import load_snapshots
from starter_state_calculator import StarterStateCalculator
from state_utils import bounded_score, half_life_weight
from v11_historical_feed_parser import parse_final_feed
from v11_structural_replay import sigmoid

BASE = "https://statsapi.mlb.com/api/v1.1"
MAX_WORKERS = 16

BASELINE_SCORED = "v11_structural_default_scored_games.jsonl"
SNAPSHOTS = "pregame_lineup_snapshots.jsonl"

REPORT = "c002a_starter_talent_v2_report.json"
SCORED = "c002a_starter_talent_v2_scored_games.jsonl"

SP_WEIGHT = 0.25
EPS = 1e-15

# Hyperparameters are selected on a chronological 2024 train/validation split.
HALF_LIFE_CANDIDATES = [90.0, 180.0, 365.0]
PRIOR_BF_CANDIDATES = [150.0, 350.0, 700.0]
RIDGE_CANDIDATES = [0.1, 1.0, 10.0, 100.0]

INTERNAL_TRAIN_END = "2024-06-30"
INTERNAL_VALID_START = "2024-07-01"
INTERNAL_VALID_END = "2024-09-29"


def _dt(v):
    return datetime.fromisoformat(str(v).replace("Z", "+00:00"))


def final_feed_url(game_pk):
    return f"{BASE}/game/{game_pk}/feed/live"


def fetch_parse(game):
    return parse_final_feed(game, fetch_json(final_feed_url(game["game_pk"])))


def fetch_parsed_games():
    games, _ = completed_games_chunked("2024-03-20", "2025-09-28")
    snapshots = load_snapshots(SNAPSHOTS)
    target_pks = {str(x["game_pk"]) for x in snapshots}
    wanted = [
        g for g in games
        if str(g["game_date"]).startswith("2024")
        or str(g["game_pk"]) in target_pks
    ]

    parsed, failures = [], []
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as pool:
        futures = {pool.submit(fetch_parse, g): g for g in wanted}
        for i, fut in enumerate(as_completed(futures), 1):
            g = futures[fut]
            try:
                parsed.append(fut.result())
            except Exception as e:
                failures.append({
                    "game_pk": str(g["game_pk"]),
                    "reason": f"{type(e).__name__}:{str(e)[:200]}",
                })
            if i % 250 == 0 or i == len(futures):
                print(
                    f"C002 feeds={i}/{len(futures)} parsed={len(parsed)} "
                    f"failures={len(failures)}",
                    flush=True,
                )
    if failures:
        raise RuntimeError(f"C002 feed failures: {failures[:5]}")
    return parsed, snapshots


def starter_appearances(parsed_games, season):
    rows = []
    for g in parsed_games:
        if not str(g["game_date"]).startswith(str(season)):
            continue
        for p in g.get("pitching_rows", []):
            if int(p.get("p_gs", 0)) != 1:
                continue
            rows.append({
                "game_pk": str(g["game_pk"]),
                "game_date": str(g["game_date"]),
                "game_time_utc": g["game_time_utc"],
                "pitcher_id": str(p["id"]),
                "batters_faced": float(p.get("p_bfp", 0)),
                "runs_allowed": float(p.get("p_r", 0)),
                "outs": float(p.get("p_ipouts", 0)),
                "strikeouts": float(p.get("p_so", 0)),
                "walks": float(p.get("p_bb", 0)),
                "home_runs": float(p.get("p_hr", 0)),
                "hit_batters": float(p.get("p_hbp", 0)),
            })
    return sorted(rows, key=lambda r: (r["game_time_utc"], r["game_pk"], r["pitcher_id"]))


def population_rates(rows):
    bf = sum(r["batters_faced"] for r in rows)
    if bf <= 0:
        raise ValueError("population BF must be positive")
    return {
        "k": sum(r["strikeouts"] for r in rows) / bf,
        "bb": sum(r["walks"] for r in rows) / bf,
        "hr": sum(r["home_runs"] for r in rows) / bf,
        "hbp": sum(r["hit_batters"] for r in rows) / bf,
        "ra": sum(r["runs_allowed"] for r in rows) / bf,
    }


def shrunk_event_features(history, cutoff, priors, half_life_days, prior_bf):
    cutoff = _dt(cutoff)
    sums = {
        "bf": 0.0,
        "k": 0.0,
        "bb": 0.0,
        "hr": 0.0,
        "hbp": 0.0,
    }
    starts_prior = 0
    for r in history:
        d = _dt(r["game_time_utc"])
        if d >= cutoff:
            continue
        starts_prior += 1
        age = max(0, (cutoff - d).days)
        w = half_life_weight(age, half_life_days)
        sums["bf"] += r["batters_faced"] * w
        sums["k"] += r["strikeouts"] * w
        sums["bb"] += r["walks"] * w
        sums["hr"] += r["home_runs"] * w
        sums["hbp"] += r["hit_batters"] * w

    bf = sums["bf"]
    denom = bf + prior_bf
    rates = {
        "k": (sums["k"] + prior_bf * priors["k"]) / denom,
        "bb": (sums["bb"] + prior_bf * priors["bb"]) / denom,
        "hr": (sums["hr"] + prior_bf * priors["hr"]) / denom,
        "hbp": (sums["hbp"] + prior_bf * priors["hbp"]) / denom,
    }

    # Deviations from population priors. Positive K is good; positive BB/HR/HBP bad.
    x = np.array([
        rates["k"] - priors["k"],
        rates["bb"] - priors["bb"],
        rates["hr"] - priors["hr"],
        rates["hbp"] - priors["hbp"],
    ], dtype=float)
    return x, rates, starts_prior, bf


def build_next_start_dataset(rows, priors, half_life_days, prior_bf):
    by_pitcher = defaultdict(list)
    X, y, meta = [], [], []

    # Same-day starts are evaluated before adding that day's observations.
    by_day = defaultdict(list)
    for r in rows:
        by_day[r["game_date"]].append(r)

    for day in sorted(by_day):
        for r in by_day[day]:
            if r["batters_faced"] <= 0:
                continue
            history = by_pitcher[r["pitcher_id"]]
            x, rates, starts_prior, eff_bf = shrunk_event_features(
                history, r["game_time_utc"], priors, half_life_days, prior_bf
            )
            if starts_prior > 0:
                X.append(x)
                y.append(r["runs_allowed"] / r["batters_faced"])
                meta.append({
                    "game_date": r["game_date"],
                    "pitcher_id": r["pitcher_id"],
                    "starts_prior": starts_prior,
                    "effective_bf": eff_bf,
                    "rates": rates,
                    "row": r,
                    "history": list(history),
                })
        for r in by_day[day]:
            by_pitcher[r["pitcher_id"]].append(r)

    return np.asarray(X, dtype=float), np.asarray(y, dtype=float), meta


def fit_ridge(X, y, ridge_lambda):
    if len(X) == 0:
        raise ValueError("empty training matrix")
    means = X.mean(axis=0)
    scales = X.std(axis=0)
    scales[scales < 1e-12] = 1.0
    Z = (X - means) / scales
    A = np.column_stack([np.ones(len(Z)), Z])
    penalty = np.eye(A.shape[1]) * float(ridge_lambda)
    penalty[0, 0] = 0.0
    beta = np.linalg.solve(A.T @ A + penalty, A.T @ y)
    return {
        "intercept": float(beta[0]),
        "coef": beta[1:].astype(float),
        "means": means.astype(float),
        "scales": scales.astype(float),
        "ridge_lambda": float(ridge_lambda),
    }


def predict(model, X):
    X = np.atleast_2d(np.asarray(X, dtype=float))
    Z = (X - model["means"]) / model["scales"]
    return model["intercept"] + Z @ model["coef"]


def rmse(y, pred):
    return float(np.sqrt(np.mean((np.asarray(y) - np.asarray(pred)) ** 2)))


def baseline_next_start_predictions(meta, league_ra):
    calc = StarterStateCalculator(league_runs_per_bf=league_ra)
    preds = []
    for m in meta:
        history = [{
            "date": r["game_time_utc"],
            "batters_faced": r["batters_faced"],
            "runs_allowed": r["runs_allowed"],
            "outs": r["outs"],
        } for r in m["history"]]
        state = calc.calculate(history, m["row"]["game_time_utc"])
        preds.append(float(state.get("runs_per_bf", league_ra)))
    return np.asarray(preds, dtype=float)


def select_hyperparameters(rows_2024):
    training_population = [
        r for r in rows_2024 if r["game_date"] <= INTERNAL_TRAIN_END
    ]
    priors = population_rates(training_population)

    candidates = []
    for half_life in HALF_LIFE_CANDIDATES:
        for prior_bf in PRIOR_BF_CANDIDATES:
            X, y, meta = build_next_start_dataset(
                rows_2024, priors, half_life, prior_bf
            )
            train_idx = [
                i for i, m in enumerate(meta)
                if m["game_date"] <= INTERNAL_TRAIN_END
            ]
            valid_idx = [
                i for i, m in enumerate(meta)
                if INTERNAL_VALID_START <= m["game_date"] <= INTERNAL_VALID_END
            ]
            if not train_idx or not valid_idx:
                continue

            X_train, y_train = X[train_idx], y[train_idx]
            X_valid, y_valid = X[valid_idx], y[valid_idx]

            for ridge_lambda in RIDGE_CANDIDATES:
                model = fit_ridge(X_train, y_train, ridge_lambda)
                pred = predict(model, X_valid)
                candidates.append({
                    "half_life_days": half_life,
                    "prior_bf": prior_bf,
                    "ridge_lambda": ridge_lambda,
                    "validation_rmse": rmse(y_valid, pred),
                    "train_n": len(train_idx),
                    "validation_n": len(valid_idx),
                })

    if not candidates:
        raise RuntimeError("no C002 hyperparameter candidates evaluated")
    return min(candidates, key=lambda x: x["validation_rmse"]), candidates


def fit_final_2024_model(rows_2024, selected):
    priors = population_rates(rows_2024)
    X, y, meta = build_next_start_dataset(
        rows_2024,
        priors,
        selected["half_life_days"],
        selected["prior_bf"],
    )
    model = fit_ridge(X, y, selected["ridge_lambda"])
    return priors, model, X, y, meta


def model_json(model):
    return {
        "intercept": model["intercept"],
        "coef": [float(x) for x in model["coef"]],
        "means": [float(x) for x in model["means"]],
        "scales": [float(x) for x in model["scales"]],
        "ridge_lambda": model["ridge_lambda"],
        "feature_order": ["K_rate_delta", "BB_rate_delta", "HR_rate_delta", "HBP_rate_delta"],
    }


def c002_talent_score(history, cutoff, priors, selected, model):
    if not history:
        return 0.0, {
            "starts_prior": 0,
            "predicted_ra_per_bf": priors["ra"],
            "data_quality": "prior-only-default",
        }
    x, rates, starts_prior, eff_bf = shrunk_event_features(
        history,
        cutoff,
        priors,
        selected["half_life_days"],
        selected["prior_bf"],
    )
    pred_ra = float(predict(model, x)[0])
    # Keep transformation compatible with the structural starter score scale.
    score = bounded_score(
        pred_ra,
        priors["ra"],
        max(priors["ra"] * 0.20, 1e-6),
        invert=True,
    )
    return float(score), {
        "starts_prior": starts_prior,
        "effective_bf": eff_bf,
        "predicted_ra_per_bf": pred_ra,
        "rates": rates,
    }


def build_c002_game_scores(parsed_games, snapshots, priors, selected, model):
    state = defaultdict(list)
    warmup = [
        r for r in starter_appearances(parsed_games, 2024)
    ]
    for r in warmup:
        state[r["pitcher_id"]].append(r)

    finals_2025 = {
        str(g["game_pk"]): g
        for g in parsed_games
        if str(g["game_date"]).startswith("2025")
    }

    by_date = defaultdict(list)
    for s in snapshots:
        by_date[str(s["game_date"])].append(s)

    scores = {}
    diagnostics = {}
    for day in sorted(by_date):
        targets = sorted(
            by_date[day],
            key=lambda x: (x["game_time_utc"], str(x["game_pk"])),
        )
        for s in targets:
            hp = str(s["home_probable_starter_id"])
            ap = str(s["away_probable_starter_id"])
            h_score, h_diag = c002_talent_score(
                state.get(hp, []), s["game_time_utc"], priors, selected, model
            )
            a_score, a_diag = c002_talent_score(
                state.get(ap, []), s["game_time_utc"], priors, selected, model
            )
            game_pk = str(s["game_pk"])
            scores[game_pk] = advantage(h_score, a_score)
            diagnostics[game_pk] = {
                "home": h_diag,
                "away": a_diag,
                "home_talent_score": h_score,
                "away_talent_score": a_score,
            }

        # Preserve conservative baseline replay rule: add results after all same-day forecasts.
        for s in targets:
            g = finals_2025.get(str(s["game_pk"]))
            if g is None:
                continue
            for p in g.get("pitching_rows", []):
                if int(p.get("p_gs", 0)) != 1:
                    continue
                state[str(p["id"])].append({
                    "game_pk": str(g["game_pk"]),
                    "game_date": str(g["game_date"]),
                    "game_time_utc": g["game_time_utc"],
                    "pitcher_id": str(p["id"]),
                    "batters_faced": float(p.get("p_bfp", 0)),
                    "runs_allowed": float(p.get("p_r", 0)),
                    "outs": float(p.get("p_ipouts", 0)),
                    "strikeouts": float(p.get("p_so", 0)),
                    "walks": float(p.get("p_bb", 0)),
                    "home_runs": float(p.get("p_hr", 0)),
                    "hit_batters": float(p.get("p_hbp", 0)),
                })
    return scores, diagnostics


def apply_to_baseline(baseline_rows, c002_scores, diagnostics):
    out = []
    missing = []
    for r in baseline_rows:
        game_pk = str(r["game_pk"])
        if game_pk not in c002_scores:
            missing.append(game_pk)
            continue
        baseline_sp = float(r["features"]["starting_pitcher"])
        challenger_sp = float(c002_scores[game_pk])
        score = (
            float(r["weighted_score"])
            - SP_WEIGHT * baseline_sp
            + SP_WEIGHT * challenger_sp
        )
        p = sigmoid(score)
        y = float(r["home_win"])
        pp = min(1.0 - EPS, max(EPS, p))
        brier = (p - y) ** 2
        ll = -(y * math.log(pp) + (1.0 - y) * math.log(1.0 - pp))
        correct = (p >= 0.5 and y == 1.0) or (p < 0.5 and y == 0.0)
        out.append({
            **r,
            "challenger_id": "C002a",
            "challenger_label": "starter-event-rate-v2",
            "baseline_home_win_probability": float(r["home_win_probability"]),
            "baseline_brier": float(r["brier"]),
            "baseline_log_loss": float(r["log_loss"]),
            "baseline_starting_pitcher_feature": baseline_sp,
            "c002_starting_pitcher_feature": challenger_sp,
            "c002_starter_diagnostics": diagnostics[game_pk],
            "weighted_score": score,
            "home_win_probability": p,
            "away_win_probability": 1.0 - p,
            "brier": brier,
            "log_loss": ll,
            "correct_side": bool(correct),
            "probability_margin": abs(p - 0.5),
        })
    if missing:
        raise RuntimeError(f"missing C002 scores for {len(missing)} games: {missing[:5]}")
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
            "ece_5pp_bins": chall_ece - base_ece,
        },
    }


def write_jsonl(rows, path):
    with open(path, "w", encoding="utf-8") as f:
        for row in rows:
            f.write(json.dumps(row, separators=(",", ":")) + "\n")


def main():
    parsed, snapshots = fetch_parsed_games()
    starts_2024 = starter_appearances(parsed, 2024)

    selected, candidates = select_hyperparameters(starts_2024)
    priors, model, X_2024, y_2024, meta_2024 = fit_final_2024_model(
        starts_2024, selected
    )

    # Diagnostic: next-start prediction on the untouched 2025 starter appearances.
    starts_2025 = starter_appearances(parsed, 2025)
    X_2025, y_2025, meta_2025 = build_next_start_dataset(
        starts_2025,
        priors,
        selected["half_life_days"],
        selected["prior_bf"],
    )
    c002_next_start_pred = predict(model, X_2025)
    baseline_next_start_pred = baseline_next_start_predictions(
        meta_2025, priors["ra"]
    )

    c002_scores, diagnostics = build_c002_game_scores(
        parsed, snapshots, priors, selected, model
    )
    baseline_rows = load_jsonl(BASELINE_SCORED)
    challenger_rows = apply_to_baseline(
        baseline_rows, c002_scores, diagnostics
    )
    comparison = compare(baseline_rows, challenger_rows)

    report = {
        "challenger_id": "C002a",
        "challenger_label": "starter-event-rate-v2",
        "status": "research-only",
        "production_model_changed": False,
        "sportsbook_prices_used": False,
        "spec_alignment": {
            "posterior_event_family": ["K", "BB", "HR", "HBP"],
            "contact_quality_statcast_included": False,
            "reason_contact_quality_deferred": (
                "BT-0090 supplies boxscore event primitives; Statcast contact-quality "
                "inputs remain a later C002 extension."
            ),
            "recency_weighted": True,
            "shrinkage_used": True,
            "hyperparameters_selected_on_2024_only": True,
            "2025_outcomes_used_for_fitting": False,
        },
        "training": {
            "season": 2024,
            "internal_train_end": INTERNAL_TRAIN_END,
            "internal_validation_start": INTERNAL_VALID_START,
            "internal_validation_end": INTERNAL_VALID_END,
            "selected_hyperparameters": selected,
            "candidate_count": len(candidates),
            "population_priors": priors,
            "final_training_rows": len(y_2024),
            "fitted_model": model_json(model),
        },
        "next_start_validation_2025": {
            "n": len(y_2025),
            "baseline_runs_per_bf_rmse": rmse(y_2025, baseline_next_start_pred),
            "c002_runs_per_bf_rmse": rmse(y_2025, c002_next_start_pred),
            "delta_c002_minus_baseline_rmse": (
                rmse(y_2025, c002_next_start_pred)
                - rmse(y_2025, baseline_next_start_pred)
            ),
        },
        "game_probability_validation_2025": {
            "n": len(challenger_rows),
            "identical_games_to_BT_0088": len(challenger_rows) == len(baseline_rows),
            "comparison": comparison,
        },
        "governance": {
            "automatic_promotion_authorized": False,
            "v11_weight_change_authorized": False,
            "decision_note": (
                "C002a changes only the starting-pitcher feature in a research challenger. "
                "Even a positive result requires multi-season validation and subgroup review."
            ),
        },
    }

    Path(REPORT).write_text(json.dumps(report, indent=2), encoding="utf-8")
    write_jsonl(challenger_rows, SCORED)
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
