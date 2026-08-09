# BT-0060 Exact Bundle → Probability Contract

The production probability path is now explicitly separated from price evaluation.

Sequence:
1. require a fully green exact-history bundle
2. convert exact historical records to assembler inputs
3. build `PregameFacts`
4. build normalized model inputs
5. reject unresolved red integrity
6. run frozen v1.1 and shadow RC1 through `DualModelRunner.predict`
7. freeze the probability pair
8. record that no sportsbook price has been seen
9. only a later execution-layer call may compare the frozen v1.1 probability with Bet365

Important architecture rule:
`LiveWorkflow.analyze_game` requires a price, so it is not the probability-generation boundary.
`ProbabilityOnlyRunner` is the clean blind-to-market boundary.

No model weights are changed by this bridge.
