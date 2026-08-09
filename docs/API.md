# MLB Baseball Engine API Documentation

## Base URL

```
http://localhost:3000/api
```

## Endpoints

### Chat Endpoints

#### POST /chat/message
Send a message to the ChatGPT baseball analyzer.

**Request:**
```json
{
  "message": "Who are the top 5 outfielders this season?",
  "conversationHistory": [
    { "role": "user", "content": "Who won the World Series?" },
    { "role": "assistant", "content": "The answer..." }
  ]
}
```

**Response:**
```json
{
  "message": "The top 5 outfielders this season are...",
  "usage": {
    "prompt_tokens": 50,
    "completion_tokens": 150,
    "total_tokens": 200
  }
}
```

#### POST /chat/analyze-player
Get detailed analysis of a player's performance.

**Request:**
```json
{
  "playerData": {
    "name": "Aaron Judge",
    "position": "OF",
    "team": "NYY",
    "stats": {
      "games": 130,
      "homeRuns": 37,
      "avg": 0.276
    }
  }
}
```

**Response:**
```json
{
  "analysis": "Aaron Judge is having an excellent season..."
}
```

### Stats Endpoints

#### GET /stats/players
Get a list of all players with available stats.

**Response:**
```json
{
  "players": [...],
  "count": 5
}
```

#### GET /stats/player/:id
Get statistics for a specific player.

**Response:**
```json
{
  "name": "Aaron Judge",
  "position": "OF",
  "team": "NYY",
  "stats": {...}
}
```

## Error Handling

All errors return JSON in the following format:

```json
{
  "error": "Error message describing what went wrong"
}
```

## Rate Limiting

Currently no rate limiting implemented. Will be added in future versions.

## Authentication

Currently no authentication required. Will be added for production deployment.
