# src/providers/draftkings/parser.py
"""Parser for DraftKings raw odds data.

Converts the raw JSON response into a list of StandardizedGame objects.
"""

import string
from datetime import datetime
from typing import List, Dict, Optional, Any
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

def convert_to_datetime(utc_str: str) -> Optional[datetime]:
    """Convert ISO UTC string to datetime object."""
    try:
        return datetime.fromisoformat(utc_str.replace("Z", "+00:00"))
    except Exception as e:
        log.warning(f"Failed to parse datetime {utc_str}: {e}")
        return None

class DraftKingsParser:
    """Parser for DraftKings API responses with comprehensive market data extraction."""
    
    def convert_to_datetime(self, utc_str: str) -> Optional[datetime]:
        """Convert ISO UTC string to datetime object.
        
        Args:
            utc_str: ISO format UTC timestamp string
            
        Returns:
            datetime object or None if parsing fails
        """
        try:
            return datetime.fromisoformat(utc_str.replace("Z", "+00:00"))
        except Exception as e:
            log.warning(f"Failed to parse datetime {utc_str}: {e}")
            return None
    
    def parse_games(self, raw_data: Dict[str, Any], sport_name: str) -> List[StandardizedGame]:
        """Parse DraftKings API response into StandardizedGame objects with market data.
        
        Handles the Events → Markets → Selections hierarchy from the dynamic API.
        
        Args:
            raw_data: Raw JSON response from DraftKings API
            sport_name: Sport name (e.g., "NBA", "NFL")
            
        Returns:
            List of StandardizedGame objects with market data populated
        """
        if not raw_data or not isinstance(raw_data, dict):
            log.warning("Invalid or empty raw data received")
            return []
        
        events = raw_data.get("events", [])
        markets = raw_data.get("markets", [])
        selections = raw_data.get("selections", [])
        
        if not events:
            log.info("No events found in DraftKings data")
            return []
        
        # Index selections by marketId for efficient lookup
        selections_by_market = {}
        for sel in selections:
            market_id = sel.get('marketId')
            if market_id not in selections_by_market:
                selections_by_market[market_id] = []
            selections_by_market[market_id].append(sel)
        
        # Index markets by eventId for efficient lookup
        markets_by_event = {}
        for mkt in markets:
            event_id = mkt.get('eventId')
            if event_id not in markets_by_event:
                markets_by_event[event_id] = []
            markets_by_event[event_id].append(mkt)
        
        games = []
        
        for event in events:
            try:
                event_id = str(event.get("id", ""))
                if not event_id:
                    continue
                
                # Parse start time
                start_time_str = event.get("startEventDate")
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
                
                status = event.get("status", "UNKNOWN")
                
                # Create standardized game
                game = StandardizedGame(
                    sport=sport_name,
                    game_id=f"dk_{event_id}",  # Prefix with provider to avoid conflicts
                    home_team=home_team,
                    away_team=away_team,
                    start_time=start_time,
                    status=status
                )
                
                # Process markets for this event
                event_markets = markets_by_event.get(event_id, [])
                for mkt in event_markets:
                    market_name = mkt.get('name', 'Unknown')
                    market_id = mkt.get('id')
                    
                    # Filter for main markets only: Moneyline, Spread, Total
                    # UPDATE: Removed filter to allow prop markets (e.g. Player Props) to be extracted
                    # if market_name not in ['Moneyline', 'Spread', 'Total']:
                    #    continue
                    
                    # Get selections for this market
                    mkt_selections = selections_by_market.get(market_id, [])
                    parsed_selections = []
                    
                    for sel in mkt_selections:
                        label = sel.get('label', 'Unknown')
                        odds = sel.get('displayOdds', {}).get('american', 'N/A')
                        if isinstance(odds, str):
                            odds = odds.replace('\u2212', '-')
                        
                        # Add points/line if available (for Spread/Total markets)
                        points = sel.get('points')
                        if points is not None:
                            label = f"{label} ({points})"
                        
                        parsed_selections.append({
                            'label': label,
                            'odds': odds
                        })
                    
                    # Add market data to game using the standardized method
                    game.add_market(market_name, parsed_selections)
                
                games.append(game)
                
            except Exception as e:
                log.error(f"Error parsing event {event.get('id', 'unknown')}: {e}", exc_info=True)
                continue
        
        log.info(f"Successfully parsed {len(games)} games from DraftKings")
        return games


def parse_odds(raw_data: Dict[str, Any], sport_id: str = None, sport_name: str = None) -> List[StandardizedGame]:
    """Parse DraftKings API response into StandardizedGame objects.
    
    This function provides backward compatibility with existing code while leveraging
    the new DraftKingsParser for comprehensive parsing with market data.
    
    Args:
        raw_data: Raw JSON response from DraftKings API
        sport_id: Sport ID (e.g., "200" for NBA) - not used in new implementation
        sport_name: Sport name (e.g., "NBA", "NFL")
        
    Returns:
        List of StandardizedGame objects with market data populated
    """
    if not raw_data or not isinstance(raw_data, dict):
        log.warning("Invalid or empty raw data received")
        return []
    
    # Use the new DraftKingsParser for comprehensive parsing
    parser = DraftKingsParser()
    
    # Default to a generic sport name if none provided
    sport = sport_name or "Unknown"
    
    return parser.parse_games(raw_data, sport)


