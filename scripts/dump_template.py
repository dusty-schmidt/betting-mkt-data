# scripts/dump_template.py
import sys
import os
import json

# Add src to pythonpath
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.providers.draftkings.client import DraftKingsDynamicClient

def main():
    client = DraftKingsDynamicClient()
    
    # 1. Fetch Manifest
    print("Fetching Manifest...")
    manifest = client.fetch_json(client.manifest_url, "Manifest")
    if not manifest:
        return

    # 2. Get NFL Template
    print("Finding NFL Template...")
    template_id, league_id = client.find_league_info(manifest, "NFL")
    
    if not template_id:
        print("Could not find NFL template.")
        return
        
    print(f"Template ID: {template_id}")
    
    # 3. Fetch Template
    template_url = f"{client.template_url_base}{template_id}?format=json"
    print(f"Fetching Template: {template_url}")
    template_data = client.fetch_json(template_url, "NFL Template")
    
    if template_data:
        outfile = "debug_template.json"
        with open(outfile, 'w') as f:
            json.dump(template_data, f, indent=2)
        print(f"Saved template to {outfile}")

if __name__ == "__main__":
    main()
