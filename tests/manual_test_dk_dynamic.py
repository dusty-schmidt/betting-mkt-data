import requests
import json
import logging
import urllib.parse
import time

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

def fetch_json(url, description):
    """Helper to fetch JSON data with error handling."""
    try:
        logger.info(f"Fetching {description} from: {url}")
        response = requests.get(url, headers=HEADERS)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        logger.error(f"Failed to fetch {description}: {e}")
        if hasattr(e, 'response') and e.response is not None:
             logger.error(f"Response content: {e.response.text}")
        return None

def find_nfl_template_id(manifest_data):
    """Finds the templateId for the NFL league page."""
    if not manifest_data:
        return None
    
    for route_group in manifest_data.get('routes', []):
        if route_group.get('key') == 'league':
            for override in route_group.get('overrides', []):
                if override.get('seoRoute') == '/leagues/football/nfl':
                    template_id = override.get('templateId')
                    logger.info(f"Found NFL Template ID: {template_id}")
                    return template_id
    
    logger.error("Could not find NFL route in manifest.")
    return None

def extract_all_market_queries(template_data):
    """Extracts ALL market queries from the template."""
    if not template_data:
        return []

    queries = []
    data_sets = template_data.get('data', {}).get('sets', [])
    
    for data_set in data_sets:
        params = data_set.get('parameters', {})
        provider = data_set.get('provider')
        
        if provider == 'Markets':
            markets_query = params.get('marketsQuery', '')
            events_query = params.get('eventsQuery', '')
            
            # We want to capture everything that looks like a market query
            if markets_query and events_query:
                queries.append({
                    'name': data_set.get('name'),
                    'eventsQuery': events_query,
                    'marketsQuery': markets_query
                })

    return queries

def construct_market_url(queries, league_id):
    """Constructs the final API URL."""
    if not queries:
        return None
    
    # Perform substitution on the queries
    events_query = queries['eventsQuery'].replace('@leagueId', str(league_id))
    markets_query = queries['marketsQuery'].replace('@leagueId', str(league_id))
    
    # Some queries use @page.leagueId
    events_query = events_query.replace('@page.leagueId', str(league_id))
    markets_query = markets_query.replace('@page.leagueId', str(league_id))

    # Some queries use @subcategoryId - we might need to infer this or it might be hardcoded in the template
    # If it's not replaced, the API call might fail or return empty.
    # For now, let's see what happens.
    
    # The base URL parameters from the sample
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

def extract_league_id_from_template(template_data):
    """Attempts to find the numeric League ID from the template data."""
    if not template_data:
        return None
        
    data_sets = template_data.get('data', {}).get('sets', [])
    for data_set in data_sets:
        params = data_set.get('parameters', {})
        if 'link_LeagueId' in params:
            return params['link_LeagueId']
        if 'leagueId' in params:
            return params['leagueId']
            
    return None

def main():
    logger.info("Starting NFL Market Discovery Test")

    # Step 1: Fetch Manifest
    manifest_data = fetch_json(MANIFEST_URL, "Manifest")
    if not manifest_data:
        return

    # Step 2: Find NFL Template ID
    nfl_template_id = find_nfl_template_id(manifest_data)
    if not nfl_template_id:
        return

    # Step 3: Fetch Template
    template_url = f"{TEMPLATE_URL_BASE}{nfl_template_id}?format=json"
    template_data = fetch_json(template_url, "NFL Template")
    if not template_data:
        return

    # Step 4: Extract Numeric League ID
    numeric_league_id = extract_league_id_from_template(template_data)
    if not numeric_league_id:
        logger.error("Could not find numeric League ID for NFL")
        return
    logger.info(f"Found Numeric League ID: {numeric_league_id}")

    # Step 5: Extract ALL Market Queries
    all_queries = extract_all_market_queries(template_data)
    logger.info(f"Found {len(all_queries)} market queries in the template")

    # Step 6: Fetch Data for Each Query
    for query in all_queries:
        market_url = construct_market_url(query, league_id=numeric_league_id)
        market_data = fetch_json(market_url, f"Market Data ({query['name']})")
        
        if market_data:
            events = market_data.get('events', [])
            markets = market_data.get('markets', [])
            selections = market_data.get('selections', [])
            
            if not events and not markets:
                continue

            print(f"\n=== Query Set: {query['name']} ===")
            print(f"Found {len(events)} events, {len(markets)} markets, {len(selections)} selections")

            # Create a map of markets for easy lookup
            market_map = {m['id']: m for m in markets}
            
            # Group selections by market
            selections_by_market = {}
            for sel in selections:
                market_id = sel.get('marketId')
                if market_id not in selections_by_market:
                    selections_by_market[market_id] = []
                selections_by_market[market_id].append(sel)

            for event in events[:3]: # Show first 3 events
                print(f"\n  Event: {event.get('name')} (ID: {event.get('id')})")
                
                # Find markets for this event
                event_markets = [m for m in markets if m.get('eventId') == event.get('id')]
                
                # Group markets by name/type
                markets_by_type = {}
                for m in event_markets:
                    m_name = m.get('name') or m.get('marketType', {}).get('name')
                    if m_name not in markets_by_type:
                        markets_by_type[m_name] = []
                    markets_by_type[m_name].append(m)

                for m_name, m_list in list(markets_by_type.items())[:3]: # Show first 3 market types
                    print(f"    Market: {m_name}")
                    for m in m_list[:2]: # Show first 2 instances of this market type
                        m_selections = selections_by_market.get(m['id'], [])
                        if m_selections:
                            print(f"      Selections:")
                            for sel in m_selections:
                                label = sel.get('label')
                                odds = sel.get('displayOdds', {}).get('american')
                                print(f"        - {label}: {odds}")
        else:
            logger.error(f"  Failed to fetch market data for {query['name']}")
        
        time.sleep(1)

if __name__ == "__main__":
    main()