"""
Configuration constants for DraftKings dynamic API discovery.

This module contains static configuration values extracted from the DraftKings
dynamic games test implementation. These constants are used by the dynamic
client to discover and interact with DraftKings sportsbook APIs.

The constants are organized into logical groups:
- URL configurations for different API endpoints
- HTTP headers for requests
- Sport-specific mappings and identifiers
"""

# Base URL Configuration
# ==============================================================================
BASE_URL = "https://sportsbook-nash.draftkings.com"
MANIFEST_URL = f"{BASE_URL}/sites/US-OH-SB/api/sportslayout/v1/manifest?format=json"
TEMPLATE_URL_BASE = f"{BASE_URL}/sites/US-OH-SB/api/sportsstructure/v1/templates/"
MARKET_URL_BASE = f"{BASE_URL}/sites/US-OH-SB/api/sportscontent/controldata/league/leagueSubcategory/v1/markets"


# HTTP Headers Configuration
# ==============================================================================
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


# Sport-Specific Mappings
# ==============================================================================

# Known Subcategory IDs for Game Lines
SUBCATEGORY_IDS = {
    "NFL": "4518",
    "NBA": "4511"
}

# League Route Mapping
LEAGUE_ROUTES = {
    "NFL": "/leagues/football/nfl",
    "NBA": "/leagues/basketball/nba"
}