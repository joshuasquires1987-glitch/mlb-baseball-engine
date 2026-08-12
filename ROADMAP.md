# MLB Baseball Engine — Roadmap

## Operating principle

Build the laboratory before trusting the experiment.

The roadmap prioritizes reproducible historical reconstruction and probability evaluation before expanding model complexity. Baseball Engine v1.1 remains frozen while all new modeling work is developed as challengers.

## Phase 0 — Governance and specifications

**Status: substantially complete**

- Freeze v1.1 production champion.
- Separate baseball probabilities from sportsbook/market information.
- Define point-in-time backtest rules.
- Define five-season target historical window.
- Define primary evaluation metrics.
- Establish challenger-only model-change process.
- Establish Google Sheet research/specification control plane.
- Establish GitHub executable source of truth.

**Exit criterion:** governance rules and component specifications are explicit and versioned.

## Phase 1 — Historical reconstruction infrastructure

**Status: active / late stage**

Completed or substantially implemented:
- historical schedule acquisition
- chunked MLB schedule runtime
- historical final-feed parsing
- certified pregame lineup recovery
- platoon snapshot enrichment
- starter/team/bullpen state calculators
- point-in-time state assembly
- replay test suite
- manual structural replay workflow

Current work:
- harden cross-stage schema contracts
- validate missing/final-score handling
- complete full structural replay without unhandled exceptions
- produce auditable replay-failure report

**Exit criterion:** one deterministic run generates a complete structural probability ledger with documented coverage and no unhandled data exceptions.

## Phase 2 — Frozen v1.1 benchmark

**Status: next**

1. Generate structural v1.1 probabilities for every eligible historical game.
2. Join predictions to final outcomes.
3. Produce:
   - Brier score
   - log loss
   - calibration table/curve
   - probability-band counts
   - home/away diagnostics
   - favorite/underdog diagnostics
   - starter/data-quality diagnostics
4. Record coverage and exclusions.
5. Store benchmark run metadata in the Sheet and/or committed run summary.

**Exit criterion:** a reproducible benchmark report exists and can be regenerated from code.

## Phase 3 — Parameter-estimation framework

**Status: specified, early implementation**

Build expanding/rolling historical training utilities for parameters that must not be hand-selected from hindsight.

Targets include:
- shrinkage strengths
- recency half-lives
- workload priors
- league event-rate priors
- Negative Binomial dispersion
- selected interaction coefficients

**Exit criterion:** parameters used by challengers are estimated only from information available before each validation period.

## Phase 4 — Component challengers

**Status: specified**

Develop components independently so incremental value can be measured.

### Starting pitcher
- posterior K talent
- posterior BB talent
- contact-quality suppression
- current-state/change-point detection
- workload distribution
- times-through-order deterioration
- pitcher/lineup pitch-mix interactions

### Offense
- hitter latent talent
- lineup posterior
- batting-order weighting
- handedness/platoon effects
- pitch-type matchup interactions

### Bullpen
- reliever talent
- availability/fatigue
- expected deployment
- starter-to-bullpen workload mixture

### Defense/context
- defensive run prevention
- catcher effects where supportable
- park
- weather
- home field
- travel/rest/circadian

**Exit criterion:** each challenger can be toggled and evaluated against an otherwise identical baseline.

## Phase 5 — Run-distribution probability engine

**Status: specified**

1. Estimate `lambda_home` and `lambda_away`.
2. Fit Negative Binomial dispersion on training data only.
3. Generate team run distributions.
4. Test independence versus shared-game-environment challenger.
5. Resolve regulation ties explicitly into game win probability.
6. Compare against Poisson and external sanity benchmarks.

**Exit criterion:** complete probability engine produces stable, valid win probabilities and beats or matches the structural champion on held-out proper scoring metrics.

## Phase 6 — Uncertainty propagation

**Status: specified**

Monte Carlo/posterior sampling over uncertain inputs:
- probable starter scenarios
- starter workload
- lineup state
- player talent
- bullpen state
- context

Outputs:
- mean win probability
- interval width
- uncertainty/data-quality classification
- tail probabilities where useful

Initially use uncertainty descriptively. Any uncertainty-aware staking change is a separate execution challenger.

**Exit criterion:** uncertainty is reproducible, calibrated enough to be diagnostically useful, and does not contaminate core probability evaluation.

## Phase 7 — Calibration

**Status: specified**

Compare chronological calibration approaches:
- logistic/Platt-style
- isotonic
- Bayesian/other challenger methods

Selection occurs on validation data and final reporting occurs on untouched later data.

**Exit criterion:** calibrated challenger improves probability meaning without overfit.

## Phase 8 — Champion/challenger validation

**Status: future**

For each serious challenger:
- identical historical snapshots
- identical eligible games
- Brier comparison
- log-loss comparison
- calibration comparison
- subgroup stability
- uncertainty and failure-rate review
- reproducibility check

Promotion requires explicit review and a new model version.

## Phase 9 — Execution research

**Status: parallel, separate**

After independent probabilities exist:
- compare against recorded Bet365 prices
- track edge buckets
- track confirmed wagers separately
- measure CLV
- research optimal bet timing
- test staking approaches

Execution research may improve the price paid or bankroll strategy but cannot change baseball probabilities unless separately implemented and validated as a baseball-model challenger.

## Immediate queue

1. Fix structural replay snapshot timestamp contract.
2. Rerun `V1.1 Structural Replay`.
3. Audit replay failures and coverage.
4. Generate benchmark probability ledger.
5. Build benchmark scoring/report script.
6. Record benchmark run.
7. Begin first scientifically isolated component challenger.

## Definition of progress

Progress is not measured by number of bets or recent wins.

Progress means:
- more eligible games reconstructed correctly
- fewer unexplained data failures
- stronger point-in-time guarantees
- reproducible probability ledgers
- better Brier/log loss/calibration on held-out games
- clearer lineage and model governance
