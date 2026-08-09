from exact_backfill_executor import ExactBackfillExecutor
def box(pk): return {"rows":[]}
def summary(pk): return {"teams":{"away":{"team":{"abbreviation":"NYM"},"score":5},"home":{"team":{"abbreviation":"PIT"},"score":3}}}
def test_canonical_export():
    e=ExactBackfillExecutor(box,summary); e.ingest_game("1","2026-08-01"); b=e.export_bundle()
    assert b["canonical_team_games"][0]["hometeam"]=="PIT"
    assert len(b["team_games"])==2
