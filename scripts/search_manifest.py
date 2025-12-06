# scripts/search_manifest.py
import sys
import os
import json
import re

# Add src to pythonpath
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.providers.draftkings.client import DraftKingsDynamicClient

def search_manifest_content():
    client = DraftKingsDynamicClient()
    print("Fetching Manifest...")
    manifest = client.fetch_json(client.manifest_url, "Manifest")
    
    if not manifest:
        print("Failed.")
        return

    manifest_str = json.dumps(manifest)
    
    # 1. Search for known IDs to see where they live
    print("\n--- Locating Known IDs ---")
    known_ids = ["4518", "16477", "88808", "42648"]
    for kid in known_ids:
        print(f"Searching for {kid}...")
        # Find all occurrences and print context
        matches = [m.start() for m in re.finditer(kid, manifest_str)]
        print(f"  Found {len(matches)} occurrences.")
        for start in matches[:3]: # Show first 3 contexts
            ctx_start = max(0, start - 100)
            ctx_end = min(len(manifest_str), start + 100)
            print(f"  Context: ...{manifest_str[ctx_start:ctx_end]}...")

    # 2. Search for "Props" or "Touchdown"
    print("\n--- Searching for 'Props' ---")
    matches = [m.start() for m in re.finditer("Props", manifest_str)]
    print(f"  Found {len(matches)} occurrences.")
    for start in matches[:5]:
        ctx_start = max(0, start - 200)
        ctx_end = min(len(manifest_str), start + 200)
        print(f"  Context: ...{manifest_str[ctx_start:ctx_end]}...")

    # 3. Search for "Player Points"
    print("\n--- Searching for 'Player Points' ---")
    matches = [m.start() for m in re.finditer("Player Points", manifest_str)]
    print(f"  Found {len(matches)} occurrences.")
    for start in matches[:5]:
        ctx_start = max(0, start - 200)
        ctx_end = min(len(manifest_str), start + 200)
        print(f"  Context: ...{manifest_str[ctx_start:ctx_end]}...")

if __name__ == "__main__":
    search_manifest_content()
