from mlb_historical_timecode_runtime import safe_pregame_timecode,timecoded_feed_url
from historical_pregame_lineup_probe import extract_starting_orders,probe_result,summarize

def test_latest_timestamp_before_cutoff_is_selected():
    stamps=[
        "20250701_225000",
        "20250701_225900",
        "20250701_230000",
        "bad",
    ]
    assert safe_pregame_timecode(
        stamps,"2025-07-01T23:00:00Z",60
    )=="20250701_225900"

def test_post_cutoff_timestamp_is_never_selected():
    stamps=["20250701_230000","20250701_230100"]
    assert safe_pregame_timecode(
        stamps,"2025-07-01T23:00:00Z",60
    ) is None

def test_timecoded_url_contains_historical_code():
    assert "timecode=20250701_225900" in timecoded_feed_url(
        "123","20250701_225900"
    )

def test_extract_orders_requires_boxscore_batting_order():
    state={
        "liveData":{
            "boxscore":{
                "teams":{
                    "away":{"battingOrder":list(range(1,10))},
                    "home":{"battingOrder":list(range(11,20))},
                }
            }
        }
    }
    x=extract_starting_orders(state)
    assert len(x["away"])==9
    assert len(x["home"])==9

def test_completed_state_fallback_does_not_exist():
    game={"game_pk":"1","game_date":"2025-07-01","game_time_utc":"2025-07-01T23:00:00Z"}
    r=probe_result(game,None)
    assert not r["recoverable"]
    assert r["reason"]=="no-pregame-timecode"

def test_duplicate_player_invalidates_order():
    state={
        "liveData":{
            "boxscore":{
                "teams":{
                    "away":{"battingOrder":[1,2,3,4,5,6,7,8,8]},
                    "home":{"battingOrder":list(range(11,20))},
                }
            }
        }
    }
    game={"game_pk":"1","game_date":"2025-07-01","game_time_utc":"2025-07-01T23:00:00Z"}
    payload={"timecode":"20250701_225900","state":state}
    r=probe_result(game,payload)
    assert not r["recoverable"]

def test_summary():
    s=summarize([
        {"recoverable":True},
        {"recoverable":False,"reason":"no-pregame-timecode"},
    ])
    assert s["games_probed"]==2
    assert s["recoverable_rate"]==0.5
