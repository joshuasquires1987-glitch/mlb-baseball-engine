import math

from run_c001_prior_season_home_baseline import (
    apply_challenger,
    estimate_prior_season_home_intercept,
    logit,
)

def test_prior_season_intercept_uses_only_final_home_results():
    games = [
        {"home_runs": 5, "away_runs": 3},
        {"home_runs": 2, "away_runs": 4},
        {"home_runs": 3, "away_runs": 2},
    ]
    result = estimate_prior_season_home_intercept(games)
    assert result["eligible_games"] == 3
    assert result["home_wins"] == 2
    assert abs(result["home_win_rate"] - 2/3) < 1e-12
    assert abs(result["home_logit_intercept"] - logit(2/3)) < 1e-12

def test_challenger_changes_only_home_intercept_on_weighted_score():
    baseline = [{
        "game_pk": "1",
        "weighted_score": 0.20,
        "home_win_probability": 1/(1+math.exp(-0.20)),
        "home_win": 1,
        "brier": 0.1,
        "log_loss": 0.5,
        "correct_side": True,
        "probability_margin": 0.05,
    }]
    home_intercept = 0.10
    out = apply_challenger(baseline, home_intercept)
    expected_score = 0.20 - 0.004 + 0.10
    assert abs(out[0]["weighted_score"] - expected_score) < 1e-12
    assert out[0]["challenger_id"] == "C001"
