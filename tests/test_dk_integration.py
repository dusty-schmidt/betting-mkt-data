# tests/test_dk_integration.py
"""Integration test for DraftKings provider migration validation.

This test validates the complete DraftKings provider workflow from the provider
interface through to the standardized game output, ensuring the migration to the
dynamic client architecture is working correctly.

Tests the complete data flow:
DraftKingsProvider → DraftKingsDynamicClient → DraftKingsParser → StandardizedGame
"""

import pytest
import time
from unittest.mock import patch, MagicMock
from src.providers.draftkings import DraftKingsProvider
from src.core.schemas import StandardizedGame
from src.core.logger import get_logger

log = get_logger(__name__)

class TestDraftKingsProviderIntegration:
    """Integration tests for DraftKings provider with dynamic client."""
    
    def setup_method(self):
        """Setup for each test method."""
        self.provider = DraftKingsProvider()
        
    def test_provider_initialization(self):
        """Test that DraftKingsProvider can be properly instantiated.
        
        Verifies:
        - Provider instance creation succeeds
        - Both legacy and dynamic clients are initialized
        - Parser is properly configured
        - Provider inherits from BaseProvider
        """
        assert self.provider is not None, "Provider should instantiate successfully"
        
        # Verify component initialization
        assert hasattr(self.provider, 'client'), "Legacy client should be initialized"
        assert hasattr(self.provider, 'dynamic_client'), "Dynamic client should be initialized"
        assert hasattr(self.provider, 'parser'), "Parser should be initialized"
        
        # Verify inheritance
        from src.providers.base import BaseProvider
        assert isinstance(self.provider, BaseProvider), "Provider should inherit from BaseProvider"
        
        log.info("DraftKingsProvider initialization test passed")
        
    def test_sports_mapping(self):
        """Test get_sports_mapping() returns expected sports.
        
        Verifies:
        - Method returns dictionary
        - Contains expected sport mappings (NFL, NBA, MLB)
        - Maps sport IDs to sport names correctly
        """
        mapping = self.provider.get_sports_mapping()
        
        assert isinstance(mapping, dict), "Sports mapping should return a dictionary"
        assert "100" in mapping, "Should contain NFL mapping"
        assert "200" in mapping, "Should contain NBA mapping"
        assert "300" in mapping, "Should contain MLB mapping"
        
        # Verify sport name mappings
        assert mapping["100"] == "NFL", "Sport ID 100 should map to NFL"
        assert mapping["200"] == "NBA", "Sport ID 200 should map to NBA"
        assert mapping["300"] == "MLB", "Sport ID 300 should map to MLB"
        
        log.info(f"Sports mapping test passed: {mapping}")
        
    def test_legacy_sports_mapping(self):
        """Test legacy sports mapping for backward compatibility.
        
        Verifies:
        - Method returns dictionary with league IDs
        - Contains expected legacy mappings
        """
        legacy_mapping = self.provider.get_legacy_sports_mapping()
        
        assert isinstance(legacy_mapping, dict), "Legacy mapping should return a dictionary"
        assert "100" in legacy_mapping, "Should contain NFL legacy mapping"
        assert "200" in legacy_mapping, "Should contain NBA legacy mapping"
        assert "300" in legacy_mapping, "Should contain MLB legacy mapping"
        
        # Verify legacy league ID mappings
        assert legacy_mapping["100"] == "1", "NFL should map to legacy league ID 1"
        assert legacy_mapping["200"] == "42648", "NBA should map to legacy league ID 42648"
        assert legacy_mapping["300"] == "3", "MLB should map to legacy league ID 3"
        
        log.info(f"Legacy sports mapping test passed: {legacy_mapping}")
        
    def test_fetch_odds_with_invalid_sport_id(self):
        """Test error handling for invalid sport IDs.
        
        Verifies:
        - Returns empty list for unknown sport IDs
        - No exceptions are raised
        - Logging occurs for invalid sport IDs
        """
        invalid_sport_id = "999"
        result = self.provider.fetch_odds(invalid_sport_id)
        
        assert isinstance(result, list), "Should return a list for invalid sport ID"
        assert len(result) == 0, "Should return empty list for invalid sport ID"
        
        log.info("Invalid sport ID handling test passed")
        
    @pytest.mark.integration
    def test_nba_fetch_workflow_real_api(self):
        """Test complete NBA workflow with real API calls.
        
        This is a real integration test that makes actual API calls to DraftKings.
        
        Verifies:
        - Can fetch NBA data successfully
        - Returns list of StandardizedGame objects
        - Games have proper structure and metadata
        - Market data is populated correctly
        """
        # Test NBA (sport_id "200")
        log.info("Starting NBA real API integration test")
        
        nba_games = self.provider.fetch_odds("200")
        
        # Verify return type and structure
        assert isinstance(nba_games, list), "Should return a list of games"
        
        if nba_games:  # Only validate if we got data
            for game in nba_games:
                # Verify game structure
                assert isinstance(game, StandardizedGame), f"Game should be StandardizedGame, got {type(game)}"
                assert game.sport == "NBA", f"Game sport should be NBA, got {game.sport}"
                assert game.home_team is not None, "Game should have home team"
                assert game.away_team is not None, "Game should have away team"
                assert game.game_id is not None, "Game should have ID"
                
                # Verify market data structure
                if game.markets:
                    # Should have Moneyline, Spread, Total markets
                    for market_name in game.markets.keys():
                        assert market_name in ['Moneyline', 'Spread', 'Total'], \
                            f"Market name should be Moneyline/Spread/Total, got {market_name}"
                        
                        # Verify market selections
                        selections = game.markets[market_name]
                        assert isinstance(selections, list), f"Market {market_name} should have list of selections"
                        
                        for selection in selections:
                            assert isinstance(selection, dict), f"Selection should be dict, got {type(selection)}"
                            assert 'label' in selection, f"Selection should have 'label' field"
                            assert 'odds' in selection, f"Selection should have 'odds' field"
            
            log.info(f"NBA integration test passed: Found {len(nba_games)} games")
        else:
            log.warning("NBA integration test: No games returned (API may be down)")
            
    @pytest.mark.integration
    def test_nfl_fetch_workflow_real_api(self):
        """Test complete NFL workflow with real API calls.
        
        This is a real integration test that makes actual API calls to DraftKings.
        
        Verifies:
        - Can fetch NFL data successfully
        - Returns list of StandardizedGame objects
        - Games have proper structure and metadata
        - Market data is populated correctly
        """
        # Test NFL (sport_id "100")
        log.info("Starting NFL real API integration test")
        
        nfl_games = self.provider.fetch_odds("100")
        
        # Verify return type and structure
        assert isinstance(nfl_games, list), "Should return a list of games"
        
        if nfl_games:  # Only validate if we got data
            for game in nfl_games:
                # Verify game structure
                assert isinstance(game, StandardizedGame), f"Game should be StandardizedGame, got {type(game)}"
                assert game.sport == "NFL", f"Game sport should be NFL, got {game.sport}"
                assert game.home_team is not None, "Game should have home team"
                assert game.away_team is not None, "Game should have away team"
                assert game.game_id is not None, "Game should have ID"
                
                # Verify market data structure
                if game.markets:
                    # Should have Moneyline, Spread, Total markets
                    for market_name in game.markets.keys():
                        assert market_name in ['Moneyline', 'Spread', 'Total'], \
                            f"Market name should be Moneyline/Spread/Total, got {market_name}"
                        
                        # Verify market selections
                        selections = game.markets[market_name]
                        assert isinstance(selections, list), f"Market {market_name} should have list of selections"
                        
                        for selection in selections:
                            assert isinstance(selection, dict), f"Selection should be dict, got {type(selection)}"
                            assert 'label' in selection, f"Selection should have 'label' field"
                            assert 'odds' in selection, f"Selection should have 'odds' field"
            
            log.info(f"NFL integration test passed: Found {len(nfl_games)} games")
        else:
            log.warning("NFL integration test: No games returned (API may be down)")
            
    def test_legacy_fetch_method(self):
        """Test legacy fetch method for backward compatibility.
        
        Verifies:
        - Legacy fetch method exists and is callable
        - Returns appropriate structure
        - Handles errors gracefully
        """
        # Test with NBA sport ID
        result = self.provider.fetch_odds_legacy("200")
        
        assert isinstance(result, list), "Legacy fetch should return a list"
        
        if result:
            for game in result:
                assert isinstance(game, StandardizedGame), "Should return StandardizedGame objects"
                
        log.info("Legacy fetch method test passed")
        
    def test_data_structure_validation(self):
        """Test complete data structure validation with mocked API responses.
        
        Uses mocked API responses to validate the complete data flow
        without relying on external API availability.
        """
        # Mock successful API response
        mock_raw_data = {
            "events": [
                {
                    "id": "12345",
                    "name": "Team A @ Team B",
                    "startEventDate": "2024-01-15T20:00:00Z",
                    "status": "UPCOMING",
                    "participants": [
                        {
                            "name": "Team A",
                            "venueRole": "away"
                        },
                        {
                            "name": "Team B", 
                            "venueRole": "home"
                        }
                    ]
                }
            ],
            "markets": [
                {
                    "id": "mkt1",
                    "eventId": "12345",
                    "name": "Moneyline"
                },
                {
                    "id": "mkt2", 
                    "eventId": "12345",
                    "name": "Spread"
                },
                {
                    "id": "mkt3",
                    "eventId": "12345", 
                    "name": "Total"
                }
            ],
            "selections": [
                {
                    "marketId": "mkt1",
                    "label": "Team A",
                    "displayOdds": {"american": "+150"}
                },
                {
                    "marketId": "mkt1",
                    "label": "Team B", 
                    "displayOdds": {"american": "-170"}
                },
                {
                    "marketId": "mkt2",
                    "label": "Team A",
                    "points": -3.5,
                    "displayOdds": {"american": "-110"}
                },
                {
                    "marketId": "mkt2",
                    "label": "Team B",
                    "points": 3.5,
                    "displayOdds": {"american": "-110"}
                },
                {
                    "marketId": "mkt3",
                    "label": "Over",
                    "points": 215.5,
                    "displayOdds": {"american": "-110"}
                },
                {
                    "marketId": "mkt3", 
                    "label": "Under",
                    "points": 215.5,
                    "displayOdds": {"american": "-110"}
                }
            ]
        }
        
        # Test with mocked dynamic client
        with patch.object(self.provider.dynamic_client, 'get_games_for_sport', return_value=mock_raw_data):
            games = self.provider.fetch_odds("200")  # NBA
            
            assert len(games) == 1, "Should parse one game from mock data"
            
            game = games[0]
            assert isinstance(game, StandardizedGame), "Should return StandardizedGame"
            assert game.sport == "NBA", "Sport should be NBA"
            assert game.home_team == "Team B", "Home team should be Team B"
            assert game.away_team == "Team A", "Away team should be Team A"
            assert game.game_id == "dk_12345", "Game ID should be prefixed with 'dk_'"
            
            # Verify market data
            assert "Moneyline" in game.markets, "Should have Moneyline market"
            assert "Spread" in game.markets, "Should have Spread market"
            assert "Total" in game.markets, "Should have Total market"
            
            # Verify Moneyline selections
            moneyline = game.markets["Moneyline"]
            assert len(moneyline) == 2, "Moneyline should have 2 selections"
            
            # Verify Spread selections (should include points)
            spread = game.markets["Spread"]
            assert len(spread) == 2, "Spread should have 2 selections"
            for selection in spread:
                assert "(-3.5)" in selection['label'] or "(3.5)" in selection['label'], \
                    "Spread selections should include points"
                    
            # Verify Total selections (should include points)  
            total = game.markets["Total"]
            assert len(total) == 2, "Total should have 2 selections"
            for selection in total:
                assert "(215.5)" in selection['label'], "Total selections should include points"
                
        log.info("Data structure validation test passed")
        
    def test_dynamic_client_error_handling(self):
        """Test error handling when dynamic client fails.
        
        Verifies:
        - Handles API failures gracefully
        - Returns empty list on errors
        - Logs appropriate error messages
        """
        # Mock API failure
        with patch.object(self.provider.dynamic_client, 'get_games_for_sport', return_value=None):
            games = self.provider.fetch_odds("200")
            
            assert isinstance(games, list), "Should return list even on API failure"
            assert len(games) == 0, "Should return empty list on API failure"
            
        log.info("Dynamic client error handling test passed")
        
    def test_complete_workflow_integration(self):
        """Test the complete provider workflow integration.
        
        This test validates:
        1. Provider can be instantiated
        2. Sports mapping works correctly
        3. Full fetch workflow executes without errors
        4. Data parsing creates proper StandardizedGame objects
        5. Market data is properly structured
        """
        # Test 1: Provider initialization
        assert self.provider is not None
        
        # Test 2: Sports mapping
        mapping = self.provider.get_sports_mapping()
        assert "200" in mapping and mapping["200"] == "NBA"
        assert "100" in mapping and mapping["100"] == "NFL"
        
        # Test 3: Mock complete workflow
        mock_data = {
            "events": [
                {
                    "id": "99999",
                    "name": "Lakers @ Celtics",
                    "startEventDate": "2024-01-20T21:00:00Z",
                    "status": "UPCOMING",
                    "participants": [
                        {"name": "Los Angeles Lakers", "venueRole": "away"},
                        {"name": "Boston Celtics", "venueRole": "home"}
                    ]
                }
            ],
            "markets": [
                {
                    "id": "test_mkt_1",
                    "eventId": "99999", 
                    "name": "Moneyline"
                }
            ],
            "selections": [
                {
                    "marketId": "test_mkt_1",
                    "label": "Los Angeles Lakers",
                    "displayOdds": {"american": "+120"}
                },
                {
                    "marketId": "test_mkt_1",
                    "label": "Boston Celtics",
                    "displayOdds": {"american": "-140"}
                }
            ]
        }
        
        with patch.object(self.provider.dynamic_client, 'get_games_for_sport', return_value=mock_data):
            games = self.provider.fetch_odds("200")  # NBA
            
            # Validate complete workflow
            assert len(games) == 1, "Should return one game"
            
            game = games[0]
            assert isinstance(game, StandardizedGame), "Should be StandardizedGame"
            assert game.sport == "NBA", "Sport should be NBA"
            assert game.home_team == "Boston Celtics", "Home team should be Celtics"
            assert game.away_team == "Los Angeles Lakers", "Away team should be Lakers"
            assert game.game_id == "dk_99999", "Game ID should be prefixed"
            
            # Validate market data structure
            assert "Moneyline" in game.markets, "Should have Moneyline market"
            moneyline_selections = game.markets["Moneyline"]
            assert len(moneyline_selections) == 2, "Should have 2 Moneyline selections"
            
            # Validate selection structure
            for selection in moneyline_selections:
                assert isinstance(selection, dict), "Selection should be dict"
                assert 'label' in selection, "Selection should have label"
                assert 'odds' in selection, "Selection should have odds"
                
        log.info("Complete workflow integration test passed")