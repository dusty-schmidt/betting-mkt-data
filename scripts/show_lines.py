# scripts/show_lines.py
import sys
import os
import json
from datetime import datetime

# Add src to pythonpath
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.providers.draftkings.client import DraftKingsDynamicClient
from src.providers.draftkings.parser import DraftKingsParser
from src.core.logger import get_logger

log = get_logger(__name__)

def print_game_summary(games, category_name):
    print(f"\n=== {category_name} ({len(games)} games found) ===")
    if not games:
        print("  No games found.")
        return

    # Print first 3 games as sample
    for game in games[:3]:
        print(f"\n  Game: {game.away_team} @ {game.home_team} ({game.status})")
        print(f"  Markets Found: {len(game.markets)}")
        
        # Print a few markets
        for mkt_name, selections in list(game.markets.items())[:5]:
            print(f"    - {mkt_name}:")
            # Print first 3 selections
            for sel in selections[:3]:
                print(f"      * {sel['label']}: {sel['odds']}")
            if len(selections) > 3:
                print(f"      * ... ({len(selections)-3} more)")

def main():
    client = DraftKingsDynamicClient()
    parser = DraftKingsParser()
    
    sports_to_check = [
        ("NBA", "game_lines", "Game Lines"),
        ("NBA", "player_points", "Player Points"),
        ("NFL", "game_lines", "Game Lines"),
        ("NFL", "player_rushing", "Player Rushing"),
    ]
    
    for sport, subcat, label in sports_to_check:
        print(f"\nFetching {sport} - {label}...")
        try:
            raw_data = client.get_games_for_sport(sport, subcategory_name=subcat)
            if raw_data:
                games = parser.parse_games(raw_data, sport_name=sport)
                print_game_summary(games, f"{sport} {label}")
            else:
                print(f"  No raw data returned for {sport} {label}.")
        except Exception as e:
            print(f"  Error fetching/parsing: {e}")

if __name__ == "__main__":
    main()
