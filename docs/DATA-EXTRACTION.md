# Data Extraction

## Overview
The provider system fetches odds data from external sources and normalizes it into a common format.

## Architecture

```
┌──────────────┐
│  Scheduler   │ (reads config.yaml)
└──────┬───────┘
       │
       ▼
┌──────────────┐
│ Orchestrator │ (runs providers in parallel)
└──────┬───────┘
       │
       ├─────────────┬─────────────┬──────────────┐
       ▼             ▼             ▼              ▼
┌─────────────┐ ┌──────────┐ ┌──────────┐  ┌──────────┐
│ DraftKings  │ │ FanDuel  │ │  Bovada  │  │  Custom  │
└─────────────┘ └──────────┘ └──────────┘  └──────────┘
       │             │             │              │
       └─────────────┴─────────────┴──────────────┘
                     │
                     ▼
              ┌─────────────┐
              │  Database   │
              └─────────────┘
```

## Provider Contract

All providers must implement `BaseProvider`:

```python
from abc import ABC, abstractmethod
from src.core.schemas import StandardizedGame

class BaseProvider(ABC):
    @abstractmethod
    def get_sports_mapping(self) -> dict:
        """Map provider sport IDs to standard names."""
        pass
    
    @abstractmethod
    def fetch_odds(self, sport_id: str) -> list[StandardizedGame]:
        """Fetch and normalize odds data."""
        pass
```

## Provider Structure

```
src/providers/<provider_name>/
├── __init__.py      # Provider class
├── client.py        # HTTP client
└── parser.py        # Response normalization
```

### Example: DraftKings

#### `__init__.py`
```python
from ..base import BaseProvider
from .client import DraftKingsClient
from .parser import parse_odds

class DraftKingsProvider(BaseProvider):
    def __init__(self):
        self.client = DraftKingsClient()
    
    def get_sports_mapping(self) -> dict:
        return {"100": "NFL", "200": "NBA"}
    
    def fetch_odds(self, sport_id: str) -> list[StandardizedGame]:
        raw = self.client.get_odds(sport_id)
        return parse_odds(raw)
```

#### `client.py`
```python
import requests

class DraftKingsClient:
    BASE_URL = "https://api.draftkings.com/odds"
    
    def get_odds(self, sport_id: str):
        response = requests.get(f"{self.BASE_URL}/{sport_id}")
        return response.json()
```

#### `parser.py`
```python
from src.core.schemas import StandardizedGame

def parse_odds(raw_data) -> list[StandardizedGame]:
    games = []
    for item in raw_data:
        game = StandardizedGame(
            sport=item["sport"],
            game_id=item["id"],
            home_team=item["home"],
            away_team=item["away"],
            start_time=item["start"]
        )
        games.append(game)
    return games
```

## Dynamic Discovery

Providers are automatically discovered at runtime:

1. `get_all_providers()` scans `src/providers/`
2. Imports each module
3. Finds classes inheriting from `BaseProvider`
4. Instantiates and returns them

**No manual registration needed!**

## Configuration

`config.yaml`:
```yaml
intervals:
  NFL:
    DraftKings: 300  # fetch every 5 minutes
    FanDuel: 600     # fetch every 10 minutes
```

## Error Handling

Providers should handle their own errors:

```python
def fetch_odds(self, sport_id: str) -> list[StandardizedGame]:
    try:
        raw = self.client.get_odds(sport_id)
        return parse_odds(raw)
    except requests.RequestException as e:
        logger.error(f"Failed to fetch from DraftKings: {e}")
        return []  # Return empty list, don't crash
```

The orchestrator will log failures but continue with other providers.

## Best Practices

1. **Respect Rate Limits**: Use `time.sleep()` if needed
2. **Use Headers**: Rotate user agents (see `src/core/headers.py`)
3. **Handle Pagination**: If API returns paginated data
4. **Normalize Data**: Always return `StandardizedGame` objects
5. **Log Everything**: Use `logger = get_logger(__name__)`

## Testing

```python
# tests/test_providers.py
def test_draftkings_provider():
    provider = DraftKingsProvider()
    
    # Test sports mapping
    mapping = provider.get_sports_mapping()
    assert "100" in mapping
    
    # Test odds fetching (mock the HTTP call)
    with patch.object(provider.client, 'get_odds') as mock:
        mock.return_value = [...]
        games = provider.fetch_odds("NFL")
        assert len(games) > 0
```

## Future Enhancements
- Async/await for parallel HTTP requests
- Caching layer for repeated requests
- Webhook support for real-time updates
- Provider health monitoring
