from mlb_boxscore_exact_adapter import exact_pitching_rows, exact_starter_row


def payload_with_ordered_pitchers():
    return {
        "teams":{
            "away":{
                "team":{"abbreviation":"NYM"},
                "pitchers":[640455,111],
                "players":{
                    "ID640455":{
                        "person":{"id":640455},
                        "stats":{"pitching":{"inningsPitched":"6.0","runs":2,"battersFaced":25}}
                    },
                    "ID111":{
                        "person":{"id":111},
                        "stats":{"pitching":{"inningsPitched":"3.0","runs":0,"battersFaced":10}}
                    },
                },
            }
        }
    }


def test_first_ordered_pitcher_is_starter_when_probable_missing():
    rows=exact_pitching_rows(payload_with_ordered_pitchers(),"2026-08-01","NYM")
    s=[r for r in rows if r["id"]=="640455"][0]
    r=[r for r in rows if r["id"]=="111"][0]
    assert s["p_gs"]==1
    assert r["p_gs"]==0


def test_games_started_has_priority():
    p=payload_with_ordered_pitchers()
    p["teams"]["away"]["pitchers"]=[111,640455]
    p["teams"]["away"]["players"]["ID640455"]["stats"]["pitching"]["gamesStarted"]=1
    row=exact_starter_row(p,"2026-08-01","NYM","640455")
    assert row["p_gs"]==1
