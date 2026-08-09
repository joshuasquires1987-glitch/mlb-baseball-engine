# Real MLB State Calculators Contract

These calculators convert historical pregame-available baseball records into live model states.

Rules:
- Every calculation filters to rows strictly before the target game date/time.
- Starter talent uses decayed, shrunk prior performance.
- Expected starter depth uses prior starts only and a separate shorter half-life.
- Team strength/offense/defense use decayed prior team games.
- Bullpen quality uses relief appearances only, with decay and shrinkage.
- No sportsbook price or same-game result may enter state calculation.
- Missing prior history shrinks to league-average neutral state rather than inventing information.
- Calculator hyperparameters are versioned research choices and may not mutate production automatically.
