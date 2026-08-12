import json

import pytest

from run_v11_structural_default_replay import normalize_snapshot, load_snapshots

BASE = {
    "game_pk": "123",
    "game_date": "2025-04-01",
    "home_team_id": "1",
    "away_team_id": "2",
    "home_probable_starter_id": "10",
    "away_probable_starter_id": "20",
}

def test_normalize_snapshot_accepts_certified_scheduled_time_alias():
    row = {
        **BASE,
        "scheduled_game_time_utc": "2025-04-01T23:10:00Z",
    }
    normalized = normalize_snapshot(row)
    assert normalized["game_time_utc"] == "2025-04-01T23:10:00Z"
    assert normalized["scheduled_game_time_utc"] == "2025-04-01T23:10:00Z"

def test_normalize_snapshot_preserves_existing_canonical_time():
    row = {
        **BASE,
        "game_time_utc": "2025-04-01T23:10:00Z",
        "scheduled_game_time_utc": "2025-04-01T23:05:00Z",
    }
    normalized = normalize_snapshot(row)
    assert normalized["game_time_utc"] == "2025-04-01T23:10:00Z"

def test_normalize_snapshot_rejects_missing_timestamp():
    with pytest.raises(ValueError, match="game_time_utc"):
        normalize_snapshot(dict(BASE), line_number=7)

def test_load_snapshots_normalizes_jsonl(tmp_path):
    path = tmp_path / "snapshots.jsonl"
    path.write_text(json.dumps({
        **BASE,
        "scheduled_game_time_utc": "2025-04-01T23:10:00Z",
    }) + "\n")
    rows = load_snapshots(path)
    assert len(rows) == 1
    assert rows[0]["game_time_utc"] == "2025-04-01T23:10:00Z"
