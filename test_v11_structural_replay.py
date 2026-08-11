import pytest

from v11_structural_replay import probability, DEFAULT_CONTEXT, ReplayState, replay_2025

def test_default_context_locked():
    assert DEFAULT_CONTEXT["home_field"] == 0.10
    assert DEFAULT_CONTEXT["weather"] == 0.0
    assert DEFAULT_CONTEXT["park"] == 0.0

def test_probability_weighted_sigmoid():
    p, score = probability({"a": 1.0, "b": 0.0}, {"a": 1.0, "b": 2.0})
    assert score == 1.0
    assert 0.73 < p < 0.74

def test_replay_state_routes_starter_and_reliever():
    s = ReplayState()
    s.add_completed_game({
        "game_time_utc": "2024-07-01T23:00:00Z",
        "home_team_id": "1",
        "away_team_id": "2",
        "home_runs": 4,
        "away_runs": 3,
        "pitching_rows": [
            {"id": "10", "team": "1", "p_gs": 1, "p_bfp": 20, "p_r": 2, "p_ipouts": 15},
            {"id": "11", "team": "1", "p_gs": 0, "p_bfp": 8, "p_r": 1, "p_ipouts": 6},
        ],
    })
    assert len(s.starters["10"]) == 1
    assert len(s.bullpens["1"]) == 1
    assert len(s.teams["1"]) == 1

def test_replay_state_rejects_missing_score_before_mutation():
    s = ReplayState()
    with pytest.raises(ValueError, match="missing final score"):
        s.add_completed_game({
            "game_time_utc": "2024-07-01T23:00:00Z",
            "home_team_id": "1",
            "away_team_id": "2",
            "home_runs": None,
            "away_runs": 3,
            "pitching_rows": [
                {"id": "10", "team": "1", "p_gs": 1, "p_bfp": 20, "p_r": 2, "p_ipouts": 15},
            ],
        })

    assert len(s.teams["1"]) == 0
    assert len(s.teams["2"]) == 0
    assert len(s.starters["10"]) == 0

def test_replay_logs_bad_warmup_score_instead_of_crashing():
    bad_warmup = {
        "game_pk": "999",
        "game_date": "2024-07-01",
        "game_time_utc": "2024-07-01T23:00:00Z",
        "home_team_id": "1",
        "away_team_id": "2",
        "home_runs": None,
        "away_runs": 3,
        "pitching_rows": [],
    }

    rows, failures = replay_2025([bad_warmup], [], {})

    assert rows == []
    assert len(failures) == 1
    assert failures[0]["game_pk"] == "999"
    assert failures[0]["reason"] == "state-ingest-warmup:ValueError"
    assert "missing final score" in failures[0]["detail"]
