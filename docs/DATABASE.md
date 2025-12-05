# Database Design

## Overview
SQLite database for storing games and odds with support for historical tracking.

## Schema

### `games` Table
Stores unique sporting events.

| Column | Type | Description |
|--------|------|-------------|
| `id` | INTEGER PRIMARY KEY | Auto-increment ID |
| `sport` | TEXT | Sport name (NFL, NBA, etc.) |
| `game_id` | TEXT | Provider-agnostic game identifier |
| `home_team` | TEXT | Home team name |
| `away_team` | TEXT | Away team name |
| `start_time` | TEXT | Game start time (ISO 8601) |

**Unique Constraint**: `(sport, game_id)`

### `odds` Table
Stores odds data with provider attribution.

| Column | Type | Description |
|--------|------|-------------|
| `id` | INTEGER PRIMARY KEY | Auto-increment ID |
| `game_id` | INTEGER | Foreign key to `games.id` |
| `provider` | TEXT | Provider name (DraftKings, etc.) |
| `market` | TEXT | Market type (moneyline, spread, etc.) |
| `odds` | REAL | Odds value |

**Foreign Key**: `game_id` → `games.id`

## Data Models

### Python Models (`src/core/models.py`)
```python
@dataclass
class BaseDataModel:
    id: int | None = None

@dataclass
class Game(BaseDataModel):
    sport: str
    game_id: str
    home_team: str
    away_team: str
    start_time: datetime | None

@dataclass
class Odds(BaseDataModel):
    game_id: int
    provider: str
    market: str
    odds: float
```

### Pydantic Schemas (`src/core/schemas.py`)
```python
class StandardizedGame(BaseModel):
    sport: str
    game_id: str
    home_team: str | None
    away_team: str | None
    start_time: datetime | None
```

## Usage

### Initialization
```python
from src.core.database import init_db
init_db()  # Creates tables if they don't exist
```

### Querying
```python
from src.core.database import get_connection

with get_connection() as conn:
    cur = conn.cursor()
    cur.execute("SELECT * FROM games WHERE sport = ?", ("NFL",))
    games = cur.fetchall()
```

## Environment Variables
- `DB_PATH`: Override default database location (for Docker volumes)

## Future Enhancements
- Add timestamps for odds (track line movement)
- Add indexes for common queries
- Consider partitioning by date for large datasets
