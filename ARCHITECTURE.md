# MLB Baseball Engine — Architecture

## Purpose

MLB Baseball Engine is a reproducible, point-in-time MLB win-probability system. Its core objective is to estimate baseball probabilities independently of sportsbook prices, then evaluate those probabilities with proper scoring rules and calibration. Betting, market-price, CLV, and timing research sit downstream from the baseball model.

## Governance Boundary

Baseball Engine v1.1 is the frozen production champion. Production weights are not mutated automatically. Infrastructure and data-integrity fixes may be applied without creating a new model version when they do not change baseball logic. Any change to features, transformations, weights, probability generation, or calibration is a challenger until it passes leakage-safe historical evaluation and an explicit promotion decision.

## Source of Truth

- GitHub repository: executable implementation, tests, workflows, data contracts, and generated artifacts.
- Google Sheet `MLB Baseball Engine — Model, Challenger & Betting Research`: model specifications, research hypotheses, governance, backtest design, validation, lineage, and betting/execution research.

## System Layers

### 1. Historical data acquisition

Historical MLB schedules, final feeds, lineups, pitchers, team results, and other source-specific observations are collected with explicit timestamps and source lineage.

Historical records are not assumed valid merely because a source labels them final. Required fields must be validated before entering replay state.

### 2. Point-in-time snapshot layer

The system reconstructs what could have been known before a game.

Examples:
- probable starter identity
- pregame batting order
- prior pitching history
- prior team performance
- bullpen history
- context fields available at the prediction timestamp

Historical snapshots must never be replaced with information learned after first pitch.

### 3. State calculators

Current structural modules include:

- `StarterStateCalculator`
- `TeamStateCalculator`
- `BullpenStateCalculator`
- feature normalization utilities

State calculators consume only observations strictly before the target cutoff. They use recency weighting and shrinkage so sparse samples do not receive full raw-rate weight.

### 4. Game-state assembly

`RealGameStateAssembler` combines starter, team, bullpen, lineup/integrity flags, and context into a single pregame fact bundle.

This layer is responsible for keeping component ownership explicit so the same baseball effect is not counted in multiple buckets.

### 5. Frozen v1.1 structural probability path

The current historical benchmark reconstructs the structural v1.1 logic:

historical state -> normalized feature advantages -> frozen v1.1 weights -> weighted score -> sigmoid -> home/away win probability.

This replay is explicitly labelled `v1.1-structural-default-replay` and is not represented as an exact historical reproduction of every live v1.1 probability when unavailable historical inputs are defaulted.

### 6. Next-generation probability architecture

The target architecture in the model specification moves beyond a direct weighted sigmoid.

Expected direction:

offense posterior
+ opposing starter run-prevention distribution
+ expected starter workload
+ deployable bullpen distribution
+ validated matchup interactions
+ defense/catcher contribution
+ park/weather/home/travel context

-> team expected run rate

For each team, the engine will estimate a scoring distribution. The primary specified candidate is Negative Binomial with dispersion estimated on training data only.

The joint score model then produces the official independent win probability, including explicit treatment of regulation ties/extra innings.

### 7. Uncertainty propagation

Future challenger architecture should propagate uncertainty in:
- starter identity
- starter talent
- starter workload
- lineup state
- hitter talent
- bullpen availability
- context

The output becomes a probability distribution or interval rather than a falsely precise point estimate alone.

### 8. Calibration

Calibration is fit only on earlier out-of-sample forecasts and evaluated chronologically on later held-out periods.

Calibration must never use the target game's outcome or future seasons to improve an earlier forecast.

### 9. Evaluation

Every eligible reconstructed prediction is scored, not only games that would have become bets.

Primary metrics:
- Brier score
- log loss
- calibration/reliability
- subgroup diagnostics

Relevant subgroups include season, home/away, favorite/underdog, probability band, starter context, uncertainty/data quality, and model version.

Betting ROI, CLV, and staking results are tracked separately.

## Leakage Rules

1. All rolling features end before the target game.
2. Same-calendar-day results are conservatively excluded from current structural replay state.
3. Starter identity must reflect pregame knowledge, not the eventual starter discovered later.
4. Lineups may only be used when timestamped before the prediction cutoff.
5. Priors and hyperparameters must be fit without future seasons.
6. Score-distribution parameters are estimated on training periods only.
7. Calibration is chronological.
8. Sportsbook prices never enter baseball probability construction.

## Challenger Contract

A challenger must be compared with the champion on the same eligible games and the same information state except for the single method or feature under investigation.

No challenger is promoted automatically.

## Execution Layer

After the baseball engine freezes a probability, sportsbook prices may be used to calculate:
- intact implied probability
- expected edge
- stake sizing
- CLV
- timing research

Market information must not flow backward into the baseball probability engine.

## Reproducibility

Every material run should record:
- code/model version
- source/data version where available
- prediction timestamp
- feature availability state
- defaults/missingness
- replay failures
- number of eligible games
- probability output
- evaluation metrics

Generated artifacts should be sufficient to audit how a reported metric was produced.
