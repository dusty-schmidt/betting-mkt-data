# scripts/verify_props.py
import sys
import os
import json

# Add src to pythonpath
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.providers.draftkings.client import DraftKingsDynamicClient
from src.providers.draftkings.parser import parse_odds
from src.core.logger import get_logger

log = get_logger(__name__)

def verify_nba_props():
    print("\n--- Verifying NBA Player Points Props ---")
    
    client = DraftKingsDynamicClient()
    
    print("Fetching NBA Player Points Data...")
    # Fetch using the 'player_points' subcategory defined in config
    raw_data = client.get_games_for_sport("NBA", subcategory_name="player_points")
    
    if not raw_data:
        print("ERROR: Failed to fetch player points data.")
        return

    print("Parsing Data...")
    # The current parser is optimized for game lines (Moneyline, Spread, Total)
    # But let's see what it does with props. It presumably has logic to attach generic markets.
    # However, the parser specifically filters for ['Moneyline', 'Spread', 'Total'].
    # We might need to inspect the raw markets first to see if they're coming through.
    
    if 'events' in raw_data:
        print(f"Fetched {len(raw_data['events'])} events with prop data.")
    
    if 'markets' in raw_data:
        print(f"Fetched {len(raw_data['markets'])} total markets.")
        
        # Sample some market names
        market_names = set()
        for m in raw_data['markets'][:20]:
            market_names.add(m.get('name'))
        
        print(f"Sample Market Names: {market_names}")
        
        # Check for 'Points' related markets
        points_markets = [m for m in raw_data['markets'] if 'Points' in m.get('name', '')]
        if points_markets:
             print(f"Found {len(points_markets)} markets containing 'Points'.")
             print(f"Example: {points_markets[0]['name']}")
             
             # Check selections for the first points market
             mkt_id = points_markets[0]['id']
             selections = [s for s in raw_data.get('selections', []) if s.get('marketId') == mkt_id]
             print(f"Selections for {points_markets[0]['name']} ({len(selections)}):")
             for s in selections[:5]:
                 print(f"  - {s.get('label')}: {s.get('displayOdds', {}).get('american')}")
        else:
             print("WARNING: No 'Points' markets found.")

    else:
        print("WARNING: No markets found in raw response.")

if __name__ == "__main__":
    verify_nba_props()
