from pathlib import Path

from engine_types import BaseballInputs, IntegrityState, PriceInput
from dual_model_runner import DualModelRunner

ROOT = Path(__file__).resolve().parent


def test_shadow_never_controls_bet():
    runner = DualModelRunner(ROOT)

    inputs = BaseballInputs(
        game_id="X",
        game_date="2026-08-09",
        home_team="H",
        away_team="A",
        features={
            "starting_pitcher": 0.2,
            "underlying_team_strength": 0.1,
            "bullpen": 0.1,
            "confirmed_lineup_offense": 0.1,
            "home_field": 0.1,
            "starting_pitcher_talent_state": 0.2,
            "bullpen_talent_state": 0.1,
            "expected_starter_depth": 0.1,
            "bullpen_exposure_quality": 0.1,
        },
        integrity=IntegrityState(
            "green", "green", "green", "green", "green"
        ),
    )

    prod, shadow = runner.predict(inputs)

    decision, shadow_view = runner.evaluate_prices(
        prod,
        shadow,
        PriceInput(
            home_decimal=1.95,
            away_decimal=1.95,
            snapshot_label="test",
        ),
    )

    assert decision.production_model_version == "v1.1"
    assert shadow_view["controls_bets"] is False
    assert shadow_view["controls_stakes"] is False


def test_red_integrity_blocks_production():
    runner = DualModelRunner(ROOT)

    inputs = BaseballInputs(
        game_id="Y",
        game_date="2026-08-09",
        home_team="H",
        away_team="A",
        features={"starting_pitcher": 3.0},
        integrity=IntegrityState(
            "red", "green", "green", "green", "green"
        ),
    )

    prod, shadow = runner.predict(inputs)

    decision, _ = runner.evaluate_prices(
        prod,
        shadow,
        PriceInput(
            home_decimal=2.2,
            away_decimal=1.7,
            snapshot_label="test",
        ),
    )

    assert decision.eligible is False
