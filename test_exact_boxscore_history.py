import json
from pathlib import Path
from mlb_boxscore_exact_adapter import exact_starter_row,exact_relief_rows,innings_to_outs
from historical_boxscore_store import HistoricalBoxscoreStore

ROOT=Path(__file__).parent
def fixture():
    return json.loads((ROOT/"statsapi_boxscore_schema_fixture.json").read_text())

def test_exact_starter_fields():
    r=exact_starter_row(fixture(),"2026-08-04","NYM","640455")
    assert r["p_bfp"]==25
    assert r["p_r"]==2
    assert r["p_ipouts"]==18
    assert r["source_exact"] is True

def test_baseball_out_conversion():
    assert innings_to_outs("5.2")==17
    assert innings_to_outs("1.1")==4

def test_relief_excludes_starter():
    rows=exact_relief_rows(fixture(),"2026-08-04","NYM")
    assert len(rows)==1
    assert rows[0]["id"]=="123"
    assert rows[0]["p_gs"]==0

def test_store_strictly_prior():
    s=HistoricalBoxscoreStore()
    s.ingest("1","2026-08-04",fixture())
    assert len(s.pitcher_history("640455","2026-08-09"))==1
    assert len(s.pitcher_history("640455","2026-08-04"))==0

def test_store_deduplicates():
    s=HistoricalBoxscoreStore()
    s.ingest("1","2026-08-04",fixture())
    n=len(s.pitching_rows)
    s.ingest("1","2026-08-04",fixture())
    assert len(s.pitching_rows)==n
