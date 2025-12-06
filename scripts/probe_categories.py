# scripts/probe_categories.py
import sys
import os
import json

# Add src to pythonpath
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.providers.draftkings.client import DraftKingsDynamicClient

def main():
    client = DraftKingsDynamicClient()
    
    # NFL League ID
    league_id = "88808" 
    
    league_id = "88808" 
    
    # Potential URLs to probe
    urls = [
        f"https://sportsbook-us-oh.draftkings.com//sites/US-OH-SB/api/v5/eventgroups/{league_id}/categories?format=json",
        f"https://sportsbook-us-oh.draftkings.com//sites/US-OH-SB/api/v1/eventgroups/{league_id}/categories?format=json",
        f"https://sportsbook-us-oh.draftkings.com//sites/US-OH-SB/api/v1/eventgroups/{league_id}/navigation?format=json",
        f"https://sportsbook-us-oh.draftkings.com//sites/US-OH-SB/api/v2/eventgroups/{league_id}/navigation?format=json",
        f"https://sportsbook-us-oh.draftkings.com//sites/US-OH-SB/api/v1/leagues/{league_id}/categories?format=json",
        # Config driven subcategories might come from here?
         f"https://sportsbook-us-oh.draftkings.com//sites/US-OH-SB/api/v1/eventgroups/{league_id}/full?format=json",
    ]
    
    for url in urls:
        print(f"\nProbing URL: {url}")
        try:
            data = client.fetch_json(url, "Probe")
            if data:
                print("SUCCESS! Data retrieved.")
                outfile = f"debug_probe_{urls.index(url)}.json"
                with open(outfile, 'w') as f:
                    json.dump(data, f, indent=2)
                print(f"Saved to {outfile}")
                break # Stop after finding something? Maybe keep going to find the GOOD one.
        except Exception as e:
            print(f"Failed: {e}")

if __name__ == "__main__":
    main()
