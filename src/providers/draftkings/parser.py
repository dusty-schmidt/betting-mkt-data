# src/providers/draftkings/parser.py
"""Parser for DraftKings raw odds data.

Converts the raw response (list/dict) into a list of ``StandardizedGame`` objects.
This is a stub – in a real implementation you would map the API fields.
"""

from typing import List
from ...core.schemas import StandardizedGame

def parse_odds(raw_data) -> List[StandardizedGame]:
    # Placeholder implementation – return empty list or mock objects
    # Example of creating a StandardizedGame (requires appropriate fields)
    # return [StandardizedGame(sport="NFL", game_id="123", home_team="TeamA", away_team="TeamB")]
    return []
