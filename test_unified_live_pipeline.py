import pandas as pd
from datetime import datetime,timezone
from unified_live_pipeline import UnifiedLivePipeline
from current_game_sources import SourceStamp
from mlb_schedule_adapter import parse_schedule_games
from engine_types import PriceInput

NOW=datetime(2026,8,9,15,0,tzinfo=timezone.utc)

def schedule_payload():
    return {"dates":[{"date":"2026-08-09","games":[{
      "gamePk":123,"gameDate":"2026-08-09T17:05:00Z","venue":{"name":"Test Park"},
      "teams":{
        "home":{"team":{"id":1,"abbreviation":"H"},"probablePitcher":{"id":101,"fullName":"Home Starter"}},
        "away":{"team":{"id":2,"abbreviation":"A"},"probablePitcher":{"id":202,"fullName":"Away Starter"}}
      }}]}]}

def pitching():
    return pd.DataFrame([
        {"id":"101","team":"H","date":"2026-08-01","p_gs":1,"p_bfp":24,"p_r":1,"p_ipouts":18},
        {"id":"202","team":"A","date":"2026-08-01","p_gs":1,"p_bfp":24,"p_r":5,"p_ipouts":15},
        {"id":"HR","team":"H","date":"2026-08-08","p_gs":0,"p_bfp":15,"p_r":0,"p_ipouts":9},
        {"id":"AR","team":"A","date":"2026-08-08","p_gs":0,"p_bfp":15,"p_r":4,"p_ipouts":9},
    ])

def games():
    return pd.DataFrame([
        {"date":"2026-08-07","hometeam":"H","visteam":"X","hruns":7,"vruns":2},
        {"date":"2026-08-07","hometeam":"A","visteam":"X","hruns":2,"vruns":6},
    ])

def test_full_run_separation():
    src=SourceStamp("MLB",NOW.isoformat())
    row=parse_schedule_games(schedule_payload(),src)[0]
    p=UnifiedLivePipeline(".")
    out=p.full_run(
        row,True,src,0.0,src,True,src,
        pitching(),games(),PriceInput(2.20,1.70,"first"),
        park_score=.05,now_utc=NOW
    )
    assert out["production_prediction"].model_version=="v1.1"
    assert out["shadow_prediction"].model_version=="v1.2-RC1"
    assert out["analysis"]["shadow"]["controls_bets"] is False

def test_starter_missing_blocks_integrity():
    src=SourceStamp("MLB",NOW.isoformat())
    payload=schedule_payload()
    del payload["dates"][0]["games"][0]["teams"]["away"]["probablePitcher"]
    row=parse_schedule_games(payload,src)[0]
    p=UnifiedLivePipeline(".")
    current,matchup=p.build_matchup(row,True,src,0.0,src,True,src,now_utc=NOW)
    assert not matchup.away_starter_confirmed
