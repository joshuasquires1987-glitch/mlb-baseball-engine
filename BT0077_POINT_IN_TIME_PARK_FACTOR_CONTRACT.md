# BT-0077 Point-in-Time Park Run-Environment Factor

Status: RC2 research infrastructure only.

This is not declared to be a canonical causal MLB park factor.

For each target game, before adding that game's result:

1. Gather completed MLB games in the prior 730 days.
2. Compute the venue's mean total runs over its prior games.
3. Compute league mean total runs over the same historical window.
4. Raw factor = venue mean / league mean.
5. Shrink the raw factor toward 1.00 using 40 pseudo-games.
6. Require at least 20 prior games at the venue.
7. Freeze provenance showing the most recent completed game that entered history.
8. Only after the target record is created may the current game's final runs enter history for future games.

Why this is acceptable for RC2 research:
- it is deterministic
- it is point-in-time
- it contains no future games
- it is explicitly a run-environment proxy rather than a claim of causal park effect
- RC2 coefficients must still pass chronological holdout validation before shadow review

Why the registry is keyed by game:
A venue-only record would permit a later-season factor to leak backward into an earlier game.

No v1.1 weights or production rules are changed.
