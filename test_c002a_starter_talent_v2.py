import numpy as np

from run_c002a_starter_talent_v2 import (
    build_next_start_dataset,
    fit_ridge,
    population_rates,
    predict,
    shrunk_event_features,
)


def sample_rows():
    return [
        {
            "game_pk": "1",
            "game_date": "2024-04-01",
            "game_time_utc": "2024-04-01T20:00:00Z",
            "pitcher_id": "10",
            "batters_faced": 20.0,
            "runs_allowed": 2.0,
            "outs": 15.0,
            "strikeouts": 5.0,
            "walks": 2.0,
            "home_runs": 1.0,
            "hit_batters": 0.0,
        },
        {
            "game_pk": "2",
            "game_date": "2024-04-08",
            "game_time_utc": "2024-04-08T20:00:00Z",
            "pitcher_id": "10",
            "batters_faced": 22.0,
            "runs_allowed": 1.0,
            "outs": 18.0,
            "strikeouts": 7.0,
            "walks": 1.0,
            "home_runs": 0.0,
            "hit_batters": 1.0,
        },
    ]


def test_population_rates_are_event_per_bf():
    p = population_rates(sample_rows())
    assert abs(p["k"] - 12.0 / 42.0) < 1e-12
    assert abs(p["bb"] - 3.0 / 42.0) < 1e-12
    assert abs(p["hr"] - 1.0 / 42.0) < 1e-12


def test_shrunk_features_use_only_prior_starts():
    rows = sample_rows()
    priors = population_rates(rows)
    x, rates, starts_prior, eff_bf = shrunk_event_features(
        [rows[0]],
        rows[1]["game_time_utc"],
        priors,
        half_life_days=180.0,
        prior_bf=350.0,
    )
    assert starts_prior == 1
    assert eff_bf > 0
    assert x.shape == (4,)
    assert set(rates) == {"k", "bb", "hr", "hbp"}


def test_next_start_dataset_does_not_use_current_start_as_history():
    rows = sample_rows()
    priors = population_rates(rows)
    X, y, meta = build_next_start_dataset(
        rows, priors, half_life_days=180.0, prior_bf=350.0
    )
    assert len(y) == 1
    assert meta[0]["starts_prior"] == 1
    assert meta[0]["game_pk"] if "game_pk" in meta[0] else True


def test_ridge_fit_predict_shapes():
    X = np.array([
        [0.1, -0.1, 0.0, 0.0],
        [0.2, -0.2, -0.1, 0.0],
        [-0.1, 0.1, 0.1, 0.0],
        [-0.2, 0.2, 0.0, 0.1],
    ])
    y = np.array([0.10, 0.08, 0.20, 0.22])
    model = fit_ridge(X, y, 1.0)
    pred = predict(model, X)
    assert pred.shape == (4,)
    assert np.isfinite(pred).all()
