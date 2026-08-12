import math

from run_c002b_starter_signal_scale import (
    baseline_score,
    score_with_scale,
    select_scale,
)


def row():
    baseline_score_value = 0.20
    baseline_sp = 0.40
    c002_sp = 0.80
    c002a_score = baseline_score_value - 0.25 * baseline_sp + 0.25 * c002_sp
    return {
        "game_pk": "1",
        "game_date": "2025-04-01",
        "weighted_score": c002a_score,
        "baseline_starting_pitcher_feature": baseline_sp,
        "c002_starting_pitcher_feature": c002_sp,
        "baseline_home_win_probability": 1 / (1 + math.exp(-baseline_score_value)),
        "home_win_probability": 1 / (1 + math.exp(-c002a_score)),
        "home_win": 1,
        "brier": 0.1,
        "log_loss": 0.5,
        "correct_side": True,
        "probability_margin": 0.1,
    }


def test_baseline_score_is_recovered_exactly():
    assert abs(baseline_score(row()) - 0.20) < 1e-12


def test_scale_zero_removes_starter_component_entirely():
    r = row()
    out = score_with_scale(r, 0.0)
    expected = 0.20 - 0.25 * 0.40
    assert abs(out["weighted_score"] - expected) < 1e-12


def test_scale_one_reproduces_raw_c002a_score():
    r = row()
    out = score_with_scale(r, 1.0)
    assert abs(out["weighted_score"] - r["weighted_score"]) < 1e-12


def test_scale_selection_returns_candidate():
    rows = [row(), {**row(), "game_pk": "2", "home_win": 0}]
    selected, candidates = select_scale(rows)
    assert selected in candidates
    assert 0.0 <= selected["scale"] <= 1.5
