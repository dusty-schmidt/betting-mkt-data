# scripts/dump_manifest.py
import sys
import os
import json

# Add src to pythonpath
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.providers.draftkings.client import DraftKingsDynamicClient

def main():
    client = DraftKingsDynamicClient()
    manifest = client.fetch_json(client.manifest_url, "Manifest")
    
    if manifest:
        outfile = "debug_manifest.json"
        with open(outfile, 'w') as f:
            json.dump(manifest, f, indent=2)
        print(f"Saved manifest to {outfile}")

if __name__ == "__main__":
    main()
