import math

from run_v11_structural_benchmark import (
    aggregate,
    build_report,
    calibration_table,
    score_ledger,
)


def sample_ledger():
    return [
        {"game_pk": "1", "home_win_probability": 0.70, "features": {"starting_pitcher": 0.5}},
        {"game_pk": "2", "home_win_probability": 0.40, "features": {"starting_pitcher": -0.5}},
        {"game_pk": "3", "home_win_probability": 0.55, "features": {"starting_pitcher": 0.0}},
        {"game_pk": "4", "home_win_probability": 0.45, "features": {"starting_pitcher": 0.0}},
    ]


def sample_outcomes():
    return {
        "1": {"home_runs": 5.0, "away_runs": 2.0},
        "2": {"home_runs": 2.0, "away_runs": 3.0},
        "3": {"home_runs": 1.0, "away_runs": 4.0},
        "4": {"home_runs": 4.0, "away_runs": 3.0},
    }


def test_score_ledger_scores_all_available_games():
    scored, exclusions = score_ledger(sample_ledger(), sample_outcomes())
    assert len(scored) == 4
    assert exclusions == []
    assert scored[0]["home_win"] == 1
    assert scored[1]["home_win"] == 0


def test_aggregate_brier_and_logloss_are_correct():
    scored, _ = score_ledger(sample_ledger(), sample_outcomes())
    stats = aggregate(scored)

    expected_brier = ((0.70-1)**2 + (0.40-0)**2 + (0.55-0)**2 + (0.45-1)**2) / 4
    assert abs(stats["brier"] - expected_brier) < 1e-12

    expected_ll = (
        -math.log(0.70)
        -math.log(0.60)
        -math.log(0.45)
        -math.log(0.45)
    ) / 4
    assert abs(stats["log_loss"] - expected_ll) < 1e-12


def test_missing_outcome_is_audited_not_silently_dropped():
    ledger = sample_ledger()
    outcomes = sample_outcomes()
    del outcomes["4"]

    scored, exclusions = score_ledger(ledger, outcomes)

    assert len(scored) == 3
    assert exclusions == [{"game_pk": "4", "reason": "final-outcome-missing"}]


def test_calibration_table_covers_every_scored_game():
    scored, _ = score_ledger(sample_ledger(), sample_outcomes())
    table, ece = calibration_table(scored, width=0.05)

    assert sum(row["n"] for row in table) == 4
    assert 0.0 <= ece <= 1.0


def test_report_keeps_sportsbook_layer_out():
    ledger = sample_ledger()
    scored, exclusions = score_ledger(ledger, sample_outcomes())
    report = build_report(ledger, scored, exclusions)

    assert report["sportsbook_prices_used"] is False
    assert report["probability_source"] == "independent-baseball-model-only"
    assert report["scored_games"] == 4
