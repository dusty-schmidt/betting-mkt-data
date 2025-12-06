# Data Extraction

## Overview
The provider system fetches odds data from external sources and normalizes it into a common format.

## Architecture

```
┌──────────────┐
│  Scheduler   │ (reads config.yaml)
└──────┬───────┘
       │
       ▼
┌──────────────┐
│ Orchestrator │ (runs providers in parallel)
└──────┬───────┘
       │
       ├─────────────┬─────────────┬──────────────┐
       ▼             ▼             ▼              ▼
┌─────────────┐ ┌──────────┐ ┌──────────┐  ┌──────────┐
│ DraftKings  │ │ FanDuel  │ │  Bovada  │  │  Custom  │
└─────────────┘ └──────────┘ └──────────┘  └──────────┘
       │             │             │              │
       └─────────────┴─────────────┴──────────────┘
                     │
                     ▼
              ┌─────────────┐
              │  Database   │
              └─────────────┘
```

## Provider Contract

All providers must implement `BaseProvider`:

```python
from abc import ABC, abstractmethod
from src.core.schemas import StandardizedGame

class BaseProvider(ABC):
    @abstractmethod
    def get_sports_mapping(self) -> dict:
        """Map provider sport IDs to standard names."""
        pass



    @abstractmethod
    def fetch_odds(self, sport_id: str) -> list[StandardizedGame]:
        """Fetch and normalize odds data."""
        pass
```

## Provider Structure

```
src/providers/<provider_name>/
├── __init__.py      # Provider class
├── client.py        # HTTP client
└── parser.py        # Response normalization
```

