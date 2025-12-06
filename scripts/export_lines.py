# scripts/export_lines.py
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

def json_serial(obj):
    """JSON serializer for objects not serializable by default json code"""
    if isinstance(obj, datetime):
        return obj.isoformat()
    return str(obj)

def save_to_json(games, filename):
    filepath = os.path.join("output", filename)
    data = []
    for game in games:
        # Pydantic v1 vs v2 combatibility
        if hasattr(game, 'model_dump'):
            g_dict = game.model_dump()
        else:
            g_dict = game.dict()
        data.append(g_dict)
        
    with open(filepath, 'w') as f:
        json.dump(data, f, indent=2, default=json_serial)
    print(f"Saved {len(games)} games to {filepath}")

def main():
    client = DraftKingsDynamicClient()
    parser = DraftKingsParser()
    
    # Define what we want to export
    export_tasks = [
        {"sport": "NBA", "subcat": "game_lines", "filename": "nba_game_lines.json"},
        {"sport": "NBA", "subcat": "player_points", "filename": "nba_player_points.json"},
        {"sport": "NFL", "subcat": "game_lines", "filename": "nfl_game_lines.json"},
        {"sport": "NFL", "subcat": "player_rushing", "filename": "nfl_player_rushing.json"},
    ]
    
    print("Starting export...")
    
    for task in export_tasks:
        sport = task["sport"]
        subcat = task["subcat"]
        filename = task["filename"]
        
        print(f"\nFetching {sport} - {subcat}...")
        try:
            raw_data = client.get_games_for_sport(sport, subcategory_name=subcat)
            if raw_data:
                games = parser.parse_games(raw_data, sport_name=sport)
                if games:
                    save_to_json(games, filename)
                else:
                    print(f"  No games parsed for {sport} {subcat}.")
            else:
                print(f"  No raw data returned for {sport} {subcat}.")
        except Exception as e:
            print(f"  Error exporting {sport} {subcat}: {e}")

if __name__ == "__main__":
    main()
