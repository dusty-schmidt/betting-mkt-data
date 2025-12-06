# src/providers/draftkings/client.py
"""HTTP client for DraftKings sportsbook API."""

import requests
from ...core.logger import get_logger

log = get_logger(__name__)

class DraftKingsClient:
    """Client for fetching odds data from DraftKings API."""

    # Map sport IDs to DraftKings league IDs
    LEAGUE_MAPPING = {
        "100": "1",      # NFL
        "200": "42648",  # NBA
        "300": "3",      # MLB
    }

    HEADERS = {
        "User-Agent": "Mozilla/5.0 (compatible; BettingAggregator/1.0)",
        "Accept": "*/*"
    }

    def get_odds(self, sport_id: str):
        """Fetch odds data for a specific sport from DraftKings API."""
        try:
            league_id = self.LEAGUE_MAPPING.get(sport_id)
            if not league_id:
                log.warning(f"No league mapping found for sport_id: {sport_id}")
                return {}

            url = f"https://sportsbook-nash.draftkings.com/api/sportscontent/dkusoh/v1/leagues/{league_id}"
            log.info(f"Fetching DraftKings data from: {url}")

            response = requests.get(url, headers=self.HEADERS, timeout=10)
            response.raise_for_status()

            data = response.json()
            log.info(f"Successfully fetched {len(data.get('events', []))} events from DraftKings")
            return data

        except requests.exceptions.RequestException as e:
            log.error(f"DraftKings API request failed: {e}")
            return {}
        except Exception as e:
            log.error(f"Unexpected error fetching DraftKings data: {e}")
            return {}
