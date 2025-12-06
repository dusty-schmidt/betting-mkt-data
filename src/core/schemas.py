# Placeholder for core schemas using Pydantic

from pydantic import BaseModel
from datetime import datetime
from typing import Dict, Any

class StandardizedGame(BaseModel):
    sport: str
    game_id: str
    home_team: str | None = None
    away_team: str | None = None
    start_time: datetime | None = None
    status: str | None = None
    markets: Dict[str, Any] = {}
    # Additional fields as needed

    def add_market(self, market_name: str, selections) -> None:
        """Add market data to the games markets dictionary.
        
        Args:
            market_name: Name of the market (e.g., 'Moneyline', 'Spread', 'Total')
            selections: List of market selections with odds data
        """
        self.markets[market_name] = selections
