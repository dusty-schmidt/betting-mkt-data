# Placeholder for core models (ORM-like structures)

# In a real project you might use SQLAlchemy or Pydantic models.
# For this simple SQLite setup we will just define dataclasses that match the tables.

from dataclasses import dataclass
from datetime import datetime

@dataclass
class Game:
    id: int | None = None
    sport: str = ""
    game_id: str = ""
    home_team: str = ""
    away_team: str = ""
    start_time: datetime | None = None

@dataclass
class Odds:
    id: int | None = None
    game_id: int = 0
    provider: str = ""
    market: str = ""
    odds: float = 0.0
