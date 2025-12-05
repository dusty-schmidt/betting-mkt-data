# Developer Guide

## Setup
```bash
uv sync && uv run pytest && uv run python run.py
```

## Golden Rules
1. Use `uv` for all package management
2. Use `logger`, never `print()` - import from `src.core.logger`
3. Use context managers for DB connections - `with get_connection() as conn:`
4. Use locks for shared data in threads - `threading.Lock()`
5. Providers inherit `BaseProvider` (auto-discovered)
6. Extend `BaseDataModel` for new data types
7. Use `DB_PATH` and `LOG_DIR` env vars
8. Never crash the scheduler - handle all exceptions

## Known Issues (Top 5)

⚠️ **Read before coding to avoid these mistakes:**

1. **Thread Safety** - `orchestration.py` uses shared list without locks (#3)
2. **Error Handling** - Using `print()` instead of logger (#1)
3. **DB Connections** - Not using context managers, causing leaks (#2)
4. **Odds Not Saved** - Only games are persisted, odds table empty (#7)
5. **Provider Scheduling** - All providers run on every interval (#5)

See `dev-docs/CODE-QUALITY-REVIEW.md` for details.

## Architecture Quick Facts

- **Providers**: Auto-discovered via `importlib`, inherit `BaseProvider`
- **Scheduler**: One thread per provider/sport (but currently runs ALL providers)
- **Database**: SQLite at `DB_PATH`, use `get_connection()` context manager
- **API**: Read-only from DB, never calls providers directly
- **Orchestrator**: Runs providers in parallel using threads

## When You Need More

**Before adding code:**
- Check `dev-docs/TASKS.md` for current priorities
- Check `dev-docs/CODE-QUALITY-REVIEW.md` for known issues

**Specific tasks:**
- Adding provider? → `docs/DATA-EXTRACTION.md`
- Changing DB schema? → `docs/DATABASE.md`
- Adding API endpoint? → `docs/API.md`
- Modifying scheduler/orchestrator? → CODE-QUALITY-REVIEW #3, #5

## Work Logs

**Purpose**: ONE file per task to prevent redundant summaries.

**Format**: `dev-docs/work-logs/YYYY-MM-DD-task-name.md`

**Template**: `dev-docs/work-logs/TEMPLATE.md`

**Rules**:
- Create on task start
- Update same file if retrying/continuing
- Include verification steps

## Common Patterns

### Logging
```python
from src.core.logger import get_logger
log = get_logger(__name__)
log.error("Message", exc_info=True, extra={"context": "value"})
```

### Database
```python
from src.core.database import get_connection
with get_connection() as conn:
    cur = conn.cursor()
    cur.execute("SELECT ...", (param,))
    # Connection auto-closed
```

### Threading
```python
import threading
lock = threading.Lock()
with lock:
    shared_data.append(item)
```

## File Map

- `dev-docs/TASKS.md` - Roadmap & priorities
- `dev-docs/CODE-QUALITY-REVIEW.md` - Detailed issues
- `docs/` - DATABASE, DATA-EXTRACTION, API reference
- `config.yaml` - Fetch intervals
- `logs/app.log` - Runtime logs
