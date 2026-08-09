from team_game_exact_adapter_v2 import team_game_rows_from_game
from canonical_bundle_frames import canonical_games_frame
from exact_bundle_frames import games_frame
from proof_artifact import write_probability_proof
from pathlib import Path

def sample():
    return {"teams":{
      "away":{"team":{"abbreviation":"NYM"},"score":5},
      "home":{"team":{"abbreviation":"PIT"},"score":3},
    }}

def test_v2_preserves_venue():
    c,p=team_game_rows_from_game(sample(),"2026-08-01")
    assert c["hometeam"]=="PIT" and c["visteam"]=="NYM"
    assert c["hruns"]==3 and c["vruns"]==5
    assert p[0]["venue"]=="away" and p[1]["venue"]=="home"

def test_canonical_frame():
    c,_=team_game_rows_from_game(sample(),"2026-08-01")
    df=canonical_games_frame({"canonical_team_games":[c]})
    assert list(df.columns)==["date","hometeam","visteam","hruns","vruns","source_exact"]

def test_old_perspective_bundle_fails_closed():
    try:
        games_frame({"team_games":[{"date":"x","team":"NYM","opponent":"PIT","runs_for":5,"runs_against":3}]})
        assert False
    except RuntimeError: pass

def test_proof_records_no_price(tmp_path):
    r={"production":{"home_win_prob":0.51},"shadow":{"home_win_prob":0.52},
       "probabilities_frozen":True,"prices_seen":False}
    p=write_probability_proof(tmp_path/"p.json","NYM@PIT","2026-08-09",r,{"ready":True})
    assert p["prices_seen"] is False
    assert len(p["sha256"])==64
