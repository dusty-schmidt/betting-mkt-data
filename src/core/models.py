# Placeholder for core models (ORM-like structures)

# In a real project you might use SQLAlchemy or Pydantic models.
# For this simple SQLite setup we will just define dataclasses that match the tables.

from dataclasses import dataclass
from datetime import datetime

@dataclass
class BaseDataModel:
    """Base class for all data models.
    
    This establishes a common pattern for data models in the system.
    Future extensions can add common methods or properties here.
    """
    id: int | None = None

@dataclass
class Game(BaseDataModel):
    """Represents a sporting event/game."""
    sport: str = ""
    game_id: str = ""
    home_team: str = ""
    away_team: str = ""
    start_time: datetime | None = None

@dataclass
class Odds(BaseDataModel):
    """Represents odds for a specific market."""
    game_id: int = 0
    provider: str = ""
    market: str = ""
    odds: float = 0.0
