# Live Screenshot Workflow Contract

- Analyze only games with user-supplied Bet365 prices.
- Odds are downstream only; they never enter probability construction.
- Build and freeze v1.1 production and v1.2-RC1 shadow probabilities independently.
- v1.1 alone controls picks and Half-Kelly stakes.
- Starter change forces a complete rerun.
- Lineup uncertainty raises uncertainty but does not automatically block betting.
- One reliable weather source is sufficient.
- Umpire is nice-to-have; missing data never gets fabricated.
- Maintain green/yellow/red information-status reporting.
- Keep first and latest Bet365 snapshots only.
- Predictions and wagers remain separate ledgers.
- Only explicit user wager confirmation enters actual betting results.
