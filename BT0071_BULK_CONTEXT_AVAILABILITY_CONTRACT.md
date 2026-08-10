# BT-0071 Bulk Context Availability Runner

BT-0071 answers one question before RC2 calibration:

**How many historical MLB games can be assembled without leakage under the BT-0070 rules?**

It audits every completed game for:
1. final outcome
2. exact game time
3. venue identity
4. recoverable pregame weather
5. a frozen park factor whose provenance predates the labeled game
6. venue time-zone metadata
7. prior schedule state for both teams
8. a certified pre-first-pitch lineup/platoon snapshot

The runner reports missing counts by field and the number of fully usable games.

Critical rule:
- absence of a lineup snapshot is counted as missing
- it is never reconstructed from the completed-game batting order
- missing registries remain empty templates until populated from governed sources
- a zero-row result is valid if the required historical evidence does not exist

The 650-game threshold is informational here: 500 training + 150 holdout from BT-0069.

This package does not calibrate coefficients and does not modify production.
