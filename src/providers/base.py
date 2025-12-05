# src/providers/base.py
"""Abstract Base Class for all providers.

Each concrete provider must implement ``get_sports_mapping`` and ``fetch_odds``.
"""

from abc import ABC, abstractmethod
from typing import Dict, List
from ..core.schemas import StandardizedGame

class BaseProvider(ABC):
    @abstractmethod
    def get_sports_mapping(self) -> Dict[str, str]:
        """Return a mapping from provider‑specific sport IDs to standard sport names."""
        raise NotImplementedError

    @abstractmethod
    def fetch_odds(self, sport_id: str) -> List[StandardizedGame]:
        """Fetch odds for the given sport and return a list of ``StandardizedGame`` objects."""
        raise NotImplementedError
