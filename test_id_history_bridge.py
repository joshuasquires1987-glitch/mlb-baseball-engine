from pathlib import Path
from mlb_id_registry import MLBPlayerIDRegistry
from mlb_history_endpoints import player_game_log_url
from history_attachment import HistoryAttachment,attach_histories
ROOT=Path(__file__).parent
def test_registry():
    r=MLBPlayerIDRegistry.from_json(ROOT/"mlb_player_id_registry_2026-08-09.json")
    assert r.resolve("Brady Singer")=="663903"
    assert r.resolve("Jesús Luzardo")=="666200"
def test_url():
    u=player_game_log_url("663903",2026); assert "663903" in u and "gameLog" in u
def test_green_requires_history():
    r=MLBPlayerIDRegistry.from_json(ROOT/"mlb_player_id_registry_2026-08-09.json")
    rows=[{"away_pitcher_name":"Brady Singer","home_pitcher_name":"Brad Lord"}]
    def lookup(pid): return HistoryAttachment(pid,2026,[{"date":"2026-08-01"}],"u","now")
    assert attach_histories(rows,r,lookup)[0]["starter_integrity"]=="green"
def test_missing_history_red():
    r=MLBPlayerIDRegistry.from_json(ROOT/"mlb_player_id_registry_2026-08-09.json")
    rows=[{"away_pitcher_name":"Brady Singer","home_pitcher_name":"Brad Lord"}]
    def lookup(pid): return HistoryAttachment(pid,2026,[1],"u","now") if pid=="663903" else None
    assert attach_histories(rows,r,lookup)[0]["starter_integrity"]=="red"
