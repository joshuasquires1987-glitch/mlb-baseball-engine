from run_v11_structural_diagnostics import diagnostic_groups, ranked_findings


def rows():
    return [
        {
            "game_date": "2025-04-01",
            "home_win_probability": 0.43,
            "home_win": 1,
            "brier": (0.43-1)**2,
            "log_loss": 0.8439700703,
            "correct_side": False,
            "features": {
                "starting_pitcher": -0.5,
                "underlying_team_strength": -0.4,
                "bullpen": 0.0,
                "confirmed_lineup_offense": -0.2,
                "defense": -0.1,
            },
        },
        {
            "game_date": "2025-04-02",
            "home_win_probability": 0.58,
            "home_win": 1,
            "brier": (0.58-1)**2,
            "log_loss": 0.5447271754,
            "correct_side": True,
            "features": {
                "starting_pitcher": 0.5,
                "underlying_team_strength": 0.4,
                "bullpen": 0.2,
                "confirmed_lineup_offense": 0.3,
                "defense": 0.1,
            },
        },
    ]


def test_diagnostic_groups_cover_predicted_side():
    groups = diagnostic_groups(rows())
    keys = {(g["dimension"], g["group"]) for g in groups}
    assert ("predicted_side", "away") in keys
    assert ("predicted_side", "home") in keys


def test_ranked_findings_recommends_isolated_context_investigation():
    data = rows()
    groups = diagnostic_groups(data)
    findings = ranked_findings(data, groups)
    assert findings[0]["priority"] == 1
    assert "home" in findings[0]["challenger_implication"].lower()
