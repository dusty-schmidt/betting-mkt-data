# API Reference

REST API endpoints for the Betting Markets Data Aggregator service. All endpoints return JSON responses and are served on port 5000.

## Base URL

```
http://localhost:5000/api/v1
```

## Authentication

Currently, all endpoints are open and do not require authentication. Future versions may implement API key-based authentication.

## Endpoints

### GET /games

Retrieve a list of all sports games in the database.

**Endpoint:** `GET /api/v1/games`

**Response Format:**
```json
[
  {
    "sport": "NFL",
    "game_id": "5837741f-bcd2-4d93-8e9e-4f2dd9f3ff9c",
    "home_team": "Kansas City Chiefs",
    "away_team": "Buffalo Bills", 
    "start_time": "2024-12-08T20:20:00"
  },
  {
    "sport": "NBA",
    "game_id": "3f2c5a6e-8b3d-4c7e-9a1f-2d4c6b8e0f3a",
    "home_team": "Los Angeles Lakers",
    "away_team": "Boston Celtics",
    "start_time": "2024-12-09T21:00:00"
  }
]
```

**Response Fields:**

| Field | Type | Description |
|-------|------|-------------|
| `sport` | string | Sport identifier (e.g., "NFL", "NBA", "MLB") |
| `game_id` | string | Unique game identifier |
| `home_team` | string | Home team name |
| `away_team` | string | Away team name |
| `start_time` | string | Game start time in ISO 8601 format |

**Status Codes:**
- `200 OK` - Success
- `500 Internal Server Error` - Database connection error

**Example:**
```bash
curl -X GET http://localhost:5000/api/v1/games
```

---

### GET /arbitrage

Placeholder endpoint for future arbitrage opportunity detection.

**Endpoint:** `GET /api/v1/arbitrage`

**Response Format:**
```json
{
  "message": "Arbitrage endpoint not yet implemented"
}
```

**Status Codes:**
- `200 OK` - Endpoint exists, feature pending
- `501 Not Implemented` - Future implementation when feature is ready

**Example:**
```bash
curl -X GET http://localhost:5000/api/v1/arbitrage
```

---

### GET /status

AI-powered health monitoring endpoint that provides a summary of the system's current status.

**Endpoint:** `GET /api/v1/status`

**Response Format:**
Plain text (Markdown format) with system health information:

```markdown
## System Status Report

**Overall Status:** 🟢 Healthy

**Data Collection:**
- NFL Games: 15 active
- NBA Games: 12 active  
- Recent Updates: 2 minutes ago

**System Health:**
- Scheduler: Running (4 threads)
- Database: Connected (betting_markets.db)
- Recent Errors: 0

**Performance:**
- API Response Time: ~50ms average
- Last Full Sync: 3 minutes ago
```

**Status Codes:**
- `200 OK` - System healthy or operational
- `503 Service Unavailable` - If system cannot generate status

**Response Headers:**
```
Content-Type: text/plain; charset=utf-8
```

**Example:**
```bash
curl -X GET http://localhost:5000/api/v1/status
```

## Error Handling

### Standard Error Response

All endpoints may return standard error responses:

```json
{
  "error": {
    "code": "DATABASE_ERROR",
    "message": "Unable to connect to database",
    "details": "Connection timeout after 10 seconds"
  },
  "timestamp": "2024-12-06T06:51:50.707Z"
}
```

### Common Error Codes

| Code | HTTP Status | Description |
|------|-------------|-------------|
| `DATABASE_ERROR` | 500 | Database connection or query failure |
| `SCHEDULER_ERROR` | 500 | Background scheduler malfunction |
| `PROVIDER_ERROR` | 502 | Upstream provider API failure |
| `VALIDATION_ERROR` | 400 | Invalid request parameters |

## Rate Limiting

Currently, there are no rate limits implemented. In production, consider implementing:
- Request rate limiting per IP
- API key quotas
- Circuit breakers for upstream providers

## Pagination

The `/games` endpoint currently returns all games without pagination. For production use with large datasets, consider implementing:

- Query parameters: `?limit=50&offset=0`
- Response format with metadata:
```json
{
  "games": [...],
  "pagination": {
    "total": 1250,
    "limit": 50,
    "offset": 0,
    "has_next": true
  }
}
```

## Filtering and Querying

Future enhancements may include:

- **By Sport:** `GET /api/v1/games?sport=NFL`
- **By Date Range:** `GET /api/v1/games?start_date=2024-12-06&end_date=2024-12-08`
- **Search:** `GET /api/v1/games?search=Chiefs`

## Versioning

The API uses URL versioning (`/api/v1/`) for backward compatibility. When breaking changes are introduced, increment the version number (e.g., `/api/v2/`).

## SDK Examples

### Python Client Example

```python
import requests

class BettingAPI:
    def __init__(self, base_url="http://localhost:5000/api/v1"):
        self.base_url = base_url
    
    def get_games(self):
        """Retrieve all games."""
        response = requests.get(f"{self.base_url}/games")
        response.raise_for_status()
        return response.json()
    
    def get_status(self):
        """Get system status."""
        response = requests.get(f"{self.base_url}/status")
        response.raise_for_status()
        return response.text
    
    def get_arbitrage(self):
        """Check for arbitrage opportunities."""
        response = requests.get(f"{self.base_url}/arbitrage")
        response.raise_for_status()
        return response.json()

# Usage
api = BettingAPI()
games = api.get_games()
status = api.get_status()
```

### JavaScript/Node.js Client Example

```javascript
class BettingAPI {
    constructor(baseUrl = 'http://localhost:5000/api/v1') {
        this.baseUrl = baseUrl;
    }
    
    async getGames() {
        const response = await fetch(`${this.baseUrl}/games`);
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        return await response.json();
    }
    
    async getStatus() {
        const response = await fetch(`${this.baseUrl}/status`);
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        return await response.text();
    }
    
    async getArbitrage() {
        const response = await fetch(`${this.baseUrl}/arbitrage`);
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        return await response.json();
    }
}

// Usage
const api = new BettingAPI();
const games = await api.getGames();
const status = await api.getStatus();
```

## Testing with cURL

### Basic Usage

```bash
# Get all games
curl -X GET http://localhost:5000/api/v1/games \
  -H "Accept: application/json"

# Get system status
curl -X GET http://localhost:5000/api/v1/status

# Check arbitrage (placeholder)
curl -X GET http://localhost:5000/api/v1/arbitrage
```

### Withbash
#!/bin/bash

API_BASE="http://localhost:5000/api/v1"

# Test all endpoints
endpoints=("games" "arbitrage" "status")

for endpoint in "${endpoints[@ Error Handling

```]}"; do
    echo "Testing /api/v1/$endpoint..."
    
    response=$(curl -s -w "\n%{http_code}" "http://localhost:5000/api/v1/$endpoint")
    http_code=$(echo "$response" | tail -n1)
    body=$(echo "$response" | head -n -1)
    
    if [[ "$http_code" -eq 200 ]]; then
        echo "✅ $endpoint: OK"
    else
        echo "❌ $endpoint: HTTP $http_code"
        echo "Response: $body"
    fi
    echo ""
done
```

## Production Considerations

### Security

- Implement API key authentication
- Add rate limiting middleware
- Enable HTTPS/TLS
- Add CORS headers if needed for web applications
- Implement input validation and sanitization

### Performance

- Add response caching
- Implement database connection pooling
- Add response compression
- Consider pagination for large datasets

### Monitoring

- Log all API requests and responses
- Monitor response times and error rates
- Set up alerts for high error rates
- Track API usage patterns