# Live Starter + Lineup Rehearsal Contract

This layer validates how real current-game information enters the engine.

Rules:
- pitcher names alone are not enough for production confirmation
- both probable-pitcher identities must resolve to stable IDs
- unresolved/opening/bullpen-game starter situations remain red
- no substitute starter may be guessed
- lineup absence is yellow, not fabricated green
- both confirmed lineups are preferred before final pregame integrity revalidation
- starter integrity has higher priority than lineup integrity
- this rehearsal does not use sportsbook prices

The Aug. 9 fixture deliberately includes ATH@BOS with Boston unresolved to prove the pipeline blocks ambiguous starter situations.
