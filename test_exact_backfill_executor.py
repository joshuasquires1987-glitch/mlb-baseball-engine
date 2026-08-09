from exact_backfill_executor import ExactBackfillExecutor
from nym_pit_backfill_plan import dedupe_game_refs

def test_dedupe_refs():
    a=[{"game_pk":"1","game_date":"2026-07-01"},{"game_pk":"2","game_date":"2026-07-02"}]
    b=[{"game_pk":"2","game_date":"2026-07-02"},{"game_pk":"3","game_date":"2026-07-03"}]
    assert [x["game_pk"] for x in dedupe_game_refs(a,b)]==["1","2","3"]

def test_executor_ingests_once():
    def box(pk):
        return {"rows":[
          {"id":"A","team":"NYM","p_gs":1,"p_bfp":20,"p_r":1,"p_ipouts":15,"source_exact":True},
          {"id":"R","team":"NYM","p_gs":0,"p_bfp":5,"p_r":0,"p_ipouts":3,"source_exact":True}
        ]}
    def summary(pk):
        return {"teams":{
          "away":{"team":{"abbreviation":"NYM"},"score":5},
          "home":{"team":{"abbreviation":"PIT"},"score":3}}}
    e=ExactBackfillExecutor(box,summary)
    e.ingest_game("1","2026-07-01")
    e.ingest_game("1","2026-07-01")
    assert len(e.processed)==1
    assert len(e.team_games)==2

def test_fail_closed_readiness():
    def box(pk): return {"rows":[]}
    def summary(pk):
        return {"teams":{"away":{"team":{"abbreviation":"NYM"},"score":1},"home":{"team":{"abbreviation":"PIT"},"score":0}}}
    e=ExactBackfillExecutor(box,summary)
    e.ingest_game("1","2026-07-01")
    assert not e.readiness("2026-08-09","NYM","PIT","640455","683003")["ready"]
