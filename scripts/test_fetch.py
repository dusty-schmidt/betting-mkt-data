# scripts/test_fetch.py
import sys
import os
import json

# Add src to pythonpath
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.providers.draftkings.client import DraftKingsClient, DraftKingsDynamicClient
from src.core.logger import get_logger

log = get_logger(__name__)

def test_static_fetch():
    print("\n--- Testing Static Client (Standard API) ---")
    client = DraftKingsClient()
    
    # Test NFL (Sport ID 3)
    print("Fetching NFL Odds...")
    data = client.get_odds("3")
    
    if data and 'events' in data:
        events = data['events']
        print(f"SUCCESS: Fetched {len(events)} NFL events.")
        if len(events) > 0:
            print(f"Sample Event: {events[0].get('name')}")
    else:
        print("WARNING: No events found or request failed.")

def test_dynamic_fetch():
    print("\n--- Testing Dynamic Client (Discovery Flow) ---")
    client = DraftKingsDynamicClient()
    
    # Test NFL
    print("Fetching NFL Game Lines via Dynamic Flow...")
    try:
        data = client.get_games_for_sport("NFL")
        
        if data and 'events' in data:
            events = data['events']
            print(f"SUCCESS: Fetched {len(events)} NFL events via dynamic flow.")
            if len(events) > 0:
                print(f"Sample Event: {events[0].get('name')}")
        else:
            print("WARNING: Dynamic fetch returned no data.")
            
    except Exception as e:
        print(f"ERROR: Dynamic fetch failed with exception: {e}")

if __name__ == "__main__":
    test_static_fetch()
    # Uncomment to test dynamic flow if needed, but it might be slower/more complex
    # test_dynamic_fetch()
