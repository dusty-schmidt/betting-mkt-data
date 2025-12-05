# src/core/headers.py
"""Utility for managing request headers.

Provides a simple rotating header pool to avoid hitting rate limits or detection.
The pool can be populated via environment variables or a config file.
"""

import itertools
import os
from typing import Dict, List

# Example: load a list of API keys / user‑agents from env var `HEADER_POOL`
# Expected format: "key1|key2|key3" (pipe‑separated)
_raw = os.getenv("HEADER_POOL", "")
_header_pool: List[Dict[str, str]] = []
for token in filter(None, _raw.split("|")):
    # For illustration we treat each token as a Bearer token
    _header_pool.append({"Authorization": f"Bearer {token}"})

# Fallback to a default header if no pool is defined
if not _header_pool:
    _header_pool.append({"User-Agent": "betting‑markets/0.1"})

# Cycle iterator – each call to ``next_header()`` returns the next header dict
_header_cycle = itertools.cycle(_header_pool)

def next_header() -> Dict[str, str]:
    """Return the next header dictionary from the rotating pool."""
    return next(_header_cycle)

# Helper for providers to merge custom headers with the rotating one
def merge_headers(custom: Dict[str, str] | None = None) -> Dict[str, str]:
    base = next_header().copy()
    if custom:
        base.update(custom)
    return base
