# BT-0081 Platoon Lineup Delta Historical Probe

Research-only feature definition:

`platoon_lineup_delta = home advantageous-hitter share versus the away pregame probable starter - away advantageous-hitter share versus the home pregame probable starter`

Advantage classification: L vs R, R vs L, and switch hitter vs either hand. Same-handed L/L and R/R are not classified as advantaged. Range is [-1, +1].

All evidence must come from the same historical MLB timecoded pregame state. Missing probable starter, pitch hand, or lineup bat side fails closed. No final boxscore, game outcome, or performance statistic is used.
