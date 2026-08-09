# Records and Settlement Contract

- Every model output that matters is frozen and versioned before odds-based execution decisions.
- Production and shadow predictions are stored separately.
- A prediction is not a wager.
- A recommended/eligible bet is not a wager.
- Only explicit user confirmation creates a wager record.
- RC1/shadow predictions can never create wagers.
- Preserve the wager's entry odds and original production-model probability permanently.
- Settlements never rewrite the frozen prediction.
- Promotional early payouts are recorded separately from the baseball/model result.
- Actual bankroll, W/L, P/L and ROI use confirmed wagers only.
- Shadow evaluation uses all eligible analyzed games with completed outcomes and never touches bankroll.
