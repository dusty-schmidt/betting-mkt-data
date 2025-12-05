# src/providers/__init__.py
"""Provider package initialization.

This module imports and registers all provider implementations so they can be discovered
by the orchestration logic via ``get_all_providers``.
"""

from .base import BaseProvider

def get_all_providers() -> list[BaseProvider]:
    """Return a list of instantiated provider classes.

    In a real project you would dynamically discover provider modules. Here we
    manually import the concrete implementations.
    """
    providers = []
    try:
        from .draftkings import DraftKingsProvider
        providers.append(DraftKingsProvider())
    except Exception:
        pass
    try:
        from .fanduel import FanDuelProvider
        providers.append(FanDuelProvider())
    except Exception:
        pass
    # Add other providers here
    return providers
