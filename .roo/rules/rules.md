# Developer Guide

## Project
Betting market data aggregator - fetches odds from providers, normalizes data, exposes via read-only API.

**Components**: Providers → Scheduler → Database → API  
**Entry Points**: API `http://localhost:5000`, Database `betting_markets.db`, Logs `logs/app.log`

## Setup & Workflow

### Prerequisites
- Python 3.11+, `uv` package manager, `dev-workflow.sh` (`chmod +x`)

### Development Cycle
```bash
./dev-workflow.sh start    # Pull changes, create work-log
# Work on changes
./dev-workflow.sh end      # Commit, push, update work-log
```

### Manual Setup
```bash
uv sync && uv run python run.py
# Environment: DB_PATH, LOG_DIR, API_PORT, LOG_LEVEL
```

## Golden Rules
1. Use `uv` for package management
2. Use `logger`, never `print()` - `src.core.logger`
3. Context managers for DB - `get_connection()`
4. Locks for shared data - `threading.Lock()`
5. Providers inherit `BaseProvider` (auto-discovered)
6. Extend `BaseDataModel` for new data
7. Use `DB_PATH`/`LOG_DIR` env vars
8. Never crash scheduler - handle all exceptions

## Known Issues
⚠️ **Read before coding**: Thread safety (#3), error handling (#1), DB connections (#2), odds persistence (#7), provider scheduling (#5)  
**Details**: `dev-docs/TASKS.md`

## Architecture
- **Providers**: Auto-discovered via `importlib`
- **Scheduler**: Thread per provider/sport (currently runs all)
- **Database**: SQLite with `get_connection()` context manager
- **API**: Read-only from DB
- **Orchestrator**: Parallel provider execution

## Need More Info?

### Task Guidance
- **Current priorities**: `dev-docs/TASKS.md`
- **Task workflow**: Use `./dev-workflow.sh start/end`

### Specific Tasks
- Add provider → `docs/PROVIDERS.md`
- Change DB schema → `docs/DATABASE.md`  
- Add API endpoint → `docs/API.md`
- Modify scheduler → Check `dev-docs/TASKS.md`

### Code Patterns

**Logging:**
```python
from src.core.logger import get_logger
log = get_logger(__name__)
log.error("Message", exc_info=True)
```

**Database:**
```python
from src.core.database import get_connection
with get_connection() as conn:
    cur = conn.cursor()
    cur.execute("SELECT ...", (param,))
```

**Threading:**
```python
import threading
lock = threading.Lock()
with lock:
    shared_data.append(item)
```

## Project Structure
```
src/
├── core/          # logger, db, models, orchestrator
├── providers/     # DraftKings, FanDuel (auto-discovered)
├── api/           # REST endpoints
└── llm/           # LLM integration
```

## Common Tasks
```bash
# Debug
tail -f logs/app.log
sqlite3 betting_markets.db ".tables"
curl http://localhost:5000/api/v1/games

# What NOT to do
❌ print() instead of logger
❌ DB without context managers
❌ Ignore scheduler exceptions
❌ Change schema without updating models
```

## References
- **Work logs**: `dev-docs/work-logs/` (auto-managed)
- **Git workflow**: `dev-docs/references/git-workflow.md`
- **Config**: `config.yaml` (provider intervals)
- **Run**: `python run.py`

---
*For detailed task lists, architecture diagrams, and specific implementation guides, see the referenced documentation files.*