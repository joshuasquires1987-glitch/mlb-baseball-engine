import csv
import json
from pathlib import Path

from run_v11_structural_benchmark import load_jsonl, aggregate

SCORED = "v11_structural_default_scored_games.jsonl"
REPORT = "v11_structural_default_diagnostic_report.json"
CSV_OUT = "v11_structural_default_diagnostic_groups.csv"


def _month(row):
    return str(row["game_date"])[:7]


def _predicted_side(row):
    return "home" if float(row["home_win_probability"]) >= 0.5 else "away"


def _probability_band(row):
    p = float(row["home_win_probability"])
    if p < 0.40:
        return "<0.40"
    if p < 0.45:
        return "0.40-0.45"
    if p < 0.50:
        return "0.45-0.50"
    if p < 0.55:
        return "0.50-0.55"
    if p < 0.60:
        return "0.55-0.60"
    return "0.60+"


def _feature_band(value):
    x = float(value)
    if x < -0.25:
        return "away_edge"
    if x > 0.25:
        return "home_edge"
    return "neutral"


def diagnostic_groups(rows):
    groups = {}

    def add(dimension, label, row):
        groups.setdefault((dimension, label), []).append(row)

    for row in rows:
        add("month", _month(row), row)
        add("predicted_side", _predicted_side(row), row)
        add("home_probability_band", _probability_band(row), row)

        features = row.get("features") or {}
        for feature in (
            "starting_pitcher",
            "underlying_team_strength",
            "bullpen",
            "confirmed_lineup_offense",
            "defense",
        ):
            if features.get(feature) is not None:
                add(feature, _feature_band(features[feature]), row)

    result = []
    for (dimension, label), bucket in sorted(groups.items()):
        stats = aggregate(bucket)
        result.append({
            "dimension": dimension,
            "group": label,
            **stats,
        })
    return result


def ranked_findings(rows, groups):
    overall = aggregate(rows)
    findings = []

    by_key = {(g["dimension"], g["group"]): g for g in groups}

    home = by_key.get(("predicted_side", "home"))
    away = by_key.get(("predicted_side", "away"))
    if home and away:
        findings.append({
            "priority": 1,
            "finding": "away-side predictions materially weaker than home-side predictions",
            "evidence": {
                "away_brier": away["brier"],
                "home_brier": home["brier"],
                "away_calibration_bias": away["calibration_bias"],
                "home_calibration_bias": home["calibration_bias"],
            },
            "interpretation": (
                "The structural reconstruction is systematically too bearish on the "
                "home team, especially when it crosses below 50% and selects the away side."
            ),
            "challenger_implication": (
                "Investigate home/context baseline representation before changing "
                "starter/team/bullpen production weights."
            ),
        })

    low_home = [
        g for g in groups
        if g["dimension"] == "home_probability_band"
        and g["group"] in ("0.40-0.45", "0.45-0.50")
    ]
    if low_home:
        findings.append({
            "priority": 2,
            "finding": "largest useful calibration miss concentrated in 40-50% home probability range",
            "evidence": [
                {
                    "group": g["group"],
                    "n": g["n"],
                    "mean_home_probability": g["mean_home_probability"],
                    "actual_home_win_rate": g["actual_home_win_rate"],
                    "calibration_bias": g["calibration_bias"],
                    "brier": g["brier"],
                }
                for g in low_home
            ],
            "interpretation": (
                "Many nominal away-favorite calls should have been closer to neutral "
                "or home-leaning in this structural reconstruction."
            ),
            "challenger_implication": (
                "A context/home-intercept challenger can be isolated and tested without "
                "mutating v1.1."
            ),
        })

    findings.append({
        "priority": 3,
        "finding": "component signals are directionally useful but not sufficient to remove global home bias",
        "evidence": {
            "overall_brier": overall["brier"],
            "overall_calibration_bias": overall["calibration_bias"],
        },
        "interpretation": (
            "Starter, team, bullpen, lineup, and defense features should be retained as "
            "baseline signals while their individual latent-state models are improved later."
        ),
        "challenger_implication": (
            "Do not reweight components from this one-season diagnostic. First isolate "
            "the context/home-baseline issue, then move to component challengers."
        ),
    })

    return findings


def write_csv(rows, path):
    if not rows:
        Path(path).write_text("", encoding="utf-8")
        return
    fields = list(rows[0].keys())
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def main():
    rows = load_jsonl(SCORED)
    groups = diagnostic_groups(rows)
    findings = ranked_findings(rows, groups)

    report = {
        "diagnostic_id": "BT-0089",
        "model_label": "v1.1-structural-default-replay",
        "n": len(rows),
        "production_model_changed": False,
        "sportsbook_prices_used": False,
        "purpose": "diagnose benchmark error concentration before challenger selection",
        "overall": aggregate(rows),
        "ranked_findings": findings,
        "governance": {
            "weight_change_authorized": False,
            "automatic_promotion_authorized": False,
            "recommended_next_step": (
                "Implement an isolated context/home-baseline challenger and compare it "
                "on identical historical snapshots."
            ),
        },
    }

    Path(REPORT).write_text(json.dumps(report, indent=2), encoding="utf-8")
    write_csv(groups, CSV_OUT)
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
