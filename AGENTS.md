# AGENTS.md

This file provides guidance to agents when working with code in this repository.

## Critical Project-Specific Rules

- **Database**: Use `betting_markets.db` (not `betting.db` as some docs state) - located via `DB_PATH` env var or `src/betting_markets.db`
- **Port**: Server runs on port 5000 (not 8000 mentioned in some docs)
- **Providers**: Auto-discovered via `importlib` from `src.providers.*` - place new providers in subdirectories there
- **Logging**: Mandatory `get_logger(__name__)` from `src.core.logger` - never use `print()` - writes to `logs/app.log` with 5MB rotation
- **Database**: Always use context managers with `get_connection()` - direct connections will cause issues
- **Threading**: Explicitly lock shared data with `threading.Lock()` - scheduler runs parallel threads
- **Scheduler**: Handle ALL exceptions to prevent crashes - wraps provider execution
- **Config**: Provider intervals in `config.yaml` use nested structure: `sport.provider: seconds`

## Development Workflow

**MANDATORY**: Use `./dev-workflow.sh start|end` instead of raw git commands - automates work logs in `dev-docs/work-logs/`

### Workflow Steps:
1. `./dev-workflow.sh start` - Pull latest changes, create timestamped work log in `dev-docs/work-logs/YYYY-MM-DD-task-name.md`
2. Make your changes
3. `./dev-workflow.sh end` - Commit with auto-generated message, push changes, mark work log as completed

### Documentation System:
- **Work logs**: `dev-docs/work-logs/` - auto-managed, one per session
- **Task priorities**: `dev-docs/TASKS.md` - check before starting work
- **Implementation guides**: `docs/` directory (API.md, DATABASE.md, DATA-EXTRACTION.md)
- **Git workflow reference**: `dev-docs/references/git-workflow.md`

## Key Commands

- **Single test**: `uv run pytest tests/test_*.py::TestClass::test_method -v`
- **Debug logs**: `tail -f logs/app.log`
- **Database inspect**: `sqlite3 betting_markets.db ".tables"`
- **API test**: `curl http://localhost:5000/games`