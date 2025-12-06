# scripts/inspect_template.py
import sys
import os
import json

# Add src to pythonpath
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.providers.draftkings.client import DraftKingsDynamicClient

def inspect_template(sport_name="NFL"):
    print(f"\n--- Inspecting Template for {sport_name} ---")
    client = DraftKingsDynamicClient()
    
    # 1. Fetch Manifest
    manifest = client.fetch_json(client.manifest_url, "Manifest")
    if not manifest: return

    # 2. Find League Info
    template_id, league_id = client.find_league_info(manifest, sport_name)
    print(f"Template ID: {template_id}")
    print(f"League ID: {league_id}")
    
    if not template_id: return

    # 3. Fetch Template
    template_url = f"{client.template_url_base}{template_id}?format=json"
    template = client.fetch_json(template_url, "Template")
    
    if not template: return

    # 4. Inspect Data Sets (Queries)
    print("\n[Data Sets / Queries]")
    sets = template.get('data', {}).get('sets', [])
    for s in sets:
        name = s.get('name')
        provider = s.get('provider')
        params = s.get('parameters', {})
        
        m_query = params.get('marketsQuery', '')
        e_query = params.get('eventsQuery', '')
        
        if provider == 'Markets':
            print(f"  - Name: {name}")
            print(f"    Markets Query: {m_query[:100]}...")
            print(f"    Events Query: {e_query[:100]}...")
            
    # 5. Inspect Navigation / Modules for Subcategory ID mappings
    # Often found in 'modules' -> 'items' -> metadata
    print("\n[Modules / Navigation]")
    modules = template.get('modules', [])
    _recursive_module_search(modules)

def _recursive_module_search(items, level=0):
    indent = "  " * level
    if isinstance(items, list):
        for item in items:
            _recursive_module_search(item, level)
    elif isinstance(items, dict):
        # Print the type/keys of this dict to understand structure
        # name = items.get('name') or items.get('displayName') or items.get('title')
        # print(f"{indent}Dict Keys: {list(items.keys())}")
        
        # Check if this is a Navigation module
        c_type = items.get('componentType', '')
        m_type = items.get('type', '')
        if 'Navigation' in c_type or 'Navigation' in m_type:
            print(f"{indent}FOUND NAVIGATION MODULE: {c_type or m_type}")
            print(f"{indent}Keys: {list(items.keys())}")
            # Dump the whole thing key by key to avoid truncation
            print(f"{indent}Content:")
            import json
            print(json.dumps(items, indent=2))
            
        elif 'subcategoryId' in str(items):
             pass # Already finding these, keep quiet to reduce noise, or modify as needed

        # Recurse
        for k, v in items.items():
            if isinstance(v, (list, dict)):
                 _recursive_module_search(v, level + 1)

if __name__ == "__main__":
    inspect_template("NFL")
