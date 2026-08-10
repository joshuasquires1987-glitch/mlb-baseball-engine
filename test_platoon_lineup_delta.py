import pytest
from platoon_lineup_delta import hitter_has_platoon_advantage, lineup_advantage_share, platoon_lineup_delta
from timecoded_platoon_evidence import probable_starter_ids, player_map


def test_opposite_hand_advantage():
    assert hitter_has_platoon_advantage("L", "R") == 1.0
    assert hitter_has_platoon_advantage("R", "L") == 1.0
    assert hitter_has_platoon_advantage("R", "R") == 0.0
    assert hitter_has_platoon_advantage("L", "L") == 0.0


def test_switch_hitter_advantage():
    assert hitter_has_platoon_advantage("S", "R") == 1.0
    assert hitter_has_platoon_advantage("S", "L") == 1.0


def test_share_requires_nine():
    with pytest.raises(ValueError):
        lineup_advantage_share(["R"] * 8, "L")


def test_delta_home_minus_away():
    assert platoon_lineup_delta(["R"] * 9, ["R"] * 9, "R", "L") == 1.0


def test_delta_bounds():
    x = platoon_lineup_delta(["L"] * 9, ["R"] * 9, "L", "R")
    assert -1.0 <= x <= 1.0


def test_timecoded_probables_and_players():
    state = {"gameData": {"probablePitchers": {"away": {"id": 100}, "home": {"id": 200}}, "players": {"ID100": {"id": 100, "pitchHand": {"code": "L"}}, "ID200": {"id": 200, "pitchHand": {"code": "R"}}, "ID1": {"id": 1, "batSide": {"code": "S"}}}}}
    assert probable_starter_ids(state) == {"away": "100", "home": "200"}
    p = player_map(state)
    assert p["100"]["pitch_hand"] == "L"
    assert p["1"]["bat_side"] == "S"
