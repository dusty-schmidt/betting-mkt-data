# tests/test_draftkings_client_config.py
import sys
import os
import unittest
from unittest.mock import MagicMock, patch

# Add src to pythonpath
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.providers.draftkings.client import DraftKingsClient, DraftKingsDynamicClient
from src.core.config import load_config

class TestDraftKingsClientConfig(unittest.TestCase):
    def setUp(self):
        self.config = load_config()

    def test_client_init(self):
        """Test that client initializes with config values."""
        client = DraftKingsClient()
        self.assertIsNotNone(client.config)
        self.assertIsNotNone(client.provider_config)
        self.assertIn("User-Agent", client.headers)
        
        # Check specific header value from config
        expected_ua = self.config.get_provider_config("DraftKings")["headers"]["User-Agent"]
        self.assertEqual(client.headers["User-Agent"], expected_ua)

    def test_dynamic_client_init(self):
        """Test that dynamic client initializes with config values and resolves templates."""
        client = DraftKingsDynamicClient()
        
        base_url = "https://sportsbook-nash.draftkings.com"
        expected_manifest = f"{base_url}/sites/US-OH-SB/api/sportslayout/v1/manifest?format=json"
        
        self.assertEqual(client.base_url, base_url)
        self.assertEqual(client.manifest_url, expected_manifest)
        self.assertIn("template_url_base", self.config.get_provider_config("DraftKings"))

    @patch('src.providers.draftkings.client.requests.get')
    def test_get_odds_config_lookup(self, mock_get):
        """Test that get_odds correctly looks up league ID from config."""
        client = DraftKingsClient()
        
        # Mock response
        mock_response = MagicMock()
        mock_response.json.return_value = {"events": []}
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response

        # Call with Sport ID "3" (NFL)
        client.get_odds("3")
        
        # Verify URL constructed with correct League ID 88808
        args, kwargs = mock_get.call_args
        url = args[0]
        self.assertIn("/leagues/88808", url)

if __name__ == '__main__':
    unittest.main()
