# BT-0079 Historical Pregame Lineup Timecode Probe

Purpose:
Determine whether MLB's historical timecoded live feed can supply a
certified pregame batting order without reading the completed-game order.

Method:
1. Sample 120 completed games across the 2025 audit period.
2. Request MLB's historical feed timestamps for each game.
3. Select the latest available timestamp at least 60 seconds before the
   scheduled game time.
4. Request the live feed at exactly that historical timecode.
5. Inspect only that timecoded state's boxscore battingOrder.
6. Mark the game recoverable only if both clubs already have exactly nine
   distinct players in batting order.

Forbidden:
- current/completed live-feed fallback
- final boxscore battingOrder fallback
- reconstructing starters from first plate appearances
- substitutions or postgame roster state
- filling a missing lineup with zero or a projected lineup

This probe does NOT calculate platoon_lineup_delta.
It only answers whether certified pregame starters can be recovered.

If recovery is strong, the next ticket will turn these point-in-time
orders into a governed snapshot registry and separately define the
platoon/lineup scoring feature.
