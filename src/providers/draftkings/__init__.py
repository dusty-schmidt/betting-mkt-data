# src/providers/draftkings/__init__.py
"""DraftKings provider implementation with dynamic API integration.

This provider integrates the new DraftKingsDynamicClient and DraftKingsParser
to leverage dynamic API discovery and comprehensive market data extraction.
"""

from .client import DraftKingsClient, DraftKingsDynamicClient
from .parser import DraftKingsParser, parse_odds
from ..base import BaseProvider
from ...core.schemas import StandardizedGame
from ...core.logger import get_logger

log = get_logger(__name__)

class DraftKingsProvider(BaseProvider):
    """DraftKings provider with dynamic API discovery and comprehensive market parsing.
    
    Integrates both legacy and dynamic client support for maximum compatibility
    and comprehensive market data extraction including Moneyline, Spread, and Total markets.
    """
    
    def __init__(self):
        """Initialize the DraftKings provider with both legacy and dynamic clients."""
        # Legacy client for backward compatibility
        self.client = DraftKingsClient()
        
        # New dynamic client for comprehensive API discovery
        self.dynamic_client = DraftKingsDynamicClient()
        
        # Enhanced parser for comprehensive market data extraction
        self.parser = DraftKingsParser()
        
        log.info("DraftKingsProvider initialized with dynamic client support")

    def get_sports_mapping(self) -> dict:
        """Return mapping from sport IDs to sport names for dynamic client.
        
        Maintains backward compatibility with existing scheduler integration while
        also providing sport names needed for dynamic API discovery.
        
        Returns:
            Dictionary mapping sport IDs to sport names
        """
        return {
            "100": "NFL",      # NFL
            "200": "NBA",      # NBA  
            "300": "MLB",      # MLB
        }

    def fetch_odds(self, sport_id: str) -> list[StandardizedGame]:
        """Fetch odds for the given sport using dynamic API discovery.
        
        Implements the dynamic workflow:
        1. Map sport_id to sport_name
        2. Use dynamic client to discover API endpoints and fetch raw data
        3. Use enhanced parser to extract comprehensive market data
        4. Return StandardizedGame objects with populated markets
        
        Args:
            sport_id: Sport ID from scheduler (e.g., "200" for NBA)
            
        Returns:
            List of StandardizedGame objects with market data populated
        """
        try:
            # Map sport_id to sport_name for dynamic client
            sport_name = self.get_sports_mapping().get(sport_id)
            if not sport_name:
                log.warning(f"No sport mapping found for sport_id: {sport_id}")
                return []
            
            log.info(f"Fetching {sport_name} odds using dynamic client for sport_id: {sport_id}")
            
            # Use dynamic client to fetch comprehensive market data
            raw_data = self.dynamic_client.get_games_for_sport(sport_name)
            
            if not raw_data:
                log.warning(f"No data returned from dynamic client for {sport_name}")
                return []
            
            log.info(f"Successfully fetched {len(raw_data.get('events', []))} events for {sport_name}")
            
            # Use enhanced parser to extract comprehensive market data
            games = self.parser.parse_games(raw_data, sport_name)
            
            log.info(f"Successfully parsed {len(games)} games with market data for {sport_name}")
            return games
            
        except Exception as e:
            log.error(f"Error fetching odds for sport_id {sport_id}: {e}", exc_info=True)
            return []

    def get_legacy_sports_mapping(self) -> dict:
        """Get legacy sport mapping for backward compatibility.
        
        Returns:
            Dictionary mapping sport IDs to legacy league IDs
        """
        return {
            "100": "1",        # NFL
            "200": "42648",    # NBA  
            "300": "3",        # MLB
        }

    def fetch_odds_legacy(self, sport_id: str) -> list[StandardizedGame]:
        """Legacy fetch method using original client and parser.
        
        This method is retained for compatibility and fallback scenarios.
        
        Args:
            sport_id: Sport ID from scheduler
            
        Returns:
            List of StandardizedGame objects
        """
        try:
            log.debug(f"Using legacy fetch method for sport_id: {sport_id}")
            
            # Use legacy client
            raw = self.client.get_odds(sport_id)
            
            if not raw:
                log.warning(f"No data returned from legacy client for sport_id: {sport_id}")
                return []
            
            # Get sport name for legacy parsing
            sport_name = self.get_sports_mapping().get(sport_id, "Unknown")
            
            # Use legacy parser for backward compatibility
            return parse_odds(raw, sport_id, sport_name)
            
        except Exception as e:
            log.error(f"Error in legacy fetch for sport_id {sport_id}: {e}", exc_info=True)
            return []