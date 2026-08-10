# BT-0070 Historical Context Dataset Contract

Purpose: produce leakage-safe rows for future RC2 context calibration.

Allowed historical inputs:
- venue/park identity known before first pitch
- a park factor frozen from data ending before the game being modeled
- pregame weather observation
- prior schedule state only
- prior venue/time-zone state only
- an archived lineup/platoon snapshot captured before first pitch

Allowed postgame field:
- final winner, used only as the supervised target `home_win`

Forbidden:
- completed-game batting order as a proxy for pregame lineup
- substitutions or postgame roster state
- same-game final statistics in any feature
- park factors calculated using the game being labeled
- schedule information from after first pitch
- random train/holdout splitting

Games lacking an archived pregame lineup/platoon snapshot are skipped rather than filled with zero.

Travel/rest direction is home advantage:
- positive `rest_days_delta` means more rest for home
- positive `travel_timezone_delta_hours` means the away side had a larger time-zone transition than home

The dataset must be split chronologically. BT-0069 still controls the 500-game training / 150-game holdout gate.

This package creates data only. It does not calibrate coefficients, alter v1.1, alter frozen RC1, or promote RC2.
