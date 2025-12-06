# scripts/discover_subcategories.py
import sys
import os
import json

# Add src to pythonpath
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.providers.draftkings.client import DraftKingsDynamicClient
from src.core.logger import get_logger

log = get_logger(__name__)

def inspect_manifest(sport_name="NFL"):
    print(f"\n--- Inspecting Manifest for {sport_name} Subcategories ---")
    client = DraftKingsDynamicClient()
    
    # 1. Fetch Manifest
    manifest = client.fetch_json(client.manifest_url, "Manifest")
    if not manifest:
        print("Failed to fetch manifest")
        return

    # 2. Find League ID (to ensure we are looking at the right section)
    # We'll reuse the logic from client to find the league ID first
    _, league_id = client.find_league_info(manifest, sport_name)
    print(f"Target League ID for {sport_name}: {league_id}")

    # 3. Traverse Manifest for Subcategories
    # The structure is often:
    # menus -> items (Sports) -> items (Leagues) -> items (Subcategories)
    # OR sometimes routes -> overrides...
    
    # Let's look for the 'menus' section which often defines the navigation hierarchy
    menus = manifest.get('menus', [])
    
    found = False
    for menu in menus:
        for item in menu.get('items', []):
            # Check if this item is our sport (by name or some predictable ID)
            # The structure varies, but often top level items are Key Sports
            
            # Let's try to recursively find the League ID
            if _recursive_search(item, league_id):
                found = True
                
    if not found:
        print("Could not locate league in menu hierarchy.")
        
def _recursive_search(item, target_league_id, level=0):
    # Check if this item IS the league
    # Items often have 'path' or 'route' or 'metadata'
    
    name = item.get('displayName') or item.get('name') or "Unknown"
    indent = "  " * level
    
    # Check if this item links to our league ID
    # Sometimes it's in 'parameters' -> 'leagueId'
    item_league_id = str(item.get('parameters', {}).get('leagueId', ''))
    
    if item_league_id == str(target_league_id):
        print(f"{indent}[LEAGUE FOUND] {name} (ID: {item_league_id})")
        # Print children (Subcategories)
        if 'items' in item:
            print(f"{indent}  Subcategories:")
            for child in item['items']:
                child_name = child.get('displayName') or child.get('name')
                child_sub_id = child.get('parameters', {}).get('subcategoryId')
                if child_sub_id:
                     print(f"{indent}    - {child_name}: {child_sub_id}")
        return True
        
    # Recurse
    if 'items' in item:
        for child in item['items']:
            if _recursive_search(child, target_league_id, level + 1):
                return True
                
    return False

if __name__ == "__main__":
    inspect_manifest("NFL")
    inspect_manifest("NBA")
