from context_availability_audit import audit_game,summarize_audit
from pregame_snapshot_registry import PregameSnapshotRegistry
from context_static_registries import FrozenRegistry
from bulk_context_dataset_runner import BulkContextDatasetRunner

def game(pk="1"):
    return {
      "game_pk":pk,"game_date":"2025-07-01","game_time_utc":"2025-07-01T23:00:00Z",
      "home_team_id":"134","away_team_id":"121","home_runs":4,"away_runs":2,"venue_id":"31"
    }

def test_audit_names_lineup_bottleneck():
    a=audit_game(
      game(),{"temp_f":80,"wind_out_mph":0,"wind_in_mph":0},
      {"park_factor":1.0,"frozen_through_date":"2024-12-31"},
      {"utc_offset_hours":-4},
      {"home":{},"away":{}},
      None,
    )
    assert not a["usable"]
    assert a["missing"]==["pregame_lineup_snapshot"]

def test_summary_target():
    s=summarize_audit([{"usable":True,"missing":[]} for _ in range(650)])
    assert s["meets_650_game_target"]

def test_registry_rejects_uncertified_snapshot():
    try:
        PregameSnapshotRegistry([{"game_pk":"1","captured_before_first_pitch":False}])
        assert False
    except ValueError:
        pass

def test_runner_never_fills_missing_snapshot():
    parks=FrozenRegistry([{"venue_id":"31","park_factor":1.0,"frozen_through_date":"2024-12-31"}],key="venue_id")
    venues=FrozenRegistry([{"venue_id":"31","utc_offset_hours":-4}],key="venue_id")
    snaps=PregameSnapshotRegistry([])
    runner=BulkContextDatasetRunner(
      lambda pk:{"temp_f":80,"wind_out_mph":0,"wind_in_mph":0},
      parks,venues,snaps
    )
    # Two games establish prior schedule state, but neither can become usable without snapshot.
    g1=game("1")
    g2={**game("2"),"game_date":"2025-07-03","game_time_utc":"2025-07-03T23:00:00Z"}
    r=runner.run([g1,g2])
    assert r["rows"]==[]
    assert r["availability"]["missing_counts"]["pregame_lineup_snapshot"]==2
