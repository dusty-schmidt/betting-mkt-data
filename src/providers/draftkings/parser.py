# src/providers/draftkings/parser.py
"""Parser for DraftKings raw odds data.

Converts the raw JSON response into a list of StandardizedGame objects.
"""

import string
from datetime import datetime
from typing import List, Dict
from ...core.schemas import StandardizedGame
from ...core.logger import get_logger

log = get_logger(__name__)

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

def normalize_team(name: str) -> str:
    """Normalize team name for abbreviation lookup."""
    return name.lower().translate(str.maketrans('', '', string.punctuation))

def convert_to_datetime(utc_str: str) -> datetime:
    """Convert ISO UTC string to datetime object."""
    try:
        return datetime.fromisoformat(utc_str.replace("Z", "+00:00"))
    except Exception as e:
        log.warning(f"Failed to parse datetime {utc_str}: {e}")
        return None

def parse_odds(raw_data: Dict, sport_id: str = None, sport_name: str = None) -> List[StandardizedGame]:
    """Parse DraftKings API response into StandardizedGame objects.

    Args:
        raw_data: Raw JSON response from DraftKings API
        sport_id: Sport ID (e.g., "200" for NBA)
        sport_name: Sport name (e.g., "NBA")

    Returns:
        List of StandardizedGame objects
    """
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
            start_time = convert_to_datetime(start_time_str) if start_time_str else None

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
                sport=sport_name or "Unknown",
                game_id=f"dk_{event_id}",  # Prefix with provider to avoid conflicts
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
