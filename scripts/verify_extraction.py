# scripts/verify_extraction.py
import sys
import os
import json

# Add src to pythonpath
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.providers.draftkings.client import DraftKingsClient, DraftKingsDynamicClient
from src.providers.draftkings.parser import parse_odds
from src.core.logger import get_logger

log = get_logger(__name__)

def verify_nfl_extraction():
    print("\n--- Verifying NFL Market Extraction ---")
    
    # Use dynamic client for best results
    client = DraftKingsDynamicClient()
    
    print("Fetching NFL Data...")
    raw_data = client.get_games_for_sport("NFL")
    
    if not raw_data:
        print("ERROR: Failed to fetch data.")
        return

    print("Parsing Data...")
    games = parse_odds(raw_data, sport_name="NFL")
    
    print(f"Parsed {len(games)} games.")
    
    if not games:
        print("ERROR: No games parsed.")
        return

    # Check for markets in the first few games
    games_checked = 0
    markets_found = set()
    
    for game in games[:5]:
        print(f"\nGame: {game.away_team} @ {game.home_team}")
        print(f"Markets: {list(game.markets.keys())}")
        
        markets_found.update(game.markets.keys())
        
        # Detail check for a specific market if present
        if 'Spread' in game.markets:
            spreads = game.markets['Spread']
            print(f"  Spread Selections ({len(spreads)}):")
            for sel in spreads:
                print(f"    - {sel['label']}: {sel['odds']}")

    print("\n--- Extraction Summary ---")
    required_markets = {'Moneyline', 'Spread', 'Total'}
    missing = required_markets - markets_found
    
    if missing:
        print(f"FAIL: Missing extraction for markets: {missing}")
    else:
        print("SUCCESS: All required markets (Moneyline, Spread, Total) extracted.")

if __name__ == "__main__":
    verify_nfl_extraction()
