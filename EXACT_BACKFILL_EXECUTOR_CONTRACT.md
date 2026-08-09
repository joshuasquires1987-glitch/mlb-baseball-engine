# Exact Historical Backfill Executor Contract

The executor performs the real production-history fill in a deterministic sequence:

1. discover completed pregame games for both target teams
2. deduplicate game IDs
3. fetch each exact MLB boxscore
4. extract starter and relief rows with exact BF / runs / outs
5. fetch exact team scores
6. build team-game rows
7. retain only pre-target-date data at readiness time
8. evaluate all six completeness checks
9. export the exact bundle
10. fail closed if coverage is incomplete

NYM@PIT rehearsal window:
- target: 2026-08-09
- Sean Manaea: MLB ID 640455
- Jared Jones: MLB ID 683003
- Mets: MLB team ID 121
- Pirates: MLB team ID 134
- backfill window: 2026-06-20 through 2026-08-08

No probability stage is invoked unless the readiness gate is fully green.
