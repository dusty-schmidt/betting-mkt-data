import requests
import logging
import urllib.parse
from datetime import datetime
from typing import List, Dict, Optional

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Constants
BASE_URL = "https://sportsbook-nash.draftkings.com"
MANIFEST_URL = f"{BASE_URL}/sites/US-OH-SB/api/sportslayout/v1/manifest?format=json"
TEMPLATE_URL_BASE = f"{BASE_URL}/sites/US-OH-SB/api/sportsstructure/v1/templates/"
MARKET_URL_BASE = f"{BASE_URL}/sites/US-OH-SB/api/sportscontent/controldata/league/leagueSubcategory/v1/markets"

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:145.0) Gecko/20100101 Firefox/145.0',
    'Accept': '*/*',
    'Accept-Language': 'en-US,en;q=0.5',
    'Accept-Encoding': 'gzip, deflate, br, zstd',
    'Referer': 'https://sportsbook.draftkings.com/',
    'X-Client-Name': 'web',
    'X-Client-Version': '1.6.0',
    'X-Client-Feature': 'cms',
    'X-Client-Page': 'home',
    'Origin': 'https://sportsbook.draftkings.com',
    'Connection': 'keep-alive',
    'Sec-Fetch-Dest': 'empty',
    'Sec-Fetch-Mode': 'cors',
    'Sec-Fetch-Site': 'same-site',
    'Priority': 'u=4',
    'TE': 'trailers'
}

class StandardizedGame:
    def __init__(self, sport: str, game_id: str, home_team: str, away_team: str, start_time=None, status=None):
        self.sport = sport
        self.game_id = game_id
        self.home_team = home_team
        self.away_team = away_team
        self.start_time = start_time
        self.status = status

    def __repr__(self):
        return f"Game({self.sport}: {self.away_team} @ {self.home_team}, Start: {self.start_time}, Status: {self.status})"

class DraftKingsDynamicClient:
    """Client to fetch DraftKings data using dynamic template discovery."""

    def fetch_json(self, url, description):
        """Helper to fetch JSON data with error handling."""
        try:
            logger.info(f"Fetching {description} from: {url}")
            response = requests.get(url, headers=HEADERS)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to fetch {description}: {e}")
            return None

    def find_nfl_info(self, manifest_data):
        """Finds the templateId and leagueId for the NFL league page."""
        if not manifest_data:
            return None, None
        
        for route_group in manifest_data.get('routes', []):
            if route_group.get('key') == 'league':
                for override in route_group.get('overrides', []):
                    if override.get('seoRoute') == '/leagues/football/nfl':
                        template_id = override.get('templateId')
                        
                        # Extract league ID from route: /sport/3/league/88808
                        route = override.get('route', '')
                        league_id = None
                        if '/league/' in route:
                            try:
                                league_id = route.split('/league/')[1]
                            except IndexError:
                                pass
                        
                        logger.info(f"Found NFL Template ID: {template_id}, League ID: {league_id}")
                        return template_id, league_id
        
        logger.error("Could not find NFL route in manifest.")
        return None, None

    def extract_all_market_queries(self, template_data):
        """Extracts ALL valid market queries from the template."""
        if not template_data:
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
        
        return queries

    def construct_market_url(self, queries, league_id):
        """Constructs the final API URL."""
        if not queries:
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
        return f"{MARKET_URL_BASE}?{query_string}"

    def get_nfl_games(self):
        """Orchestrates the fetching of NFL games."""
        
        # Step 1: Fetch Manifest
        manifest_data = self.fetch_json(MANIFEST_URL, "Manifest")
        if not manifest_data:
            return None

        # Step 2: Find NFL Template ID and League ID
        nfl_template_id, numeric_league_id = self.find_nfl_info(manifest_data)
        if not nfl_template_id or not numeric_league_id:
            return None

        # Step 3: Fetch Template
        template_url = f"{TEMPLATE_URL_BASE}{nfl_template_id}?format=json"
        template_data = self.fetch_json(template_url, "NFL Template")
        if not template_data:
            return None

        # Step 5: Extract ALL Market Queries
        queries = self.extract_all_market_queries(template_data)
        logger.info(f"Found {len(queries)} potential market queries")

        # Step 6: Iterate and find the one with Game Lines
        # We'll try to fetch data for each query until we find one that returns events with Game Lines
        
        for query in queries:
            # Skip queries that look like they are for specific events (often have 'eventId' in query)
            if 'eventId' in query['eventsQuery']:
                continue

            # Skip queries that don't use subcategoryId (might be too broad or specific)
            if '@subcategoryId' not in query['eventsQuery']:
                continue

            # We need to guess the subcategoryId.
            # Based on previous analysis:
            # NBA Game Lines: 4511
            # NFL Game Lines: 4518 (from template-response.json)
            # Let's try substituting 4518 for NFL.
            
            # Create a modified query object with the subcategoryId substituted
            # We do this manually here because construct_market_url expects the query string to have the placeholder
            # But we need to inject the specific ID we want to test.
            
            # Actually, construct_market_url just does string replacement.
            # So we can pass the query as is, but we need to handle the @subcategoryId replacement.
            
            # Let's try to inject '4518' (NFL Game Lines) into the query strings
            modified_query = {
                'name': query['name'],
                'eventsQuery': query['eventsQuery'].replace('@subcategoryId', '4518'),
                'marketsQuery': query['marketsQuery'].replace('@subcategoryId', '4518')
            }
            
            market_url = self.construct_market_url(modified_query, league_id=numeric_league_id)
            market_data = self.fetch_json(market_url, f"Market Data ({query['name']})")
            
            if market_data and market_data.get('events'):
                logger.info(f"Found data with {len(market_data['events'])} events using query {query['name']}")
                return market_data
                
        logger.error("Could not find any data for Game Lines")
        return None

class DraftKingsParser:
    """Parses DraftKings API response."""

    def convert_to_datetime(self, utc_str: str) -> Optional[datetime]:
        """Convert ISO UTC string to datetime object."""
        try:
            return datetime.fromisoformat(utc_str.replace("Z", "+00:00"))
        except Exception as e:
            logger.warning(f"Failed to parse datetime {utc_str}: {e}")
            return None

    def parse_games(self, raw_data) -> List[StandardizedGame]:
        """Parse DraftKings API response into StandardizedGame objects."""
        if not raw_data or not isinstance(raw_data, dict):
            logger.warning("Invalid or empty raw data received")
            return []

        events = raw_data.get("events", [])
        if not events:
            logger.info("No events found in DraftKings data")
            return []

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
                    logger.warning(f"Skipping event {event_id}: missing team info")
                    continue
                
                status = event.get("status", "UNKNOWN")

                # Create standardized game
                game = StandardizedGame(
                    sport="NFL",
                    game_id=f"dk_{event_id}",
                    home_team=home_team,
                    away_team=away_team,
                    start_time=start_time,
                    status=status
                )

                games.append(game)

            except Exception as e:
                logger.error(f"Error parsing event {event.get('id', 'unknown')}: {e}")
                continue

        logger.info(f"Successfully parsed {len(games)} games from DraftKings")
        return games

def main():
    logger.info("Starting NFL Games Fetch Test")
    
    client = DraftKingsDynamicClient()
    parser = DraftKingsParser()
    
    # Fetch raw data
    raw_data = client.get_nfl_games()
    
    if raw_data:
        # Parse games
        games = parser.parse_games(raw_data)
        
        print(f"\nFound {len(games)} Upcoming NFL Games:")
        print("-" * 60)
        for game in games:
            print(f"{game.away_team} @ {game.home_team}")
            print(f"  Start: {game.start_time}")
            print(f"  Status: {game.status}")
            print("-" * 60)
    else:
        print("Failed to fetch NFL games data.")

if __name__ == "__main__":
    main()