from coverage_gate import full_history_gate,starter_coverage,bullpen_coverage,team_game_coverage

def pitching():
    rows=[]
    for i in range(5):
        rows += [
          {"date":f"2026-07-{10+i:02d}","id":"A","team":"NYM","p_gs":1,"p_bfp":24,"p_r":2,"p_ipouts":18,"source_exact":True},
          {"date":f"2026-07-{10+i:02d}","id":"H","team":"PIT","p_gs":1,"p_bfp":23,"p_r":2,"p_ipouts":17,"source_exact":True},
        ]
    for i in range(15):
        rows += [
          {"date":f"2026-07-{10+i:02d}","id":f"NR{i}","team":"NYM","p_gs":0,"p_bfp":5,"p_r":0,"p_ipouts":3,"source_exact":True},
          {"date":f"2026-07-{10+i:02d}","id":f"PR{i}","team":"PIT","p_gs":0,"p_bfp":5,"p_r":1,"p_ipouts":3,"source_exact":True},
        ]
    return rows

def games():
    out=[]
    for i in range(10):
        out += [
          {"date":f"2026-07-{10+i:02d}","team":"NYM","runs_for":5,"runs_against":3},
          {"date":f"2026-07-{10+i:02d}","team":"PIT","runs_for":4,"runs_against":4},
        ]
    return out

def test_full_ready():
    x=full_history_gate(pitching(),games(),"2026-08-09","NYM","PIT","A","H")
    assert x["ready"]

def test_one_missing_start_blocks():
    rows=[r for r in pitching() if not (r["id"]=="A" and r["date"]=="2026-07-14")]
    x=full_history_gate(rows,games(),"2026-08-09","NYM","PIT","A","H")
    assert not x["ready"]
    assert not x["checks"]["away_starter"]["ready"]

def test_future_rows_do_not_count():
    rows=pitching()+[{"date":"2026-08-10","id":"A","team":"NYM","p_gs":1,"p_bfp":25,"p_r":0,"p_ipouts":21,"source_exact":True}]
    assert starter_coverage(rows,"A","2026-08-09",6)["ready"] is False

def test_non_exact_rows_do_not_count():
    rows=pitching()
    rows.append({"date":"2026-07-20","id":"A","team":"NYM","p_gs":1,"p_bfp":25,"p_r":0,"p_ipouts":21,"source_exact":False})
    assert starter_coverage(rows,"A","2026-08-09",6)["ready"] is False
