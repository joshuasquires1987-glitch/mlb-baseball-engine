from v11_historical_feed_parser import innings_to_outs, parse_team_pitching

def test_innings_to_outs():
    assert innings_to_outs("6.0") == 18
    assert innings_to_outs("5.2") == 17
    assert innings_to_outs("0.1") == 1

def test_first_pitcher_is_starter():
    box = {
        "pitchers": [10, 20],
        "players": {
            "ID10": {"stats": {"pitching": {"battersFaced": 22, "runs": 2, "inningsPitched": "5.2"}}},
            "ID20": {"stats": {"pitching": {"battersFaced": 10, "runs": 1, "inningsPitched": "3.1"}}},
        },
    }
    rows = parse_team_pitching(box, "99", "2025-07-01T23:00:00Z")
    assert rows[0]["id"] == "10"
    assert rows[0]["p_gs"] == 1
    assert rows[0]["p_ipouts"] == 17
    assert rows[1]["p_gs"] == 0
