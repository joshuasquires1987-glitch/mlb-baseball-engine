from game_summary_runtime import fetch_linescore_summary, live_feed_url


def test_live_feed_url():
    assert live_feed_url("123").endswith("/game/123/feed/live")


def test_summary_extracts_team_and_runs():
    payload = {
        "gameData": {
            "teams": {
                "away": {"abbreviation": "NYM"},
                "home": {"abbreviation": "PIT"},
            }
        },
        "liveData": {
            "linescore": {
                "teams": {
                    "away": {"runs": 5},
                    "home": {"runs": 3},
                }
            }
        },
    }

    def fetcher(url):
        return payload

    x = fetch_linescore_summary("123", fetcher=fetcher)
    assert x["teams"]["away"]["team"]["abbreviation"] == "NYM"
    assert x["teams"]["home"]["team"]["abbreviation"] == "PIT"
    assert x["teams"]["away"]["score"] == 5
    assert x["teams"]["home"]["score"] == 3
