import pytest

from live_integrity import LiveIntegritySnapshot, assert_production_ready


def snapshot(**overrides):
    values = dict(
        game_pk="123",
        starter="green",
        lineup="green",
        bullpen="green",
        weather="green",
        roster_news="green",
        umpire="yellow",
    )
    values.update(overrides)
    return LiveIntegritySnapshot(**values)


def test_all_required_green_is_production_ready():
    assert snapshot().production_ready() is True


def test_yellow_required_component_blocks_probability():
    s = snapshot(lineup="yellow")
    assert s.production_ready() is False
    assert s.blockers() == ["lineup"]
    with pytest.raises(RuntimeError, match="lineup"):
        assert_production_ready(s)


def test_umpire_is_not_a_hard_probability_blocker():
    assert snapshot(umpire="red").production_ready() is True
