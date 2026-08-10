# BT-0080 Full-Season Pregame Lineup Snapshot Builder

Scales BT-0079 to the full 2025 audit population.

Outputs:
- pregame_lineup_snapshots_raw.jsonl
- pregame_lineup_snapshot_build_report.json

Each successful row freezes the MLB historical timecode, both nine-player batting orders, source provenance, and captured_before_first_pitch=true.

platoon_lineup_delta remains null by design. Retrieval and feature-definition are separate governance steps.

No current-feed fallback, final-boxscore batting-order fallback, plate-appearance reconstruction, projection substitution, or zero-filling is allowed.

The workflow fails if fewer than 2,000 games are recovered.
