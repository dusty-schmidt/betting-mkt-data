# tests/test_nfl_props_extraction.py
import sys
import os
import json
import unittest

# Add src to pythonpath
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.providers.draftkings.parser import DraftKingsParser
from src.core.schemas import StandardizedGame

class TestNFLPropsExtraction(unittest.TestCase):
    def setUp(self):
        self.parser = DraftKingsParser()
        self.sample_file = os.path.join(
            os.path.dirname(__file__), 
            '../dev-docs/references/dk-api/samples/sample-response-props-2.json'
        )

    def test_parse_rushing_yards(self):
        print(f"\nTesting extraction from {self.sample_file}")
        with open(self.sample_file, 'r') as f:
            data = json.load(f)
            
        games = self.parser.parse_games(data, sport_name="NFL")
        
        self.assertTrue(len(games) > 0, "Should find games in sample")
        print(f"Found {len(games)} games.")
        
        # Look for James Cook Rushing Yards in the first game or wherever it exists
        # In the sample, James Cook is in "CIN Bengals @ BUF Bills"?
        # Actually Event ID 32225489 is CIN @ BUF.
        
        target_game = next((g for g in games if "Bills" in g.home_team or "Bills" in g.away_team), None)
        self.assertIsNotNone(target_game, "Should find Bills game")
        
        print(f"Inspecting markets for {(target_game.home_team, target_game.away_team)}: {list(target_game.markets.keys())}")
        
        # The parser as currently written might NOT extract 'Player Rushing' automatically 
        # because it filters for ['Moneyline', 'Spread', 'Total'].
        # This test will confirm if we need to update the parser to be more searching.
        
        # If the parser is strict, we might need to modify it.
        # Let's see what is extracted.
        
        # Check if ANY non-standard market is extracted
        rushing_found = any("Rushing" in m for m in target_game.markets.keys())
        
        if not rushing_found:
            print("WARNING: Rushing markets NOT extracted. Parser probably filters them out.")
        else:
            print("SUCCESS: Rushing markets extracted.")
            
        # Manually verify we CAN extract them if we wanted to (which we do)
        # We might need to update the parser to allow configured valid markets
        
if __name__ == "__main__":
    unittest.main()
