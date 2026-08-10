# BT-0068 Verified Pregame Evidence Contract

This layer verifies facts; it does not invent model scores.

From MLB's official live feed it records:
- both teams
- recorded starters
- both batting orders
- lineup confirmation
- venue
- raw weather condition, temperature, and wind
- explicit source provenance

Important distinction:

`venue verified` is not the same thing as `park_score verified`.

`weather observation verified` is not the same thing as `weather_score verified`.

The current v1.1 pipeline accepts numeric park/weather/travel/platoon scores but the repository contains no frozen, governed transformation specification for producing those scores from raw facts.

Therefore BT-0068 must never mark those scores verified merely because raw data exists, and it must never substitute zero for unknown.

This is deliberate fail-closed behavior under the frozen-model governance rules.
