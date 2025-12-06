# src/core/config.py
"""Configuration management module."""

import os
import yaml
from typing import Dict, Any, Optional
from ..core.logger import get_logger

log = get_logger(__name__)

class Config:
    """Application configuration loaded from config.yaml."""
    
    _instance = None
    _config_data = {}

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(Config, cls).__new__(cls)
            cls._instance._load_config()
        return cls._instance

    def _load_config(self, config_path: str = "config.yaml"):
        """Load configuration from YAML file."""
        try:
            # Look for config in current directory or parent directories
            if not os.path.exists(config_path):
                # Try finding it relative to project root if running from inside src
                potential_paths = [
                    config_path,
                    os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), config_path),
                    os.path.join(os.getcwd(), config_path)
                ]
                for path in potential_paths:
                    if os.path.exists(path):
                        config_path = path
                        break
            
            with open(config_path, 'r') as f:
                self._config_data = yaml.safe_load(f) or {}
            log.info(f"Loaded configuration from {config_path}")
        except Exception as e:
            log.error(f"Failed to load configuration: {e}")
            self._config_data = {}

    def get(self, key: str, default: Any = None) -> Any:
        """Get a top-level configuration value."""
        return self._config_data.get(key, default)

    def get_provider_config(self, provider_name: str) -> Dict[str, Any]:
        """Get configuration for a specific provider."""
        return self._config_data.get('providers', {}).get(provider_name, {})

    def get_sport_config(self, provider_name: str, sport_name: str) -> Optional[Dict[str, Any]]:
        """Get specific sport configuration for a provider."""
        provider_config = self.get_provider_config(provider_name)
        return provider_config.get('sports', {}).get(sport_name)

def load_config() -> Config:
    """Factory function to get the Config singleton."""
    return Config()
