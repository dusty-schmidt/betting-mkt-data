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
        # Example mapping; real values would come from DraftKings docs
        return {"100": "NFL", "200": "NBA"}

    def fetch_odds(self, sport_id: str) -> list[StandardizedGame]:
        raw = self.client.get_odds(sport_id)
        return parse_odds(raw)
