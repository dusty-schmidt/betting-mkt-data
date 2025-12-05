# Placeholder for core schemas using Pydantic

from pydantic import BaseModel
from datetime import datetime

class StandardizedGame(BaseModel):
    sport: str
    game_id: str
    home_team: str | None = None
    away_team: str | None = None
    start_time: datetime | None = None
    # Additional fields as needed
