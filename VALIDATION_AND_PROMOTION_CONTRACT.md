# Validation and Promotion Contract

Validation tracks sample size, wins/losses, win rate, average posted implied probability,
average model probability, average predicted edge, realized edge where defined, dollars staked,
P/L, ROI, CLV, Brier score, log loss, and Kelly performance.

Required segmentation includes +3-5pp, +5-8pp, +8+pp edge buckets; favorite/underdog;
home/away; implied-price band; starting-pitcher context; uncertainty/confidence; and model version.

RC1 shadow promotion gate:
- minimum 500 live shadow games
- zero unresolved integrity failures
- RC1 Brier no worse than v1.1
- acceptable calibration
- no catastrophic segment failure
- explicit human approval

Reaching the gate never promotes RC1 automatically.
