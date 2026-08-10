# BT-0069 Context Calibration Challenger Contract

This package does not change v1.1 or frozen v1.2-RC1.

It creates research infrastructure for a future context-scoring challenger.

Rules:
1. No hand-selected park/weather/travel/platoon score may be promoted into production.
2. Raw context facts must first be converted into explicit numeric research features.
3. Coefficients must be estimated on historical training games.
4. Evaluation must use a separate chronological holdout.
5. Minimum training sample: 500 games.
6. Minimum holdout sample: 150 games.
7. Challenger must improve holdout log loss relative to the identical model with context terms zeroed.
8. Coefficients are bounded to catch unstable or malformed calibration.
9. Passing the gate permits shadow review only.
10. Production promotion remains false until explicit governance review and a new model version.

Initial coefficient template values are `null` by design. Unknown is not zero.

This keeps the successful NYM@PIT blind artifact preserved and prevents that single matchup from influencing context formula design.
