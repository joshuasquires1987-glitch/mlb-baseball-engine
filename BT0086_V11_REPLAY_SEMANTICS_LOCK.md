# BT-0086 v1.1 Replay Semantics Lock

Finding:

The frozen v1.1 code can reconstruct the five state-derived components:
- starting pitcher
- underlying team strength
- bullpen
- confirmed_lineup_offense (actually TeamState offense_score)
- defense

The remaining five context components are not calculated by the frozen
v1.1 implementation. They are normalized scores supplied to the
assembler/ingestor from outside the model:
- home_field
- park
- weather
- travel_rest_circadian
- platoon_matchup_fit

Frozen defaults:
- home_field = 0.10
- park = 0.0
- weather = 0.0
- travel_rest_circadian = 0.0
- platoon_matchup_fit = 0.0

Therefore:

1. An EXACT historical v1.1 probability ledger cannot be certified from
   this repository alone unless archived historical values for those
   externally supplied normalized scores are found.

2. A STRUCTURAL-DEFAULT v1.1 replay can be built using the frozen code
   defaults. It must be labeled as such and never represented as the
   original historical v1.1 probability.

3. RC2 raw context variables must not be inserted into the old v1.1
   feature slots merely because their names are similar.

Next permitted research step:
Build the leakage-safe structural-default v1.1 replay for the historical
games, then test candidate context layers as additions to that fixed
baseline. Production v1.1 remains frozen.
