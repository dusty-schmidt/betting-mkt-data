# src/providers/draftkings/client.py
"""Simple HTTP client placeholder for DraftKings.

In a real implementation this would handle authentication, session management,
and constructing the correct endpoint URLs.
"""

import requests

class DraftKingsClient:
    BASE_URL = "https://api.draftkings.com/odds"

    def get_odds(self, sport_id: str):
        # Placeholder: return empty list or mock data
        # In practice you would perform a GET request like:
        # response = requests.get(f"{self.BASE_URL}/{sport_id}")
        # return response.json()
        return []
