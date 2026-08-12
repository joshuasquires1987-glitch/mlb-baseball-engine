from v11_structural_replay import ReplayState
from run_v11_structural_default_replay import pitching_event_coverage

def test_replay_state_preserves_starter_event_fields():
    s = ReplayState()
    s.add_completed_game({
        "game_time_utc": "2024-07-01T23:00:00Z",
        "home_team_id": "1",
        "away_team_id": "2",
        "home_runs": 4,
        "away_runs": 3,
        "pitching_rows": [{
            "id": "10",
            "team": "1",
            "p_gs": 1,
            "p_bfp": 24,
            "p_r": 2,
            "p_ipouts": 18,
            "p_so": 8,
            "p_bb": 2,
            "p_hr": 1,
            "p_hbp": 0,
        }],
    })
    row = s.starters["10"][0]
    assert row["strikeouts"] == 8
    assert row["walks"] == 2
    assert row["home_runs"] == 1
    assert row["hit_batters"] == 0

def test_pitching_event_coverage_counts_starter_rows():
    parsed = [{
        "pitching_rows": [
            {
                "p_gs": 1,
                "p_bfp": 20,
                "p_so": 5,
                "p_bb": 2,
                "p_hr": 1,
                "p_hbp": 0,
            },
            {
                "p_gs": 0,
                "p_bfp": 10,
                "p_so": 2,
                "p_bb": 1,
                "p_hr": 0,
                "p_hbp": 0,
            },
        ]
    }]
    c = pitching_event_coverage(parsed)
    assert c["p_so"]["starter_rows"] == 1
    assert c["p_so"]["present"] == 1
    assert c["p_so"]["coverage_rate"] == 1.0
