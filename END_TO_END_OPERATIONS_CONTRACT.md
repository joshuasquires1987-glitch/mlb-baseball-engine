# End-to-End Operations Contract

The operational sequence is:

1. User supplies Bet365 prices.
2. Gather current baseball inputs independently of those prices.
3. Build v1.1 production and v1.2-RC1 shadow probabilities.
4. Freeze both predictions.
5. Compare frozen v1.1 probability with intact Bet365 implied probability.
6. Apply integrity checks and the +3pp minimum edge rule.
7. Calculate Half-Kelly stake from the frozen production probability only.
8. A candidate remains only a recommendation until the user explicitly confirms a wager.
9. Confirmed wagers enter the wager ledger with permanent entry price and original model probability.
10. Settlement updates actual betting P/L and bankroll without rewriting predictions.
11. Completed game outcomes score both production and shadow predictions.
12. Daily retrospective and validation metrics are updated.
13. RC1 remains shadow-only until the formal review gate is satisfied and explicit human approval occurs.

No sportsbook price may alter the baseball probability model.
No shadow-model output may alter a production wager.
No retrospective or validation result may automatically mutate production weights.
