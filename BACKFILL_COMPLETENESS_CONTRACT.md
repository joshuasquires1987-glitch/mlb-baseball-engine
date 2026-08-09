# Exact Backfill Completeness Contract

The engine must not confuse a handful of exact historical rows with a complete pregame state.

Before a real probability is permitted, the historical bundle must meet minimum exact coverage for:
- both starting pitchers
- both bullpens
- both team game histories

Default rehearsal minimums:
- 5 exact prior starts per starter
- 15 exact prior relief rows per bullpen
- 10 exact prior team games per team

These thresholds are a data-completeness gate, not a model-weight change.

All rows must predate the target game and retain `source_exact=True`.
If any coverage check fails, the probability run remains blocked.
