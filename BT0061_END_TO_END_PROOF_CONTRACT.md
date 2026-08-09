# BT-0061 End-to-End Probability Proof Harness

This harness is the final blind-to-market integration boundary.

It requires:
- a fully green exact-history bundle
- exact pitcher rows
- canonical exact team-game rows with explicit home/away venue
- clean pregame integrity
- frozen v1.1 + RC1 outputs
- `prices_seen = false`
- a SHA-256 proof artifact

Important audit finding:
The earlier exact team-game adapter stored only team-perspective rows. The existing
`retrosheet_adapters.team_rows_from_games()` requires canonical `hometeam`,
`visteam`, `hruns`, and `vruns` fields.

BT-0061 does not infer venue from scores or row order. It adds a v2 exact team-game
adapter that preserves explicit home/away identity and a canonical frame adapter.

The proof runner must fail closed until the backfill bundle contains
`canonical_team_games`.

No sportsbook price is accepted anywhere in this harness.
