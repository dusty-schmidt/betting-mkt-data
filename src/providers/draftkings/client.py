# src/providers/draftkings/client.py
"""HTTP client for DraftKings sportsbook API."""

import requests
import urllib.parse
from ...core.logger import get_logger
from .mappings import (
    MANIFEST_URL,
    TEMPLATE_URL_BASE,
    MARKET_URL_BASE,
    HEADERS,
    SUBCATEGORY_IDS,
    LEAGUE_ROUTES
)

log = get_logger(__name__)

class DraftKingsClient:
    """Client for fetching odds data from DraftKings API."""

    # Map sport IDs to DraftKings league IDs
    LEAGUE_MAPPING = {
        "100": "1",      # NFL
        "200": "42648",  # NBA
        "300": "3",      # MLB
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

            response = requests.get(url, headers=HEADERS, timeout=10)
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


class DraftKingsDynamicClient:
    """Client to fetch DraftKings data using dynamic template discovery.
    
    This client implements a 3-step workflow:
    1. Fetch manifest to discover API structure
    2. Find template ID and league ID for specific sports
    3. Extract market queries and construct final API URLs
    """

    def fetch_json(self, url: str, description: str):
        """Helper to fetch JSON data with error handling.
        
        Args:
            url: The URL to fetch data from
            description: Description of what is being fetched for logging
            
        Returns:
            JSON data if successful, None if failed
        """
        try:
            log.info(f"Fetching {description} from: {url}")
            response = requests.get(url, headers=HEADERS, timeout=10)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            log.error(f"Failed to fetch {description}: {e}")
            return None

    def find_league_info(self, manifest_data: dict, sport_name: str):
        """Finds the templateId and leagueId for a specific sport league page.
        
        Args:
            manifest_data: The manifest JSON response
            sport_name: Name of the sport (e.g., "NFL", "NBA")
            
        Returns:
            Tuple of (template_id, league_id) or (None, None) if not found
        """
        if not manifest_data:
            log.error("No manifest data provided")
            return None, None
        
        target_route = LEAGUE_ROUTES.get(sport_name)
        if not target_route:
            log.error(f"No route mapping for sport: {sport_name}")
            return None, None

        for route_group in manifest_data.get('routes', []):
            if route_group.get('key') == 'league':
                for override in route_group.get('overrides', []):
                    if override.get('seoRoute') == target_route:
                        template_id = override.get('templateId')
                        
                        # Extract league ID from route: /sport/{sportId}/league/{leagueId}
                        route = override.get('route', '')
                        league_id = None
                        if '/league/' in route:
                            try:
                                league_id = route.split('/league/')[1]
                            except IndexError:
                                pass
                        
                        log.info(f"Found {sport_name} Template ID: {template_id}, League ID: {league_id}")
                        return template_id, league_id
        
        log.error(f"Could not find {sport_name} route in manifest.")
        return None, None

    def extract_all_market_queries(self, template_data: dict):
        """Extracts ALL valid market queries from the template.
        
        Args:
            template_data: The template JSON response
            
        Returns:
            List of query dictionaries with 'name', 'eventsQuery', and 'marketsQuery' keys
        """
        if not template_data:
            log.error("No template data provided")
            return []

        queries = []
        data_sets = template_data.get('data', {}).get('sets', [])
        
        for data_set in data_sets:
            name = data_set.get('name', '')
            params = data_set.get('parameters', {})
            provider = data_set.get('provider')
            
            if provider == 'Markets':
                markets_query = params.get('marketsQuery', '')
                events_query = params.get('eventsQuery', '')
                
                if markets_query and events_query:
                    queries.append({
                        'name': name,
                        'eventsQuery': events_query,
                        'marketsQuery': markets_query
                    })
                    log.debug(f"Found market query: {name}")
        
        log.info(f"Extracted {len(queries)} potential market queries")
        return queries

    def construct_market_url(self, queries: dict, league_id: str):
        """Constructs the final API URL with parameter substitution.
        
        Args:
            queries: Dictionary with 'eventsQuery' and 'marketsQuery' keys
            league_id: The numeric league ID to substitute
            
        Returns:
            Complete market data URL if successful, None if failed
        """
        if not queries:
            log.error("No queries provided for URL construction")
            return None
        
        # Perform substitution on the queries
        events_query = queries['eventsQuery'].replace('@leagueId', str(league_id))
        markets_query = queries['marketsQuery'].replace('@leagueId', str(league_id))
        
        # Some queries use @page.leagueId
        events_query = events_query.replace('@page.leagueId', str(league_id))
        markets_query = markets_query.replace('@page.leagueId', str(league_id))

        # The base URL parameters
        params = {
            'isBatchable': 'false',
            'templateVars': league_id, 
            'eventsQuery': events_query,
            'marketsQuery': markets_query,
            'include': 'Events',
            'entity': 'events'
        }
        
        # URL encode the parameters
        query_string = urllib.parse.urlencode(params)
        market_url = f"{MARKET_URL_BASE}?{query_string}"
        
        log.debug(f"Constructed market URL with {len(events_query)} events query chars")
        return market_url

    def get_games_for_sport(self, sport_name: str):
        """Orchestrates the fetching of games for a specific sport.
        
        Implements the 3-step workflow:
        1. Fetch Manifest
        2. Find Template ID and League ID  
        3. Extract Market Queries and Construct Final URL
        
        Args:
            sport_name: Name of the sport (e.g., "NFL", "NBA")
            
        Returns:
            Market data JSON response if successful, None if failed
        """
        log.info(f"Starting dynamic fetch for {sport_name}")
        
        # Step 1: Fetch Manifest
        manifest_data = self.fetch_json(MANIFEST_URL, "Manifest")
        if not manifest_data:
            log.error(f"Failed to fetch manifest for {sport_name}")
            return None

        # Step 2: Find Template ID and League ID
        template_id, numeric_league_id = self.find_league_info(manifest_data, sport_name)
        if not template_id or not numeric_league_id:
            log.error(f"Could not find league info for {sport_name}")
            return None

        # Step 3: Fetch Template
        template_url = f"{TEMPLATE_URL_BASE}{template_id}?format=json"
        template_data = self.fetch_json(template_url, f"{sport_name} Template")
        if not template_data:
            log.error(f"Failed to fetch template for {sport_name}")
            return None

        # Step 4: Extract ALL Market Queries
        queries = self.extract_all_market_queries(template_data)
        log.info(f"Found {len(queries)} potential market queries for {sport_name}")

        # Step 5: Iterate and find the one with Game Lines
        target_subcategory_id = SUBCATEGORY_IDS.get(sport_name)
        if not target_subcategory_id:
            log.warning(f"No known subcategory ID for {sport_name}, skipping substitution attempt")
            return None

        for query in queries:
            # Skip queries that look like they are for specific events
            if 'eventId' in query['eventsQuery']:
                log.debug(f"Skipping query {query['name']}: appears to be for specific events")
                continue

            # Skip queries that don't use subcategoryId
            if '@subcategoryId' not in query['eventsQuery']:
                log.debug(f"Skipping query {query['name']}: doesn't use subcategoryId")
                continue

            # Inject the target subcategory ID
            modified_query = {
                'name': query['name'],
                'eventsQuery': query['eventsQuery'].replace('@subcategoryId', target_subcategory_id),
                'marketsQuery': query['marketsQuery'].replace('@subcategoryId', target_subcategory_id)
            }
            
            log.debug(f"Attempting query: {query['name']} with subcategoryId {target_subcategory_id}")
            
            market_url = self.construct_market_url(modified_query, league_id=numeric_league_id)
            if not market_url:
                continue
                
            market_data = self.fetch_json(market_url, f"Market Data ({query['name']})")
            
            if market_data and market_data.get('events'):
                log.info(f"Found data with {len(market_data['events'])} events using query {query['name']}")
                return market_data
                
        log.error(f"Could not find any data for {sport_name} Game Lines")
        return None