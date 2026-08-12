from run_c001_multifold_validation import score_constant_probability, summarize_home_results

def test_home_summary():
    games = [
        {"home_runs": 5, "away_runs": 2},
        {"home_runs": 1, "away_runs": 3},
        {"home_runs": 4, "away_runs": 2},
    ]
    x = summarize_home_results(games)
    assert x["n"] == 3
    assert x["home_wins"] == 2
    assert abs(x["home_win_rate"] - 2/3) < 1e-12

def test_constant_home_probability_scores_without_market_data():
    games = [
        {"home_runs": 5, "away_runs": 2},
        {"home_runs": 1, "away_runs": 3},
    ]
    x = score_constant_probability(games, 0.55)
    assert x["n"] == 2
    assert abs(x["actual_home_win_rate"] - 0.5) < 1e-12
    assert x["brier"] > 0
    assert x["log_loss"] > 0
