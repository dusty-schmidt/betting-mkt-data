# Developer Quickstart & Critical Rules

## ⚡ Golden Rules
1. **Use `uv`** for all dependency management. Never use `pip` directly.
2. **Providers are Plugins**. They must inherit `BaseProvider` and never import from other providers.
3. **Set-and-Forget**. The app must be resilient. Handle exceptions in providers; never crash the main loop.
4. **Persistence**. Always use `DB_PATH` and `LOG_DIR` env vars. Docker containers are ephemeral.

## 🚀 Quick Commands
| Action | Command |
|--------|---------|
| **Setup** | `uv sync` |
| **Test** | `uv run pytest` |
| **Run (Local)** | `uv run python run.py` |
| **Docker Build** | `docker build -t betting-markets .` |
| **Docker Run** | `docker run -d -p 5000:5000 -v $(pwd)/data:/app/data -v $(pwd)/logs:/app/logs betting-markets` |

## 📂 Critical Locations
- **Config**: `config.yaml` (Fetch intervals)
- **Logs**: `logs/app.log` (Rotated, 5MB limit)
- **Database**: `betting_markets.db` (SQLite)
- **New Providers**: `src/providers/<name>/`

## 🏗️ Architecture in a Nutshell
- **Scheduler** (`src/core/scheduler.py`) triggers **Orchestrator** (`src/core/orchestration.py`).
- **Orchestrator** calls **Providers** (`src/providers/`) and saves to **DB**.
- **API** (`src/api/`) reads from **DB** (never calls providers directly).
