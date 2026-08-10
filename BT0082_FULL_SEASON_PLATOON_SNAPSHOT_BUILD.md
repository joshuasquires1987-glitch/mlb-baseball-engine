# BT-0082 Full-Season Platoon Snapshot Build

Purpose:
Convert the 2,427 BT-0080 certified historical pregame batting orders
into the final snapshot file consumed by the Context Availability Audit.

For each raw certified snapshot:
- re-fetch the same historical MLB timecoded state
- read both pregame probable starters
- read starter throwing hand
- read each lineup hitter's batting side
- derive platoon_lineup_delta using the BT-0081 definition
- preserve captured_before_first_pitch=true
- write the enriched row to pregame_lineup_snapshots.jsonl

The build fails closed when required pregame evidence is missing.

Governance:
- no final boxscore fallback
- no current-feed lineup fallback
- no outcome/postgame performance stats
- no zero-filling
- no production model mutation

Sanity gate:
At least 2,300 final snapshots must be produced.
