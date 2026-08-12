from live_slate_runtime import _extract_live_slate


def test_live_slate_extracts_canonical_identity_and_probables():
    payload = {
        "dates": [{
            "date": "2026-08-12",
            "games": [{
                "gamePk": 123,
                "gameDate": "2026-08-12T23:10:00Z",
                "status": {
                    "abstractGameState": "Preview",
                    "detailedState": "Scheduled",
                },
                "teams": {
                    "home": {
                        "team": {"id": 1, "name": "Home"},
                        "probablePitcher": {"id": 10, "fullName": "Home SP"},
                    },
                    "away": {
                        "team": {"id": 2, "name": "Away"},
                        "probablePitcher": {"id": 20, "fullName": "Away SP"},
                    },
                },
                "venue": {"id": 99, "name": "Park"},
            }],
        }],
    }
    rows = _extract_live_slate(payload)
    assert rows[0]["game_pk"] == "123"
    assert rows[0]["home_team_id"] == "1"
    assert rows[0]["away_team_id"] == "2"
    assert rows[0]["home_probable_starter_id"] == "10"
    assert rows[0]["away_probable_starter_id"] == "20"
    assert rows[0]["venue_id"] == "99"
