# Pregame Feature Builder Contract

The feature builder converts verified pregame baseball facts into normalized home-minus-away model features.

Rules:
- Positive feature values favor the home team; negative values favor the away team.
- Sportsbook prices are forbidden inputs.
- Starting-pitcher identity has highest integrity priority.
- A starter change invalidates the prior feature build and requires a complete rerun.
- Expected starter depth uses only prior starts.
- Lineup projections may be used when confirmed lineups are unavailable, but integrity is yellow.
- Missing weather/bullpen/roster context is represented by yellow integrity rather than fabricated values.
- Umpire data is optional.
- v1.1 and RC1 are built from the same verified fact set, with RC1 additionally using expected starter depth and bullpen exposure × quality.
