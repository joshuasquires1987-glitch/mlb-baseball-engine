# BT-0078 Chunked Historical Schedule Fix

Observed failure:
BT-0077's multi-year MLB schedule request completed without an HTTP
error but produced zero historical games, which in turn created zero
park-factor records.

Fix:
- historical schedules are now requested one calendar month at a time
- results are merged and deduplicated by MLB gamePk
- games are sorted chronologically before point-in-time calculation
- per-chunk retrieval counts are stored in the registry artifact
- the build now fails hard if fewer than 4,000 completed historical
  games are recovered
- the build also fails if fewer than 2,000 2025 target park-factor
  records are produced

The thresholds are sanity guards, not model parameters.

No park-factor formula or production model weight is changed by BT-0078.
