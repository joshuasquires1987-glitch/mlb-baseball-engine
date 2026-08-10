import pytest
from context_calibration_schema import validate_training_row
from context_calibration_gate import calibration_gate
from context_score_transform import scores_from_calibrated_features

def row():
    return {
        "game_id":"1","game_date":"2026-01-01","home_win":1,
        "park_factor_delta":0.2,
        "temperature_delta_f":5,
        "wind_out_mph":8,
        "wind_in_mph":0,
        "travel_timezone_delta_hours":-1,
        "rest_days_delta":1,
        "platoon_lineup_delta":0.3,
    }

def coefs():
    return {
        "park_factor_delta":0.3,
        "temperature_delta_f":0.01,
        "wind_out_mph":0.02,
        "wind_in_mph":-0.02,
        "travel_timezone_delta_hours":0.1,
        "rest_days_delta":0.15,
        "platoon_lineup_delta":0.4,
    }

def test_training_schema():
    assert validate_training_row(row())

def test_gate_requires_real_sample_and_holdout_improvement():
    q=calibration_gate(500,150,coefs(),-0.002)
    assert q["eligible_for_shadow_review"]
    assert q["production_promotion_allowed"] is False

def test_gate_rejects_small_sample():
    assert not calibration_gate(50,20,coefs(),-0.01)["eligible_for_shadow_review"]

def test_gate_rejects_no_improvement():
    assert not calibration_gate(1000,300,coefs(),0.001)["eligible_for_shadow_review"]

def test_scores_only_accept_complete_calibrated_features():
    s=scores_from_calibrated_features(row(),coefs())
    assert set(("park_score","weather_score","travel_rest_score","platoon_score")) <= set(s)
    bad=row(); del bad["wind_out_mph"]
    with pytest.raises(ValueError):
        scores_from_calibrated_features(bad,coefs())
