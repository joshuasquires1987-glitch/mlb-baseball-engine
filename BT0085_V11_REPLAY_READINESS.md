# BT-0085 v1.1 Historical Replay Readiness Audit

Purpose:
Prevent a false "true challenger" comparison.

The repository already defines the frozen v1.1 probability function:
a weighted feature sum passed through a sigmoid.

However, historical replay is only valid if each of the ten v1.1 feature
inputs can be rebuilt as they would have existed pregame.

This ticket inventories the production contract and explicitly blocks
using RC2 context variables as substitutes for v1.1 feature slots unless
their normalization is proven identical.

No bets, stakes, weights, or production code are changed.
