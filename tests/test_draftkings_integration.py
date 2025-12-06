# tests/test_draftkings_integration.py
"""Test-Driven Development for DraftKings provider integration.

This file contains experimental code to test DraftKings API integration
before applying changes to the production provider code.
"""

import requests
import string
from datetime import datetime
from typing import List, Dict

# Simple logging for testing
import logging
logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)

# Simplified StandardizedGame for testing
class StandardizedGame:
    def __init__(self, sport: str, game_id: str, home_team: str, away_team: str, start_time=None):
        self.sport = sport
        self.game_id = game_id
        self.home_team = home_team
        self.away_team = away_team
        self.start_time = start_time

    def __repr__(self):
        return f"Game({self.sport}: {self.away_team} @ {self.home_team})"

class TestDraftKingsClient:
    """Test implementation of DraftKings client."""

    # Map sport names to DraftKings league IDs
    LEAGUE_MAPPING = {
        "NFL": "1",
        "NBA": "42648",
        "MLB": "3",
    }

    HEADERS = {
        "User-Agent": "Mozilla/5.0 (compatible; BettingAggregator/1.0)",
        "Accept": "*/*"
    }

    def get_odds(self, sport_name: str):
        """Fetch odds data for a specific sport from DraftKings API."""
        try:
            league_id = self.LEAGUE_MAPPING.get(sport_name)
            if not league_id:
                log.warning(f"No league mapping found for sport: {sport_name}")
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

class TestDraftKingsParser:
    """Test implementation of DraftKings parser."""

    # Team name abbreviations (from example)
    TEAM_ABBR = {
        "atlanta hawks": "ATL", "boston celtics": "BOS", "brooklyn nets": "BKN",
        "charlotte hornets": "CHO", "chicago bulls": "CHI", "cleveland cavaliers": "CLE",
        "dallas mavericks": "DAL", "denver nuggets": "DEN", "detroit pistons": "DET",
        "golden state warriors": "GSW", "houston rockets": "HOU", "indiana pacers": "IND",
        "los angeles clippers": "LAC", "los angeles lakers": "LAL", "memphis grizzlies": "MEM",
        "miami heat": "MIA", "milwaukee bucks": "MIL", "minnesota timberwolves": "MIN",
        "new orleans pelicans": "NOP", "new york knicks": "NYK", "oklahoma city thunder": "OKC",
        "orlando magic": "ORL", "philadelphia 76ers": "PHI", "phoenix suns": "PHX",
        "portland trail blazers": "POR", "sacramento kings": "SAC", "san antonio spurs": "SAS",
        "toronto raptors": "TOR", "utah jazz": "UTA", "washington wizards": "WAS"
    }

    def normalize_team(self, name: str) -> str:
        """Normalize team name for abbreviation lookup."""
        import string
        return name.lower().translate(str.maketrans('', '', string.punctuation))

    def convert_to_datetime(self, utc_str: str) -> datetime:
        """Convert ISO UTC string to datetime object."""
        try:
            return datetime.fromisoformat(utc_str.replace("Z", "+00:00"))
        except Exception as e:
            log.warning(f"Failed to parse datetime {utc_str}: {e}")
            return None

    def parse_odds(self, raw_data, sport_name: str) -> list[StandardizedGame]:
        """Parse DraftKings API response into StandardizedGame objects."""
        if not raw_data or not isinstance(raw_data, dict):
            log.warning("Invalid or empty raw data received")
            return []

        events = raw_data.get("events", [])
        if not events:
            log.info("No events found in DraftKings data")
            return []

        games = []

        for event in events:
            try:
                event_id = str(event.get("id", ""))
                if not event_id:
                    continue

                game_name = event.get("name", "")
                start_time_str = event.get("startEventDate")

                # Parse start time
                start_time = self.convert_to_datetime(start_time_str) if start_time_str else None

                # Extract participants (teams)
                participants = event.get("participants", [])
                away_team = None
                home_team = None

                for participant in participants:
                    venue_role = participant.get("venueRole", "").lower()
                    team_name = participant.get("name", "")

                    if venue_role == "away":
                        away_team = team_name
                    elif venue_role == "home":
                        home_team = team_name

                # Skip if we don't have both teams
                if not away_team or not home_team:
                    log.warning(f"Skipping event {event_id}: missing team info")
                    continue

                # Create standardized game
                game = StandardizedGame(
                    sport=sport_name,
                    game_id=f"dk_{event_id}",
                    home_team=home_team,
                    away_team=away_team,
                    start_time=start_time
                )

                games.append(game)

            except Exception as e:
                log.error(f"Error parsing event {event.get('id', 'unknown')}: {e}")
                continue

        log.info(f"Successfully parsed {len(games)} games from DraftKings")
        return games

def test_draftkings_nba_fetch():
    """Test fetching NBA data from DraftKings."""
    client = TestDraftKingsClient()
    parser = TestDraftKingsParser()

    # Test NBA fetch
    raw_data = client.get_odds("NBA")
    if raw_data:
        games = parser.parse_odds(raw_data, "NBA")
        print(f"Fetched {len(games)} NBA games:")
        for game in games[:3]:  # Show first 3
            print(f"  {game.sport}: {game.away_team} @ {game.home_team} at {game.start_time}")
        return games
    else:
        print("Failed to fetch NBA data")
        return []

def test_end_to_end():
    """Test the full provider pipeline as it would run in production."""
    import sys
    import os
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

    from src.providers.draftkings import DraftKingsProvider

    # Create provider instance
    provider = DraftKingsProvider()

    # Test fetch_odds as the scheduler would call it
    print("Testing DraftKings provider fetch_odds('NBA')...")
    games = provider.fetch_odds("NBA")

    print(f"Provider returned {len(games)} games:")
    for i, game in enumerate(games[:5]):  # Show first 5
        print(f"  {i+1}. {game.game_id}: {game.away_team} @ {game.home_team}")

    return games

if __name__ == "__main__":
    print("=== Testing DraftKings API Integration ===")
    test_games = test_draftkings_nba_fetch()

    print("\n=== Testing End-to-End Provider Pipeline ===")
    provider_games = test_end_to_end()

    print(f"\nTest Results: {len(test_games)} test games, {len(provider_games)} provider games")
    if len(test_games) == len(provider_games):
        print("✅ Test and provider implementations match!")
    else:
        print("❌ Test and provider implementations differ!")