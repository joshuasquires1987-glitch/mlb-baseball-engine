from v11_replay_semantics import (
    V11_FEATURE_SEMANTICS,
    exact_replay_possible,
    structural_default_replay_possible,
)

def test_named_lineup_feature_uses_team_offense_semantics():
    x=V11_FEATURE_SEMANTICS["confirmed_lineup_offense"]
    assert "TeamState.offense_score" in x["derivation"]

def test_external_context_scores_block_exact_replay():
    assert exact_replay_possible() is False
    assert V11_FEATURE_SEMANTICS["weather"]["default_value"]==0.0
    assert V11_FEATURE_SEMANTICS["home_field"]["default_value"]==0.10

def test_structural_default_replay_is_possible():
    assert structural_default_replay_possible() is True
