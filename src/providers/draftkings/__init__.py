# src/providers/draftkings/__init__.py
"""DraftKings provider implementation placeholder.

In a real implementation this would handle authentication, request building,
and parsing of DraftKings API responses.
"""

from .client import DraftKingsClient
from .parser import parse_odds
from ..base import BaseProvider
from ...core.schemas import StandardizedGame

class DraftKingsProvider(BaseProvider):
    def __init__(self):
        self.client = DraftKingsClient()

    def get_sports_mapping(self) -> dict:
        # Map sport names to their internal DraftKings league IDs
        return {"NFL": "1", "NBA": "42648", "MLB": "3"}

    def fetch_odds(self, sport_id: str) -> list[StandardizedGame]:
        raw = self.client.get_odds(sport_id)
        sport_name = self.get_sports_mapping().get(sport_id, "Unknown")
        return parse_odds(raw, sport_id, sport_name)
