# Unified Live Pipeline Contract

The live pipeline sequence is:

1. ingest current schedule/starter/lineup/weather/roster/park information
2. convert it to a `MatchupDefinition`
3. assemble strictly prior historical starter/team/bullpen state
4. create `PregameFacts`
5. build normalized v1.1 and RC1 features
6. calculate and freeze both model probabilities
7. only then accept Bet365 prices
8. calculate implied probability, edge, eligibility and Half-Kelly from v1.1 only
9. RC1 remains shadow-only

Sportsbook prices are forbidden from every stage before the execution layer.
Any starter change requires a fresh run beginning at current-game ingestion.
