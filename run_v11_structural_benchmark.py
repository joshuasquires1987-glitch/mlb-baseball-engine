import csv
import json
import math
from pathlib import Path

from mlb_bulk_schedule_runtime import completed_games_chunked

LEDGER = "v11_structural_default_probability_ledger.jsonl"
SCORED = "v11_structural_default_scored_games.jsonl"
REPORT = "v11_structural_default_benchmark_report.json"
CALIBRATION = "v11_structural_default_calibration.csv"
SUBGROUPS = "v11_structural_default_subgroups.csv"

START = "2025-03-27"
END = "2025-09-28"
EPS = 1e-15


def load_jsonl(path):
    rows = []
    with open(path, "r", encoding="utf-8") as f:
        for line_number, line in enumerate(f, 1):
            if not line.strip():
                continue
            row = json.loads(line)
            if "game_pk" not in row or "home_win_probability" not in row:
                raise ValueError(
                    f"invalid ledger row on line {line_number}: "
                    "game_pk/home_win_probability required"
                )
            rows.append(row)
    return rows


def outcome_map(games):
    out = {}
    for g in games:
        hr = g.get("home_runs")
        ar = g.get("away_runs")
        if hr is None or ar is None:
            continue
        out[str(g["game_pk"])] = {
            "home_runs": float(hr),
            "away_runs": float(ar),
        }
    return out


def score_ledger(ledger_rows, outcomes):
    scored = []
    exclusions = []

    for row in ledger_rows:
        game_pk = str(row["game_pk"])
        result = outcomes.get(game_pk)
        if result is None:
            exclusions.append({
                "game_pk": game_pk,
                "reason": "final-outcome-missing",
            })
            continue

        hr = result["home_runs"]
        ar = result["away_runs"]
        if hr == ar:
            exclusions.append({
                "game_pk": game_pk,
                "reason": "final-score-tie",
                "home_runs": hr,
                "away_runs": ar,
            })
            continue

        p = float(row["home_win_probability"])
        if not math.isfinite(p) or not (0.0 < p < 1.0):
            exclusions.append({
                "game_pk": game_pk,
                "reason": "invalid-probability",
                "home_win_probability": p,
            })
            continue

        y = 1.0 if hr > ar else 0.0
        p_log = min(1.0 - EPS, max(EPS, p))
        brier = (p - y) ** 2
        log_loss = -(y * math.log(p_log) + (1.0 - y) * math.log(1.0 - p_log))
        predicted_home = p >= 0.5
        correct = (predicted_home and y == 1.0) or ((not predicted_home) and y == 0.0)

        scored.append({
            **row,
            "home_runs": hr,
            "away_runs": ar,
            "home_win": int(y),
            "brier": brier,
            "log_loss": log_loss,
            "correct_side": bool(correct),
            "probability_margin": abs(p - 0.5),
        })

    return scored, exclusions


def _quantile(values, q):
    if not values:
        return None
    xs = sorted(float(x) for x in values)
    if len(xs) == 1:
        return xs[0]
    pos = (len(xs) - 1) * q
    lo = int(math.floor(pos))
    hi = int(math.ceil(pos))
    if lo == hi:
        return xs[lo]
    frac = pos - lo
    return xs[lo] * (1.0 - frac) + xs[hi] * frac


def aggregate(rows):
    n = len(rows)
    if n == 0:
        return {
            "n": 0,
            "brier": None,
            "log_loss": None,
            "accuracy": None,
            "mean_home_probability": None,
            "actual_home_win_rate": None,
            "calibration_bias": None,
        }

    ps = [float(r["home_win_probability"]) for r in rows]
    ys = [float(r["home_win"]) for r in rows]
    brier = sum(float(r["brier"]) for r in rows) / n
    log_loss = sum(float(r["log_loss"]) for r in rows) / n
    accuracy = sum(bool(r["correct_side"]) for r in rows) / n
    mean_p = sum(ps) / n
    actual = sum(ys) / n

    return {
        "n": n,
        "brier": brier,
        "brier_skill_vs_50pct": 1.0 - (brier / 0.25),
        "log_loss": log_loss,
        "log_loss_improvement_vs_50pct": math.log(2.0) - log_loss,
        "accuracy": accuracy,
        "mean_home_probability": mean_p,
        "actual_home_win_rate": actual,
        "calibration_bias": mean_p - actual,
        "probability_min": min(ps),
        "probability_p05": _quantile(ps, 0.05),
        "probability_p25": _quantile(ps, 0.25),
        "probability_median": _quantile(ps, 0.50),
        "probability_p75": _quantile(ps, 0.75),
        "probability_p95": _quantile(ps, 0.95),
        "probability_max": max(ps),
        "mean_probability_margin": sum(abs(p - 0.5) for p in ps) / n,
    }


def calibration_table(rows, width=0.05):
    bins = {}
    for r in rows:
        p = float(r["home_win_probability"])
        idx = min(int(p / width), int(1.0 / width) - 1)
        lo = idx * width
        hi = lo + width
        key = (round(lo, 10), round(hi, 10))
        bins.setdefault(key, []).append(r)

    result = []
    total = len(rows)
    ece = 0.0
    for (lo, hi), bucket in sorted(bins.items()):
        stats = aggregate(bucket)
        gap = stats["mean_home_probability"] - stats["actual_home_win_rate"]
        ece += (len(bucket) / total) * abs(gap) if total else 0.0
        result.append({
            "bin_low": lo,
            "bin_high": hi,
            "n": len(bucket),
            "mean_probability": stats["mean_home_probability"],
            "actual_home_win_rate": stats["actual_home_win_rate"],
            "calibration_gap": gap,
            "brier": stats["brier"],
            "log_loss": stats["log_loss"],
        })
    return result, ece


def _probability_band(p):
    cuts = [
        (0.00, 0.40, "0.00-0.40"),
        (0.40, 0.45, "0.40-0.45"),
        (0.45, 0.50, "0.45-0.50"),
        (0.50, 0.55, "0.50-0.55"),
        (0.55, 0.60, "0.55-0.60"),
        (0.60, 1.01, "0.60-1.00"),
    ]
    for lo, hi, label in cuts:
        if lo <= p < hi:
            return label
    return "other"


def _confidence_band(p):
    m = abs(p - 0.5)
    if m < 0.025:
        return "<2.5pp"
    if m < 0.075:
        return "2.5-7.5pp"
    if m < 0.15:
        return "7.5-15pp"
    return "15pp+"


def subgroup_rows(rows):
    groups = {}

    def add(dimension, label, row):
        groups.setdefault((dimension, label), []).append(row)

    for r in rows:
        p = float(r["home_win_probability"])
        add("predicted_side", "home_favorite" if p >= 0.5 else "away_favorite", r)
        add("home_probability_band", _probability_band(p), r)
        add("confidence_margin", _confidence_band(p), r)

        features = r.get("features") or {}
        sp = features.get("starting_pitcher")
        if sp is not None:
            sp = float(sp)
            if sp < -0.25:
                label = "away_SP_edge"
            elif sp > 0.25:
                label = "home_SP_edge"
            else:
                label = "SP_neutral"
            add("starting_pitcher_feature", label, r)

    out = []
    for (dimension, label), bucket in sorted(groups.items()):
        stats = aggregate(bucket)
        out.append({
            "dimension": dimension,
            "group": label,
            **stats,
        })
    return out


def write_jsonl(rows, path):
    with open(path, "w", encoding="utf-8") as f:
        for row in rows:
            f.write(json.dumps(row, separators=(",", ":")) + "\n")


def write_csv(rows, path):
    if not rows:
        Path(path).write_text("", encoding="utf-8")
        return
    fields = list(rows[0].keys())
    with open(path, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def build_report(ledger_rows, scored, exclusions):
    overall = aggregate(scored)
    calibration, ece = calibration_table(scored)
    subgroups = subgroup_rows(scored)

    overall["expected_calibration_error_5pp_bins"] = ece

    return {
        "benchmark_id": "BT-0088",
        "model_label": "v1.1-structural-default-replay",
        "exact_historical_v11_probability": False,
        "probability_source": "independent-baseball-model-only",
        "sportsbook_prices_used": False,
        "ledger_rows": len(ledger_rows),
        "scored_games": len(scored),
        "excluded_games": len(exclusions),
        "coverage_rate": len(scored) / len(ledger_rows) if ledger_rows else 0.0,
        "overall": overall,
        "calibration": calibration,
        "subgroups": subgroups,
        "exclusion_examples": exclusions[:50],
        "notes": [
            "This benchmark scores every eligible reconstructed game, not bets only.",
            "The structural replay uses documented default context values where exact historical v1.1 inputs are unavailable.",
            "No sportsbook price, CLV, or betting result enters probability construction or benchmark scoring.",
            "Brier and log loss are primary model-quality metrics; accuracy is secondary.",
        ],
    }


def main():
    ledger_rows = load_jsonl(LEDGER)

    games, chunk_stats = completed_games_chunked(START, END)
    outcomes = outcome_map(games)
    scored, exclusions = score_ledger(ledger_rows, outcomes)
    report = build_report(ledger_rows, scored, exclusions)
    report["outcome_schedule_chunks"] = chunk_stats
    report["final_outcomes_available"] = len(outcomes)

    if report["coverage_rate"] < 0.98:
        raise RuntimeError(
            f"benchmark outcome coverage too low: {report['coverage_rate']:.3%}"
        )

    write_jsonl(scored, SCORED)
    write_csv(report["calibration"], CALIBRATION)
    write_csv(report["subgroups"], SUBGROUPS)
    Path(REPORT).write_text(json.dumps(report, indent=2), encoding="utf-8")

    print(json.dumps({
        "benchmark_id": report["benchmark_id"],
        "ledger_rows": report["ledger_rows"],
        "scored_games": report["scored_games"],
        "excluded_games": report["excluded_games"],
        "coverage_rate": report["coverage_rate"],
        "overall": report["overall"],
    }, indent=2))


if __name__ == "__main__":
    main()
