# scripts/discover_all_subcategories.py
import sys
import os
import json
import re

# Add src to pythonpath
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.providers.draftkings.client import DraftKingsDynamicClient
from src.core.logger import get_logger

log = get_logger(__name__)

# Heuristic Mapping of Common Subcategory Names to Keys
# This helps us normalize weird API names into clean config keys
# e.g. "Player Points" -> "player_points"
def normalize_key(name):
    # Remove special chars and lowercase
    clean = re.sub(r'[^a-zA-Z0-9\s]', '', name).lower()
    return clean.replace(' ', '_')

def extract_subcategories_from_template(template_data):
    """
    Traverses the template modules to find navigation items that link to subcategories.
    Returns a dict: { "Normalized Key": { "id": "123", "label": "Original Label" } }
    """
    found_subs = {}
    
    # We are looking for structure that resembles navigation tabs
    # Often in 'modules' -> type='SubcategoryNavigation' or similar
    # OR recursively checking for 'subcategoryId' in metadata
    
    modules = template_data.get('modules', [])
    
    def _recursive_search(items):
        if isinstance(items, list):
            for item in items:
                _recursive_search(item)
        elif isinstance(items, dict):
            # Check if this item defines a subcategory link
            # Indicators: 'subcategoryId' in parameters or metadata
            sub_id = None
            label = items.get('title') or items.get('name') or items.get('displayName')
            
            # Check params
            params = items.get('parameters', {})
            if 'subcategoryId' in params:
                sub_id = params['subcategoryId']
                
            # Check metadata
            if not sub_id:
                meta = items.get('metadata', {})
                if 'subcategoryId' in meta:
                    sub_id = meta['subcategoryId']
                
            # If found valid subcategory
            if sub_id and label:
                # Filter out generic/useless labels if necessary
                if "Featured" not in label and "Same Game Parlay" not in label:
                    key = normalize_key(label)
                    if key not in found_subs:
                        found_subs[key] = {"id": str(sub_id), "label": label}
            
            # Recurse
            for k, v in items.items():
                if isinstance(v, (list, dict)):
                    _recursive_search(v)
                    
    _recursive_search(modules)
    return found_subs

def main():
    client = DraftKingsDynamicClient()
    
    target_sports = ["NFL", "NBA", "NHL", "MLB"]
    master_map = {}
    
    print("--- Starting DraftKings Subcategory Discovery ---")
    
    # 1. Fetch Manifest
    manifest = client.fetch_json(client.manifest_url, "Manifest")
    if not manifest:
        print("CRITICAL: Failed to fetch manifest.")
        return

    for sport in target_sports:
        print(f"\nProcessing {sport}...")
        
        # 2. Get Lead/Template Info from Manifest
        template_id, league_id = client.find_league_info(manifest, sport)
        
        if not template_id or not league_id:
            print(f"  Skipping {sport}: Could not find league info.")
            continue
            
        print(f"  League ID: {league_id}")
        
        # 3. Fetch Template
        template_url = f"{client.template_url_base}{template_id}?format=json"
        template_data = client.fetch_json(template_url, f"{sport} Template")
        
        if not template_data:
             print(f"  Skipping {sport}: Failed to fetch template.")
             continue
             
        # 4. Extract Subcategories
        subcats = extract_subcategories_from_template(template_data)
        
        if subcats:
            print(f"  Found {len(subcats)} subcategories:")
            for key, data in subcats.items():
                print(f"    - {data['label']} -> {data['id']} (key: {key})")
            
            master_map[sport] = {
                "league_id": league_id,
                "subcategories": {k: v['id'] for k, v in subcats.items()}
            }
        else:
             print("  No subcategories found in template (Structure might be different).")

    # 5. Output Result as YAML fragment for easy copying
    print("\n\n--- DISCOVERY RESULTS (Copy to config.yaml) ---")
    import yaml
    print(yaml.dump(master_map, sort_keys=True))

if __name__ == "__main__":
    main()
