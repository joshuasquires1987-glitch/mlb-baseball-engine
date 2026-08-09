# Exact Boxscore History Contract

Production history must come from exact game-level fields.

The MLB boxscore adapter accepts completed pregame historical boxscores and extracts:
- stable pitcher ID
- recorded starter flag
- exact batters faced
- exact innings pitched converted to outs
- exact runs allowed
- exact relief appearances

Rules:
- a row missing BF, IP, or runs is not silently completed
- starter history is verified against the recorded probable/starting pitcher field
- relief history contains pitchers who were not the recorded starter
- only rows strictly before the target game enter model state
- duplicate game/pitcher/team rows are rejected by the store
- sportsbook data never enters this layer

This provides the exact BF field required by the frozen starter and bullpen state calculators.
