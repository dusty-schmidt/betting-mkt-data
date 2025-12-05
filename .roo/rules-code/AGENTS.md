# Project Coding Rules (Non-Obvious Only)

- Always use custom logger from `src.core.logger.get_logger(__name__)` - never `print()` or standard logging
- Database connections MUST use context managers: `with get_connection() as conn:` - direct calls cause connection issues
- Threading requires explicit locks for ANY shared data: `with threading.Lock():` - scheduler runs parallel threads
- Provider classes must inherit `BaseProvider` and implement `get_sports_mapping()` + `fetch_odds()` - auto-discovered via importlib
- Scheduler execution must handle ALL exceptions to prevent crashes - even provider failures should be caught
- New data models must extend `BaseDataModel` for consistency
- Environment variables `DB_PATH`/`LOG_DIR` override defaults - check for Docker/production usage
- Config structure in `config.yaml` is `sport.provider: seconds` - nested YAML structure required