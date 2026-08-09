# MLB Baseball Engine

Version-controlled home for the MLB Baseball Engine.

## Model status
- **v1.1** — frozen production specification.
- **v1.2-RC1** — frozen shadow-only candidate.

## Core separation
1. Baseball probabilities are created independently of sportsbook prices.
2. Bet365 prices enter only after probabilities are frozen.
3. User-supplied Bet365 screenshots are authoritative executable prices.
4. Only explicitly confirmed wagers enter actual W/L, P/L, ROI, bankroll, and betting win rate.
5. Research measurement may be automated; production model mutation may not.

## Live workflow
A screenshot/chat workflow should parse only supplied Bet365 games, gather pregame baseball information, build v1.1 and RC1 independently of odds, freeze both probabilities, then apply prices downstream. v1.1 alone controls production picks/stakes until explicit RC1 promotion.
