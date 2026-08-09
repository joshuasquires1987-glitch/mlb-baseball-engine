# Current-Game Ingestion Contract

This layer converts live public baseball information into a `MatchupDefinition`.

Required source categories:
- MLB schedule/game metadata
- probable/confirmed starters
- lineup status
- one reliable weather source
- material roster/injury news
- park identity/context

Rules:
- source fetch timestamps are preserved
- stale data is downgraded automatically
- starters require both an ID and fresh source data to be marked confirmed
- lineup confirmation requires actual lineup data and freshness
- weather/roster status requires fresh sources
- missing/stale data becomes uncertainty; it is never fabricated
- sportsbook prices are not accepted
