# History Exactness Contract

Public game-log pages are useful for verifying recent innings and runs, but the first production probability requires the exact fields consumed by the frozen state calculator.

For starter talent/depth, required fields are:
- date
- outs
- runs allowed
- batters faced

Rules:
- baseball IP notation is converted exactly to outs
- missing batters faced is never silently approximated
- derived or estimated required fields are not production-ready
- a history snapshot may be retained for research even when the production gate is red
- the engine must obtain exact BF (for example from MLB Stats API/game data or another exact source) before the starter history can feed a real production probability

This prevents an apparent live probability from being based on hidden approximations.
