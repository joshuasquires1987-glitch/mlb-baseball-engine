from datetime import datetime,timezone,timedelta
from current_game_sources import SourceStamp
from mlb_schedule_adapter import parse_schedule_games
from current_game_ingestor import CurrentGameIngestor

NOW=datetime(2026,8,9,15,0,tzinfo=timezone.utc)
def payload():
    return {"dates":[{"date":"2026-08-09","games":[{"gamePk":123,"gameDate":"2026-08-09T17:05:00Z",
      "venue":{"name":"Test Park"},"teams":{
      "home":{"team":{"id":1,"abbreviation":"H"},"probablePitcher":{"id":101,"fullName":"Home Starter"}},
      "away":{"team":{"id":2,"abbreviation":"A"},"probablePitcher":{"id":202,"fullName":"Away Starter"}}}}]}]}

def test_schedule_parse():
    s=SourceStamp("MLB",NOW.isoformat())
    r=parse_schedule_games(payload(),s)[0]
    assert r["home_starter_id"]=="101" and r["away_starter_id"]=="202"

def test_fresh_inputs_confirm():
    s=SourceStamp("MLB",(NOW-timedelta(minutes=10)).isoformat())
    r=parse_schedule_games(payload(),s)[0]
    rec=CurrentGameIngestor().build_record(r,True,s,0.0,s,True,s,park_score=.1,now_utc=NOW)
    m=CurrentGameIngestor().to_matchup_definition(rec)
    assert m.home_starter_confirmed and m.away_starter_confirmed
    assert m.lineup_confirmed and m.weather_current and m.roster_news_clear

def test_stale_starter_not_confirmed():
    s=SourceStamp("MLB",(NOW-timedelta(hours=5)).isoformat())
    r=parse_schedule_games(payload(),s)[0]
    f=SourceStamp("fresh",(NOW-timedelta(minutes=5)).isoformat())
    rec=CurrentGameIngestor().build_record(r,True,f,0.0,f,True,f,now_utc=NOW)
    assert not rec.home_starter.confirmed and not rec.away_starter.confirmed

def test_missing_pitcher_not_confirmed():
    p=payload(); del p["dates"][0]["games"][0]["teams"]["away"]["probablePitcher"]
    s=SourceStamp("MLB",NOW.isoformat())
    r=parse_schedule_games(p,s)[0]
    rec=CurrentGameIngestor().build_record(r,True,s,0.0,s,True,s,now_utc=NOW)
    assert not rec.away_starter.confirmed
