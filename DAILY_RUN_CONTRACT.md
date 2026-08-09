# Daily Run Contract

- First run occurs when the user supplies Bet365 screenshot(s), ideally before the first pitch of game one.
- Analyze only games represented in the supplied Bet365 data.
- Lineups are gathered as early as possible; uncertain lineups increase uncertainty but do not automatically block betting.
- Starting pitcher confirmation has higher integrity priority than lineup confirmation.
- Starter change after a frozen prediction forces a complete game rerun.
- Maintain green/yellow/red information status.
- One reliable weather source is sufficient.
- Umpire is nice-to-have and never fabricated.
- Missing nonessential variables do not block EV analysis; missingness is recorded as data.
- Keep only the first and latest useful price snapshot for each game/day.
- End-of-day retrospective assigns Process Grade A-F, Prediction Grade A-F, Variance Rating 1-5.
- Retrospective classification may include model error, missing information, market superiority, and normal variance.
- Retrospective measurement never automatically mutates the model.
