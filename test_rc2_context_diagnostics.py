from rc2_context_diagnostics import expanding_folds,GROUPS
def test_groups_cover_features():
 assert "park_factor_delta" in GROUPS["park"]
 assert "platoon_lineup_delta" in GROUPS["platoon"]
def test_expanding_folds():
 rows=[{"game_date":f"2025-01-{i%28+1:02d}","game_id":str(i)} for i in range(1000)]
 f=expanding_folds(rows,4,700)
 assert len(f)==4
 assert all(len(tr)>=700 for tr,te in f)
