# README.md

# Betting Markets Aggregator

A **set‑and‑forget** Dockerized service that periodically fetches betting odds from multiple providers, normalises them into a common schema, stores them in SQLite, and exposes a simple Flask API for downstream applications.

## Features (core)
- **Modular provider architecture** – each bookie is a plug‑in under `src/providers/`.
- **Configurable fetch intervals** – defined in `config.yaml` per sport/provider.
- **Detailed logging** – all actions are written to `logs/` with rotating file handlers.
- **Historical odds storage** – SQLite tables capture every scrape for later analysis.
- **Status endpoint** – quick view of recent scrapes, errors, and DB health.
- **Header rotation stub** – ready for future anti‑bot measures.
- **Extensible LLM layer (stub)** – placeholder for intelligent monitoring/fallback.

## Quick start
```bash
# Build Docker image
docker build -t betting‑markets ./project_root

# Run container (will read config.yaml for intervals)
docker run -d -p 5000:5000 betting‑markets
```

The API will be reachable at `http://localhost:5000/api/v1/`.

## Project layout
```
project_root/
├─ docker/               # Dockerfile
├─ src/                  # Application source
│   ├─ __init__.py
│   ├─ core/             # Core utilities (db, logger, headers, orchestration)
│   ├─ api/              # Flask API (routes, factory)
│   └─ providers/        # Provider plug‑ins
├─ docs/                 # Documentation (populate as needed)
├─ logs/                 # Runtime logs (auto‑created)
├─ config.yaml           # Interval configuration
├─ pyproject.toml        # Project metadata
└─ README.md             # This file
```

## Extending the app
- Add new providers under `src/providers/` following the `BaseProvider` contract.
- Update `config.yaml` with custom intervals.
- Implement header rotation in `src/core/headers.py`.
- Flesh out the LLM assistant in `src/llm/` for smarter monitoring.

---
*Built with love by the betting‑markets team.*
