# BT-0087 v1.1 Structural-Default Historical Replay

Creates a leakage-safe structural-default v1.1 probability ledger.

- 2024 completed games provide warmup history.
- 2025 certified snapshot games are predicted using prior-only starter, team, and bullpen state.
- All games on a calendar date are predicted before any result from that date is admitted to history.
- Frozen external-context defaults are used: home_field=0.10; park/weather/travel/platoon=0.0.
- The output is explicitly NOT labeled as the exact historical v1.1 probability ledger.
- Production weights, bets, and stakes are unchanged.

Outputs:
- v11_structural_default_probability_ledger.jsonl
- v11_structural_default_replay_report.json
