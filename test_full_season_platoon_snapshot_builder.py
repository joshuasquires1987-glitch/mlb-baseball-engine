import json
from full_season_platoon_snapshot_builder import write_jsonl,load_jsonl

def test_jsonl_round_trip(tmp_path):
    p=tmp_path/"x.jsonl"
    rows=[{
        "game_pk":"1",
        "captured_before_first_pitch":True,
        "platoon_lineup_delta":0.25,
    }]
    write_jsonl(rows,p)
    assert load_jsonl(p)==rows
