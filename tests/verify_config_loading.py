# tests/verify_config_loading.py
import sys
import os

# Add src to pythonpath
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.core.config import load_config

def verify_config():
    config = load_config()
    
    print("Verifying DraftKings Configuration...")
    dk_config = config.get_provider_config("DraftKings")
    
    if not dk_config:
        print("FAIL: DraftKings config not found")
        sys.exit(1)
        
    print("OK: Found DraftKings config")
    
    # Check headers
    if "User-Agent" not in dk_config.get("headers", {}):
        print("FAIL: Headers missing User-Agent")
        sys.exit(1)
    print("OK: Headers present")

    # Check NFL Mapping
    nfl_config = config.get_sport_config("DraftKings", "NFL")
    if not nfl_config:
        print("FAIL: NFL config not found")
        sys.exit(1)
        
    expected_league_id = "88808"
    if nfl_config.get("league_id") != expected_league_id:
        print(f"FAIL: Expected NFL league_id {expected_league_id}, got {nfl_config.get('league_id')}")
        sys.exit(1)
    print(f"OK: NFL League ID matches {expected_league_id}")

    # Check Subcategories
    if nfl_config.get("subcategories", {}).get("game_lines") != "4518":
        print("FAIL: NFL Game Lines subcategory mismatch")
        sys.exit(1)
    print("OK: NFL Game Lines subcategory matches")

    print("\nSUCCESS: All config checks passed!")

if __name__ == "__main__":
    verify_config()
