from engine_types import BaseballInputs, IntegrityState

from live_probability_freeze import fingerprint_model_inputs


def test_input_fingerprint_is_stable():
    inputs = BaseballInputs(
        game_id="123",
        game_date="2026-08-12",
        home_team="1",
        away_team="2",
        features={"starting_pitcher": 0.1},
        integrity=IntegrityState(
            starter="green",
            lineup="green",
            bullpen="green",
            weather="green",
            roster_news="green",
        ),
    )
    assert fingerprint_model_inputs(inputs) == fingerprint_model_inputs(inputs)
