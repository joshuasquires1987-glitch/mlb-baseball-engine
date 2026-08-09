# Real-Source Rehearsal Contract

BT-0052 validates the ingestion layer against an actual MLB.com slate snapshot.

For 2026-08-09, the official MLB schedule lists 15 games.

This rehearsal verifies:
- all 30 MLB teams appear exactly once
- team abbreviations normalize correctly
- no accidental duplicate matchup rows exist
- earliest and latest listed games are preserved
- schedule completeness is kept separate from starter/lineup completeness

Important:
- schedule verification does not imply starter confirmation
- starter IDs must still come from a fresh probable-pitcher/game source
- lineup confirmation must still come from an actual lineup source
- no sportsbook prices are part of source validation
