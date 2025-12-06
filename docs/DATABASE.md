# Database Guide

Complete reference for the betting markets database system, including schema design, operations, and best practices.

## Overview

The betting markets aggregator uses SQLite as its database backend, providing a simple, file-based solution that's perfect for development and small-scale production deployments.

## Database Location

- **Default Path:** `betting_markets.db` (in project root)
- **Environment Override:** `DB_PATH` environment variable
- **Runtime Path:** `src/betting_markets.db`

```python
# From src/core/database.py
DB_PATH = Path(_env_path) if _env_path else Path(__file__).parent.parent / "betting_markets.db"
```

## Schema Design

### Table: games

Stores normalized game information across all sports and providers.

```sql
CREATE TABLE games (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    sport TEXT NOT NULL,
    game_id TEXT NOT NULL,
    home_team TEXT,
    away_team TEXT,
    start_time TEXT,
    UNIQUE(sport, game_id)
);
```

#### Fields

| Field | Type | Description | Constraints |
|-------|------|-------------|-------------|
| `id` | INTEGER PRIMARY KEY | Auto-incrementing primary key | AUTOINCREMENT |
| `sport` | TEXT | Sport identifier (e.g., "NFL", "NBA") | NOT NULL |
| `game_id` | TEXT | Provider-specific game identifier | NOT NULL, UNIQUE with sport |
| `home_team` | TEXT | Home team name | NULL allowed |
| `away_team` | TEXT | Away team name | NULL allowed |
| `start_time` | TEXT | Game start time in ISO 8601 format | NULL allowed |

#### Indexes

- **Primary Key:** `id` (automatic)
- **Unique Constraint:** `(sport, game_id)` prevents duplicates

### Table: odds

Stores normalized betting odds data for all markets.

```sql
CREATE TABLE odds (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    game_id INTEGER NOT NULL,
    provider TEXT NOT NULL,
    market TEXT NOT NULL,
    odds REAL NOT NULL,
    FOREIGN KEY(game_id) REFERENCES games(id)
);
```

#### Fields

| Field | Type | Description | Constraints |
|-------|------|-------------|-------------|
| `id` | INTEGER PRIMARY KEY | Auto-incrementing primary key | AUTOINCREMENT |
| `game_id` | INTEGER | Foreign key to games table | NOT NULL, FOREIGN KEY |
| `provider` | TEXT | Provider name (e.g., "DraftKings") | NOT NULL |
| `market` | TEXT | Market type (e.g., "Moneyline", "Spread") | NOT NULL |
| `odds` | REAL | Odds value | NOT NULL |

#### Foreign Keys

- `game_id` → `games(id)` - Ensures referential integrity

## Data Models

### BaseDataModel

```python
@dataclass
class BaseDataModel:
    """Base class for all data models."""
    id: int | None = None
```

Common base class providing consistent interface for all data models.

### Game Model

```python
@dataclass
class Game(BaseDataModel):
    """Represents a sporting event/game."""
    sport: str = ""
    game_id: str = ""
    home_team: str = ""
    away_team: str = ""
    start_time: datetime | None = None
```

### Odds Model

```python
@dataclass
class Odds(BaseDataModel):
    """Represents odds for a specific market."""
    game_id: int = 0
    provider: str = ""
    market: str = ""
    odds: float = 0.0
```

## Database Operations

### Connection Management

Always use context managers for database connections:

```python
from src.core.database import get_connection

# ✅ Correct usage
with get_connection() as conn:
    cur = conn.cursor()
    cur.execute("SELECT * FROM games")
    results = cur.fetchall()
    # Connection automatically closed

# ❌ Incorrect usage
conn = get_connection()
cur = conn.cursor()
# Must remember to call conn.close()
```

### Initialization

Initialize the database and create tables:

```python
from src.core.database import init_db

# Creates tables if they don't exist
init_db()
```

### Query Examples

#### Retrieve All Games

```python
from src.core.database import get_connection

with get_connection() as conn:
    cur = conn.cursor()
    cur.execute("""
        SELECT sport, game_id, home_team, away_team, start_time 
        FROM games 
        ORDER BY start_time DESC
    """)
    games = [dict(row) for row in cur.fetchall()]
```

#### Get Games by Sport

```python
def get_games_by_sport(sport: str):
    with get_connection() as conn:
        cur = conn.cursor()
        cur.execute("""
            SELECT * FROM games WHERE sport = ? ORDER BY start_time
        """, (sport,))
        return [dict(row) for row in cur.fetchall()]
```

#### Insert or Update Game

```python
def upsert_game(game_data):
    with get_connection() as conn:
        cur = conn.cursor()
        cur.execute("""
            INSERT OR REPLACE INTO games 
            (sport, game_id, home_team, away_team, start_time)
            VALUES (?, ?, ?, ?, ?)
        """, (
            game_data['sport'],
            game_data['game_id'], 
            game_data['home_team'],
            game_data['away_team'],
            game_data['start_time']
        ))
        conn.commit()
```

#### Insert Odds Data

```python
def insert_odds(odds_data):
    with get_connection() as conn:
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO odds (game_id, provider, market, odds)
            VALUES (?, ?, ?, ?)
        """, (
            odds_data['game_id'],
            odds_data['provider'],
            odds_data['market'],
            odds_data['odds']
        ))
        conn.commit()
```

#### Complex Query with JOIN

```python
def get_games_with_odds(sport=None):
    query = """
        SELECT 
            g.sport,
            g.game_id,
            g.home_team,
            g.away_team,
            g.start_time,
            o.provider,
            o.market,
            o.odds
        FROM games g
        LEFT JOIN odds o ON g.id = o.game_id
    """
    params = []
    
    if sport:
        query += " WHERE g.sport = ?"
        params.append(sport)
    
    query += " ORDER BY g.start_time, o.provider, o.market"
    
    with get_connection() as conn:
        cur = conn.cursor()
        cur.execute(query, params)
        return [dict(row) for row in cur.fetchall()]
```

## Performance Optimization

### Indexes

Consider adding indexes for common query patterns:

```sql
-- Index for sport-based queries
CREATE INDEX idx_games_sport ON games(sport);

-- Index for time-based queries  
CREATE INDEX idx_games_start_time ON games(start_time);

-- Index for provider queries
CREATE INDEX idx_odds_provider ON odds(provider);

-- Index for market type queries
CREATE INDEX idx_odds_market ON odds(market);
```

### Query Optimization

1. **Use specific columns** instead of `SELECT *`
2. **Add WHERE clauses** to limit result sets
3. **Use LIMIT** for large result sets
4. **Index frequently queried columns**

```python
# Optimized query
cur.execute("""
    SELECT sport, home_team, away_team 
    FROM games 
    WHERE sport = ? AND start_time > ?
    LIMIT 100
""", (sport, cutoff_time))
```

## Data Migration

### Adding New Columns

```python
def add_game_status_column():
    with get_connection() as conn:
        cur = conn.cursor()
        try:
            cur.execute("ALTER TABLE games ADD COLUMN status TEXT")
            conn.commit()
            print("Added status column to games table")
        except sqlite3.OperationalError as e:
            if "duplicate column name" in str(e):
                print("Status column already exists")
            else:
                raise
```

### Creating New Tables

```python
def create_markets_table():
    with get_connection() as conn:
        cur = conn.cursor()
        cur.execute("""
            CREATE TABLE IF NOT EXISTS markets (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE NOT NULL,
                description TEXT
            )
        """)
        conn.commit()
```

## Backup and Recovery

### Manual Backup

```bash
# Create backup
sqlite3 betting_markets.db ".backup backup_$(date +%Y%m%d_%H%M%S).db"

# Restore from backup
sqlite3 betting_markets.db ".restore backup_20241206_120000.db"
```

### Automated Backup Script

```python
#!/usr/bin/env python3
import sqlite3
import shutil
from datetime import datetime
from pathlib import Path

def backup_database(source_path: Path, backup_dir: Path):
    backup_dir.mkdir(exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = backup_dir / f"backup_{timestamp}.db"
    
    with sqlite3.connect(source_path) as source:
        with sqlite3.connect(backup_path) as backup:
            source.backup(backup)
    
    print(f"Database backed up to {backup_path}")
    
    # Clean up old backups (keep last 7 days)
    cleanup_old_backups(backup_dir, days=7)

def cleanup_old_backups(backup_dir: Path, days: int = 7):
    cutoff = datetime.now().timestamp() - (days * 24 * 3600)
    for backup_file in backup_dir.glob("backup_*.db"):
        if backup_file.stat().st_mtime < cutoff:
            backup_file.unlink()
            print(f"Removed old backup: {backup_file}")

if __name__ == "__main__":
    source = Path("betting_markets.db")
    backup_dir = Path("backups")
    backup_database(source, backup_dir)
```

## Monitoring and Maintenance

### Database Statistics

```python
def get_database_stats():
    with get_connection() as conn:
        cur = conn.cursor()
        
        # Table row counts
        cur.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = cur.fetchall()
        
        stats = {}
        for (table_name,) in tables:
            cur.execute(f"SELECT COUNT(*) FROM {table_name}")
            count = cur.fetchone()[0]
            stats[table_name] = count
        
        return stats

# Example usage
stats = get_database_stats()
print(f"Games: {stats.get('games', 0)}")
print(f"Odds: {stats.get('odds', 0)}")
```

### Database Integrity Check

```python
def check_database_integrity():
    with get_connection() as conn:
        cur = conn.cursor()
        cur.execute("PRAGMA integrity_check")
        result = cur.fetchone()
        return result[0] == "ok"
```

## Development vs Production

### Development

- **File-based SQLite**: Simple, no setup required
- **Local development**: Default configuration
- **Testing**: In-memory databases for unit tests

### Production Considerations

- **Connection pooling**: Consider PostgreSQL or MySQL for high load
- **Backup strategy**: Automated daily backups
- **Monitoring**: Track query performance and database size
- **Migration strategy**: Versioned schema changes

## Troubleshooting

### Common Issues

#### Database Locked

```
sqlite3.OperationalError: database is locked
```

**Solutions:**
- Ensure all connections use context managers
- Check for hanging connections
- Restart application if necessary

#### Disk Space

Monitor database size and implement cleanup:
```sql
-- Check table sizes
SELECT 
    name,
    ROUND(pgsize/1024.0, 2) as size_kb
FROM dbstat 
WHERE name IN ('games', 'odds');
```

#### Slow Queries

- Add appropriate indexes
- Optimize query structure
- Consider pagination for large result sets

### Debug Queries

```python
import sqlite3

# Enable query planning debug
with get_connection() as conn:
    cur = conn.cursor()
    cur.execute("EXPLAIN QUERY PLAN SELECT * FROM games WHERE sport = 'NFL'")
    plan = cur.fetchall()
    for row in plan:
        print(row)
```

## Best Practices

1. **Always use context managers** for database connections
2. **Never use `print()`** - use proper logging
3. **Handle exceptions** gracefully in database operations
4. **Use parameterized queries** to prevent SQL injection
5. **Keep transactions short** to avoid locking issues
6. **Monitor database size** and implement cleanup policies
7. **Regular backups** in production environments
8. **Test queries** with small datasets before production use

## Example: Complete Data Flow

```python
from src.core.database import get_connection, init_db
from src.core.schemas import StandardizedGame

def store_game_data(games_data):
    """Store a list of StandardizedGame objects."""
    init_db()  # Ensure tables exist
    
    with get_connection() as conn:
        cur = conn.cursor()
        
        for game in games_data:
            # Insert game
            cur.execute("""
                INSERT OR IGNORE INTO games 
                (sport, game_id, home_team, away_team, start_time)
                VALUES (?, ?, ?, ?, ?)
            """, (
                game.sport,
                game.game_id,
                game.home_team,
                game.away.start_time.iso_team,
                gameformat() if game.start_time else None
            ))
            
            # Get game ID for odds
            game_id = cur.lastrowid
            if not game_id:
                # Game already exists, get its ID
                cur.execute("SELECT id FROM games WHERE sport = ? AND game_id = ?",
                          (game.sport, game.game_id))
                game_id = cur.fetchone()[0]
            
            # Insert odds for each market
            for market_name, selections in game.markets.items():
                for selection in selections:
                    cur.execute("""
                        INSERT INTO odds (game_id, provider, market, odds)
                        VALUES (?, ?, ?, ?)
                    """, (game_id, "DraftKings", market_name, selection.get('odds')))
        
        conn.commit()

# Usage
games = [StandardizedGame(...), ...]  # Your game data
store_game_data(games)