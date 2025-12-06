# Provider Development Guide

Complete guide for developing new betting data providers for the aggregation system.

## Overview

Providers are responsible for fetching betting odds data from various sportsbooks and converting it into a standardized format. The system supports automatic provider discovery and parallel execution.

## Architecture

```
Provider System
├── BaseProvider (Abstract Base Class)
├── Provider Discovery (importlib)
├── Parallel Execution (threading)
└── Data Normalization
```

## Provider Discovery

New providers are automatically discovered through Python's `importlib` system:

1. Create provider directory in `src/providers/`
2. Add `__init__.py` to make it a package
3. Inherit from `BaseProvider`
4. System will automatically discover and load them

```
src/providers/
├── __init__.py           # Contains get_all_providers()
├── base.py              # BaseProvider abstract class
├── draftkings/          # Existing provider
│   ├── __init__.py
│   ├── client.py
│   └── mappings.py
└── yourprovider/         # Your new provider
    ├── __init__.py
    ├── client.py
    └── mappings.py
```

## Creating a New Provider

### Step 1: Create Provider Directory

```bash
mkdir -p src/providers/fanduel
```

### Step 2: Create __init__.py

```python
# src/providers/fanduel/__init__.py
"""FanDuel provider implementation."""

from .client import FanDuelProvider
```

### Step 3: Implement Provider Class

```python
# src/providers/fanduel/client.py
"""FanDuel provider implementation."""

from typing import Dict, List
from ...core.logger import get_logger
from ...core.schemas import StandardizedGame
from ..base import BaseProvider

log = get_logger(__name__)

class FanDuelProvider(BaseProvider):
    """FanDuel betting data provider."""
    
    def __init__(self):
        self.name = "FanDuel"
        self.base_url = "https://sportsbook.fanduel.com"
    
    def get_sports_mapping(self) -> Dict[str, str]:
        """Return mapping from FanDuel sport IDs to standard names."""
        return {
            "1": "NFL",      # NFL
            "2": "NBA",      # NBA  
            "3": "MLB",      # MLB
            "4": "NHL",      # NHL
            "6": "UFC",      # UFC
        }
    
    def fetch_odds(self, sport_id: str) -> List[StandardizedGame]:
        """Fetch odds for the given sport from FanDuel."""
        try:
            log.info(f"Fetching {sport_id} odds from FanDuel")
            
            # 1. Map sport ID to standard name
            sport_name = self.get_sports_mapping().get(sport_id)
            if not sport_name:
                log.warning(f"No mapping for sport ID: {sport_id}")
                return []
            
            # 2. Fetch data from FanDuel API
            api_data = self._fetch_fanduel_data(sport_id)
            
            # 3. Parse and normalize data
            games = self._parse_games(api_data, sport_name)
            
            log.info(f"Successfully parsed {len(games)} games from FanDuel")
            return games
            
        except Exception as e:
            log.error(f"Error fetching FanDuel odds: {e}", exc_info=True)
            return []
    
    def _fetch_fanduel_data(self, sport_id: str) -> Dict:
        """Fetch raw data from FanDuel API."""
        import requests
        
        url = f"{self.base_url}/api/odds/v1/fetch-events"
        params = {
            'sport': sport_id,
            'include': 'markets,events'
        }
        
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        
        return response.json()
    
    def _parse_games(self, api_data: Dict, sport_name: str) -> List[StandardizedGame]:
        """Parse API data into StandardizedGame objects."""
        games = []
        
        events = api_data.get('events', [])
        
        for event in events:
            try:
                game = self._parse_single_game(event, sport_name)
                if game:
                    games.append(game)
            except Exception as e:
                log.error(f"Error parsing game {event.get('id', 'unknown')}: {e}")
        
        return games
    
    def _parse_single_game(self, event: Dict, sport_name: str) -> StandardizedGame:
        """Parse a single game event into StandardizedGame."""
        from datetime import datetime
        
        # Extract basic game info
        game_id = str(event.get('id', ''))
        home_team = event.get('home_team', {}).get('name', '')
        away_team = event.get('away_team', {}).get('name', '')
        
        # Parse start time
        start_time_str = event.get('start_time')
        start_time = None
        if start_time_str:
            try:
                start_time = datetime.fromisoformat(start_time_str.replace('Z', '+00:00'))
            except ValueError:
                log.warning(f"Could not parse start time: {start_time_str}")
        
        # Create standardized game
        game = StandardizedGame(
            sport=sport_name,
            game_id=game_id,
            home_team=home_team,
            away_team=away_team,
            start_time=start_time,
            status=event.get('status', '')
        )
        
        # Parse markets
        markets = event.get('markets', [])
        for market in markets:
            market_name = market.get('name', '')
            selections = market.get('selections', [])
            
            market_data = []
            for selection in selections:
                market_data.append({
                    'name': selection.get('name', ''),
                    'odds': selection.get('odds', {}).get('decimal', 0.0)
                })
            
            if market_data:
                game.add_market(market_name, market_data)
        
        return game
```

### Step 4: Test Your Provider

```python
# tests/test_fanduel_provider.py
import pytest
from src.providers.fanduel.client import FanDuelProvider
from src.core.schemas import StandardizedGame

def test_fanduel_sports_mapping():
    provider = FanDuelProvider()
    mapping = provider.get_sports_mapping()
    
    assert "1" in mapping
    assert mapping["1"] == "NFL"
    assert "2" in mapping
    assert mapping["2"] == "NBA"

def test_fanduel_fetch_odds():
    provider = FanDuelProvider()
    
    # This would need real API integration for full testing
    # For now, we test the structure
    games = provider.fetch_odds("1")  # NFL
    
    assert isinstance(games, list)
    for game in games:
        assert isinstance(game, StandardizedGame)
        assert game.sport == "NFL"
        assert game.game_id != ""
```

## Provider Configuration

### Adding to config.yaml

Update the scheduling configuration to include your provider:

```yaml
# config.yaml
intervals:
  NFL:
    DraftKings: 300
    FanDuel: 300      # Add your provider
    YourProvider: 300
  NBA:
    DraftKings: 600
    FanDuel: 600      # Add your provider
    YourProvider: 600
```

## API Client Implementation

### HTTP Client Best Practices

```python
class ProviderClient:
    def __init__(self, base_url: str, headers: Dict[str, str] = None):
        self.base_url = base_url.rstrip('/')
        self.headers = headers or self._default_headers()
        self.session = requests.Session()
        self.session.headers.update(self.headers)
    
    def _default_headers(self) -> Dict[str, str]:
        """Default headers for API requests."""
        return {
            'User-Agent': 'Betting-Markets-Aggregator/1.0',
            'Accept': 'application/json',
            'Accept-Encoding': 'gzip, deflate',
        }
    
    def fetch_data(self, endpoint: str, params: Dict = None) -> Dict:
        """Fetch data with error handling and retry logic."""
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        
        max_retries = 3
        for attempt in range(max_retries):
            try:
                response = self.session.get(url, params=params, timeout=10)
                response.raise_for_status()
                return response.json()
                
            except requests.exceptions.RequestException as e:
                if attempt == max_retries - 1:
                    log.error(f"Failed to fetch {endpoint} after {max_retries} attempts: {e}")
                    raise
                
                wait_time = 2 ** attempt  # Exponential backoff
                log.warning(f"Attempt {attempt + 1} failed for {endpoint}, retrying in {wait_time}s")
                time.sleep(wait_time)
```

### Rate Limiting and Headers

```python
# src/providers/fanduel/mappings.py
"""FanDuel provider constants and mappings."""

import time
from typing import Dict

# API Configuration
BASE_URL = "https://sportsbook.fanduel.com"
API_TIMEOUT = 10

# Request Headers
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
    'Accept': 'application/json',
    'Accept-Language': 'en-US,en;q=0.9',
    'Accept-Encoding': 'gzip, deflate, br',
    'Connection': 'keep-alive',
    'Upgrade-Insecure-Requests': '1',
}

# Rate Limiting
MIN_REQUEST_INTERVAL = 1.0  # Minimum seconds between requests
_last_request_time = 0

def rate_limit():
    """Implement rate limiting for API calls."""
    global _last_request_time
    current_time = time.time()
    elapsed = current_time - _last_request_time
    
    if elapsed < MIN_REQUEST_INTERVAL:
        time.sleep(MIN_REQUEST_INTERVAL - elapsed)
    
    _last_request_time = time.time()
```

## Data Parsing and Normalization

### StandardizedGame Usage

```python
def parse_provider_data(provider_data: Dict, sport: str) -> List[StandardizedGame]:
    """Parse provider-specific data into standardized format."""
    games = []
    
    for event in provider_data.get('events', []):
        # Create standardized game
        game = StandardizedGame(
            sport=sport,
            game_id=str(event['id']),
            home_team=event['home_team']['name'],
            away_team=event['away_team']['name'],
            start_time=parse_datetime(event['start_time']),
            status=event.get('status', 'upcoming')
        )
        
        # Parse markets
        for market in event.get('markets', []):
            market_name = normalize_market_name(market['name'])
            selections = []
            
            for selection in market.get('selections', []):
                selections.append({
                    'name': selection['name'],
                    'odds': convert_odds(selection['odds']),
                    'line': selection.get('line')  # For spreads/totals
                })
            
            if selections:
                game.add_market(market_name, selections)
        
        games.append(game)
    
    return games

def normalize_market_name(provider_market_name: str) -> str:
    """Normalize market names across providers."""
    name_lower = provider_market_name.lower()
    
    market_mapping = {
        'money line': 'Moneyline',
        'moneyline': 'Moneyline',
        'ml': 'Moneyline',
        'point spread': 'Spread',
        'spread': 'Spread',
        'total': 'Total',
        'over/under': 'Total',
        'o/u': 'Total'
    }
    
    return market_mapping.get(name_lower, provider_market_name)

def convert_odds(provider_odds: Dict) -> float:
    """Convert odds to decimal format."""
    if 'decimal' in provider_odds:
        return float(provider_odds['decimal'])
    elif 'american' in provider_odds:
        american_odds = int(provider_odds['american'])
        if american_odds > 0:
            return (american_odds / 100) + 1
        else:
            return (100 / abs(american_odds)) + 1
    else:
        return 0.0
```

## Error Handling and Logging

### Comprehensive Error Handling

```python
class ProviderError(Exception):
    """Base exception for provider-related errors."""
    pass

class APIError(ProviderError):
    """Raised when API calls fail."""
    pass

class ParsingError(ProviderError):
    """Raised when data parsing fails."""
    pass

def safe_fetch_odds(provider_name: str, fetch_func, sport_id: str) -> List[StandardizedGame]:
    """Safely execute provider fetch with comprehensive error handling."""
    try:
        log.info(f"Starting fetch for {provider_name} - {sport_id}")
        
        games = fetch_func(sport_id)
        
        if not isinstance(games, list):
            raise ParsingError(f"Expected list, got {type(games)}")
        
        valid_games = []
        for game in games:
            if not isinstance(game, StandardizedGame):
                log.warning(f"Invalid game object from {provider_name}: {type(game)}")
                continue
            
            if not game.game_id:
                log.warning(f"Missing game_id from {provider_name}")
                continue
            
            valid_games.append(game)
        
        log.info(f"Successfully fetched {len(valid_games)} valid games from {provider_name}")
        return valid_games
        
    except APIError as e:
        log.error(f"API error for {provider_name}: {e}")
        return []
    except ParsingError as e:
        log.error(f"Parsing error for {provider_name}: {e}")
        return []
    except Exception as e:
        log.error(f"Unexpected error for {provider_name}: {e}", exc_info=True)
        return []
```

## Testing Strategies

### Unit Tests

```python
# tests/providers/test_base_provider.py
import pytest
from unittest.mock import Mock, patch
from src.providers.base import BaseProvider
from src.core.schemas import StandardizedGame

class TestProvider(BaseProvider):
    def get_sports_mapping(self):
        return {"1": "NFL"}
    
    def fetch_odds(self, sport_id):
        return [StandardizedGame(sport="NFL", game_id="123")]

def test_base_provider_interface():
    """Test that BaseProvider enforces interface."""
    with pytest.raises(TypeError):
        BaseProvider()

def test_provider_methods():
    """Test provider methods work correctly."""
    provider = TestProvider()
    
    mapping = provider.get_sports_mapping()
    assert mapping == {"1": "NFL"}
    
    games = provider.fetch_odds("1")
    assert len(games) == 1
    assert games[0].sport == "NFL"
```

### Integration Tests

```python
# tests/providers/test_provider_integration.py
import pytest
from src.core.database import get_connection
from src.providers import get_all_providers

def test_all_providers_discovered():
    """Test that all providers in the directory are discovered."""
    providers = get_all_providers()
    
    assert len(providers) > 0
    provider_names = [p.__class__.__name__ for p in providers]
    
    # Should include at least DraftKings provider
    assert "DraftKingsProvider" in provider_names

def test_provider_database_integration():
    """Test that provider data is correctly stored in database."""
    provider = TestProvider()  # Use a test provider
    games = provider.fetch_odds("1")
    
    # Store in database
    with get_connection() as conn:
        cur = conn.cursor()
        for game in games:
            cur.execute(
                "INSERT INTO games (sport, game_id, home_team, away_team) VALUES (?, ?, ?, ?)",
                (game.sport, game.game_id, game.home_team, game.away_team)
            )
        conn.commit()
    
    # Verify storage
    with get_connection() as conn:
        cur = conn.cursor()
        cur.execute("SELECT COUNT(*) FROM games")
        count = cur.fetchone()[0]
        assert count >= len(games)
```

## Performance Considerations

### Caching

```python
import time
from typing import Dict, Any

class ProviderCache:
    def __init__(self, ttl: int = 300):  # 5 minutes default TTL
        self.cache: Dict[str, Dict[str, Any]] = {}
        self.ttl = ttl
    
    def get(self, key: str) -> Any:
        """Get cached data if not expired."""
        if key in self.cache:
            data, timestamp = self.cache[key]
            if time.time() - timestamp < self.ttl:
                return data
            else:
                del self.cache[key]
        return None
    
    def set(self, key: str, data: Any) -> None:
        """Cache data with timestamp."""
        self.cache[key] = (data, time.time())

# Usage in provider
class FanDuelProvider(BaseProvider):
    def __init__(self):
        super().__init__()
        self.cache = ProviderCache(ttl=300)  # 5 minutes
    
    def fetch_odds(self, sport_id: str) -> List[StandardizedGame]:
        cache_key = f"fanduel_{sport_id}"
        
        # Check cache first
        cached_data = self.cache.get(cache_key)
        if cached_data:
            log.info(f"Using cached data for {sport_id}")
            return cached_data
        
        # Fetch fresh data
        games = self._fetch_and_parse_odds(sport_id)
        
        # Cache the results
        self.cache.set(cache_key, games)
        
        return games
```

### Batch Processing

```python
def batch_fetch_odds(providers: List[BaseProvider], sport_id: str) -> Dict[str, List[StandardizedGame]]:
    """Fetch odds from multiple providers in parallel."""
    from concurrent.futures import ThreadPoolExecutor
    import threading
    
    results = {}
    lock = threading.Lock()
    
    def fetch_provider_odds(provider):
        try:
            games = provider.fetch_odds(sport_id)
            provider_name = provider.__class__.__name__
            
            with lock:
                results[provider_name] = games
            
            return provider_name, games
        except Exception as e:
            log.error(f"Error in batch fetch for {provider.__class__.__name__}: {e}")
            return provider.__class__.__name__, []
    
    with ThreadPoolExecutor(max_workers=len(providers)) as executor:
        futures = [executor.submit(fetch_provider_odds, provider) for provider in providers]
        
        for future in futures:
            future.result()  # Wait for completion and handle any exceptions
    
    return results
```

## Deployment

### Provider Registration

Once your provider is complete:

1. **Add to configuration**: Update `config.yaml` with scheduling intervals
2. **Test integration**: Ensure it works with the orchestration system
3. **Update documentation**: Document any provider-specific configuration
4. **Monitor logs**: Watch for any provider-specific issues

### Configuration Example

```yaml
# config.yaml
intervals:
  NFL:
    DraftKings: 300
    FanDuel: 300
    YourProvider: 300  # New provider
  NBA:
    DraftKings: 600
    FanDuel: 600
    YourProvider: 600  # New provider

# Provider-specific configuration (if needed)
provider_config:
  YourProvider:
    api_key: "your-api-key"  # If needed
    rate_limit: 1.0         # Requests per second
    timeout: 15             # Request timeout
```

## Troubleshooting

### Common Issues

#### Provider Not Discovered

```bash
# Check provider directory structure
find src/providers -name "*.py" -type f

# Verify __init__.py files exist
ls -la src/providers/*/__init__.py
```

#### Import Errors

```python
# Add debug logging to src/providers/__init__.py
def get_all_providers():
    providers = []
    try:
        import importlib
        import pkgutil
        
        # Import the providers package
        providers_package = importlib.import_module('src.providers')
        
        # Walk through all submodules
        for importer, modname, ispkg in pkgutil.iter_modules(providers_package.__path__):
            if not modname.startswith('_'):
                try:
                    module = importlib.import_module(f'src.providers.{modname}')
                    
                    # Look for provider classes
                    for item_name in dir(module):
                        item = getattr(module, item_name)
                        if (isinstance(item, type) and 
                            issubclass(item, BaseProvider) and 
                            item != BaseProvider):
                            providers.append(item())
                            log.debug(f"Discovered provider: {item.__name__}")
                            
                except Exception as e:
                    log.error(f"Failed to import provider {modname}: {e}")
                    
    except Exception as e:
        log.error(f"Error during provider discovery: {e}")
    
    return providers
```

#### API Rate Limiting

```python
def handle_rate_limit(response):
    """Handle rate limiting from provider APIs."""
    if response.status_code == 429:
        retry_after = int(response.headers.get('Retry-After', 60))
        log.warning(f"Rate limited. Waiting {retry_after} seconds.")
        time.sleep(retry_after)
        return True
    return False
```

### Debugging Tools

```python
# Debug provider data structure
def debug_provider_data(provider_data: Dict, provider_name: str):
    """Print provider data structure for debugging."""
    print(f"\n=== {provider_name} Data Structure ===")
    
    def print_structure(data, indent=0):
        prefix = "  " * indent
        if isinstance(data, dict):
            for key, value in data.items():
                print(f"{prefix}{key}: {type(value).__name__}")
                if isinstance(value, (dict, list)) and len(str(value)) < 200:
                    print_structure(value, indent + 1)
        elif isinstance(data, list) and data:
            print(f"{prefix}[{len(data)} items]")
            if len(data) > 0:
                print_structure(data[0], indent + 1)
    
    print_structure(provider_data)

# Usage in your provider
# debug_provider_data(api_data, "FanDuel")
```

## Best Practices Summary

1. **Inherit from BaseProvider**: Always inherit from the abstract base class
2. **Implement required methods**: `get_sports_mapping()` and `fetch_odds()`
3. **Use proper logging**: Never use `print()`, always use `get_logger(__name__)`
4. **Handle errors gracefully**: Don't let provider failures crash the system
5. **Return standardized data**: Always return `List[StandardizedGame]`
6. **Rate limit appropriately**: Don't overwhelm provider APIs
7. **Test thoroughly**: Unit tests, integration tests, and real API tests
8. **Document provider specifics**: Any unique configuration or behavior
9. **Follow naming conventions**: Provider class name should end with "Provider"
10. **Monitor performance**: Log fetch times and success rates

## Example Provider: Complete Implementation

For a complete working example, study the existing `DraftKingsProvider` implementation in `src/providers/draftkings/`. It demonstrates:

- Complex API navigation
- Dynamic template discovery  
- Market parsing and normalization
- Comprehensive error handling
- Logging best practices
- Rate limiting implementation

This guide should enable you to create robust, production-ready providers for the betting markets aggregation system.