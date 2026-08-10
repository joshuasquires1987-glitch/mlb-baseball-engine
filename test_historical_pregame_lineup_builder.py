import json
from historical_pregame_lineup_builder import build_one,build_all,write_jsonl

def game(pk="1"):
    return {"game_pk":pk,"game_date":"2025-07-01","game_time_utc":"2025-07-01T23:00:00Z","away_team_id":"10","home_team_id":"20"}

def fake_fetch(url):
    if url.endswith("/timestamps"):
        return ["20250701_225900","20250701_230000"]
    if "timecode=20250701_225900" in url:
        return {"liveData":{"boxscore":{"teams":{"away":{"battingOrder":list(range(1,10))},"home":{"battingOrder":list(range(11,20))}}}}}
    raise AssertionError(url)

def test_build_one():
    row,err=build_one(game(),fetcher=fake_fetch)
    assert err is None and row["captured_before_first_pitch"] is True
    assert row["platoon_lineup_delta"] is None
    assert row["away_batting_order"]==list(range(1,10))

def test_no_timecode():
    def fetch(url):
        if url.endswith("/timestamps"): return ["20250701_230000"]
        raise AssertionError
    row,err=build_one(game(),fetcher=fetch)
    assert row is None and err["reason"]=="no-pregame-timecode"

def test_parallel_sort():
    rows,failures=build_all([game("2"),game("1")],max_workers=2,fetcher=fake_fetch)
    assert not failures
    assert [r["game_pk"] for r in rows]==["1","2"]

def test_jsonl(tmp_path):
    p=tmp_path/"x.jsonl"; rows=[{"game_pk":"1"}]
    write_jsonl(rows,p)
    assert json.loads(p.read_text().strip())==rows[0]
