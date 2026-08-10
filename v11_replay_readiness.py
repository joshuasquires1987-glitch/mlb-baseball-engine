import json
from pathlib import Path

REQUIRED_COMPONENTS = (
    "starting_pitcher",
    "underlying_team_strength",
    "bullpen",
    "confirmed_lineup_offense",
    "platoon_matchup_fit",
    "defense",
    "home_field",
    "park",
    "weather",
    "travel_rest_circadian",
)

def audit_repo_contract():
    findings = {
        "required_components": list(REQUIRED_COMPONENTS),
        "production_probability_function": "run_weighted_model -> sigmoid(weighted feature sum)",
        "historical_replay_status": "not_yet_certified",
        "missing_builders": [],
        "notes": [],
    }

    expected_files = [
        "runner.py",
        "models.py",
        "v1_1.json",
        "pregame_feature_builder.py",
        "pregame_inputs.py",
        "starter_state_calculator.py",
        "team_state_calculator.py",
        "bullpen_state_calculator.py",
    ]
    for f in expected_files:
        if not Path(f).exists():
            findings["missing_builders"].append(f)

    findings["notes"].append(
        "The repo contains the v1.1 weighting/probability function and prior-only state calculators."
    )
    findings["notes"].append(
        "A certified historical replay still requires a point-in-time builder for every v1.1 feature, especially "
        "confirmed_lineup_offense, platoon_matchup_fit, home_field, park, weather, and travel_rest_circadian, "
        "all keyed to the exact historical pregame state."
    )
    findings["notes"].append(
        "Do not substitute the RC2 context features directly into v1.1 feature slots unless the production feature "
        "normalization is proven identical."
    )

    return findings

def main():
    findings=audit_repo_contract()
    Path("v11_replay_readiness_report.json").write_text(json.dumps(findings, indent=2))
    print(json.dumps(findings, indent=2))

if __name__=="__main__":
    main()
