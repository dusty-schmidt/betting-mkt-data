import requests
import logging
import urllib.parse
from datetime import datetime
from typing import List, Dict, Optional, Tuple

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

# Known Subcategory IDs for Game Lines
# These might change, but they are good starting points for substitution
SUBCATEGORY_IDS = {
    "NFL": "4518",
    "NBA": "4511"
}

# League Route Mapping
LEAGUE_ROUTES = {
    "NFL": "/leagues/football/nfl",
    "NBA": "/leagues/basketball/nba"
}

class StandardizedGame:
    def __init__(self, sport: str, game_id: str, home_team: str, away_team: str, start_time=None, status=None):
        self.sport = sport
        self.game_id = game_id
        self.home_team = home_team
        self.away_team = away_team
        self.start_time = start_time
        self.status = status
        self.markets = {}  # Dictionary to store market data

    def add_market(self, market_name, selections):
        self.markets[market_name] = selections

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

    def find_league_info(self, manifest_data, sport_name):
        """Finds the templateId and leagueId for a specific sport league page."""
        if not manifest_data:
            return None, None
        
        target_route = LEAGUE_ROUTES.get(sport_name)
        if not target_route:
            logger.error(f"No route mapping for sport: {sport_name}")
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
                        
                        logger.info(f"Found {sport_name} Template ID: {template_id}, League ID: {league_id}")
                        return template_id, league_id
        
        logger.error(f"Could not find {sport_name} route in manifest.")
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

    def get_games_for_sport(self, sport_name):
        """Orchestrates the fetching of games for a specific sport."""
        logger.info(f"Starting fetch for {sport_name}")
        
        # Step 1: Fetch Manifest
        manifest_data = self.fetch_json(MANIFEST_URL, "Manifest")
        if not manifest_data:
            return None

        # Step 2: Find Template ID and League ID
        template_id, numeric_league_id = self.find_league_info(manifest_data, sport_name)
        if not template_id or not numeric_league_id:
            return None

        # Step 3: Fetch Template
        template_url = f"{TEMPLATE_URL_BASE}{template_id}?format=json"
        template_data = self.fetch_json(template_url, f"{sport_name} Template")
        if not template_data:
            return None

        # Step 4: Extract ALL Market Queries
        queries = self.extract_all_market_queries(template_data)
        logger.info(f"Found {len(queries)} potential market queries for {sport_name}")

        # Step 5: Iterate and find the one with Game Lines
        target_subcategory_id = SUBCATEGORY_IDS.get(sport_name)
        if not target_subcategory_id:
            logger.warning(f"No known subcategory ID for {sport_name}, skipping substitution attempt")
            return None

        for query in queries:
            # Skip queries that look like they are for specific events
            if 'eventId' in query['eventsQuery']:
                continue

            # Skip queries that don't use subcategoryId
            if '@subcategoryId' not in query['eventsQuery']:
                continue

            # Inject the target subcategory ID
            modified_query = {
                'name': query['name'],
                'eventsQuery': query['eventsQuery'].replace('@subcategoryId', target_subcategory_id),
                'marketsQuery': query['marketsQuery'].replace('@subcategoryId', target_subcategory_id)
            }
            
            market_url = self.construct_market_url(modified_query, league_id=numeric_league_id)
            market_data = self.fetch_json(market_url, f"Market Data ({query['name']})")
            
            if market_data and market_data.get('events'):
                logger.info(f"Found data with {len(market_data['events'])} events using query {query['name']}")
                return market_data
                
        logger.error(f"Could not find any data for {sport_name} Game Lines")
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

    def parse_games(self, raw_data, sport_name) -> List[StandardizedGame]:
        """Parse DraftKings API response into StandardizedGame objects."""
        if not raw_data or not isinstance(raw_data, dict):
            logger.warning("Invalid or empty raw data received")
            return []

        events = raw_data.get("events", [])
        markets = raw_data.get("markets", [])
        selections = raw_data.get("selections", [])

        if not events:
            logger.info("No events found in DraftKings data")
            return []

        # Index selections by marketId
        selections_by_market = {}
        for sel in selections:
            market_id = sel.get('marketId')
            if market_id not in selections_by_market:
                selections_by_market[market_id] = []
            selections_by_market[market_id].append(sel)

        # Index markets by eventId
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
                    continue
                
                status = event.get("status", "UNKNOWN")

                # Create standardized game
                game = StandardizedGame(
                    sport=sport_name,
                    game_id=f"dk_{event_id}",
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
                    
                    # Filter for main markets only
                    if market_name not in ['Moneyline', 'Spread', 'Total']:
                        continue

                    mkt_selections = selections_by_market.get(market_id, [])
                    parsed_selections = []
                    
                    for sel in mkt_selections:
                        label = sel.get('label', 'Unknown')
                        odds = sel.get('displayOdds', {}).get('american', 'N/A')
                        
                        # Add points/line if available (for Spread/Total)
                        points = sel.get('points')
                        if points is not None:
                            label = f"{label} ({points})"
                            
                        parsed_selections.append(f"{label}: {odds}")
                    
                    game.add_market(market_name, parsed_selections)

                games.append(game)

            except Exception as e:
                logger.error(f"Error parsing event {event.get('id', 'unknown')}: {e}")
                continue

        logger.info(f"Successfully parsed {len(games)} games from DraftKings")
        return games

def main():
    logger.info("Starting Dynamic Games Fetch Test")
    
    client = DraftKingsDynamicClient()
    parser = DraftKingsParser()
    
    sports_to_test = ["NFL", "NBA"]
    
    for sport in sports_to_test:
        print(f"\n=== Fetching {sport} Games ===")
        raw_data = client.get_games_for_sport(sport)
        
        if raw_data:
            games = parser.parse_games(raw_data, sport)
            
            print(f"\nFound {len(games)} Upcoming {sport} Games:")
            print("-" * 60)
            for game in games:
                print(f"{game.away_team} @ {game.home_team}")
                print(f"  Start: {game.start_time}")
                print(f"  Status: {game.status}")
                print("-" * 60)
        else:
            print(f"Failed to fetch {sport} games data.")

if __name__ == "__main__":
    main()