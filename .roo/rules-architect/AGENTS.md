# Project Architecture Rules (Non-Obvious Only)

- Provider classes MUST inherit `BaseProvider` - interface required for auto-discovery via importlib
- Scheduler runs parallel threads per provider/sport - requires explicit locking for shared data
- Database schema has strict relationships: games.id → odds.game_id (foreign key constraints)
- Environment variables override defaults: `DB_PATH` for database location, `LOG_DIR` for log files
- Config structure is hierarchical: sport → provider → interval seconds (not flat key-value)
- SQLite used for simplicity but requires context managers for connection management
- Provider exceptions must be caught to prevent scheduler crashes - graceful failure handling
- Auto-discovery system scans `src.providers.*` subdirectories for provider implementations