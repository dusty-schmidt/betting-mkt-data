# Project Debug Rules (Non-Obvious Only)

- Logs written to `logs/app.log` with 5MB rotation - check this file first for errors (not console output)
- Database file is `betting_markets.db` - use `sqlite3 betting_markets.db ".tables"` to inspect schema
- Server runs on port 5000 - test API endpoints with `curl http://localhost:5000/games`
- Scheduler runs parallel threads - thread safety issues cause silent data corruption
- Provider exceptions are caught to prevent scheduler crashes - check logs for hidden failures
- Database connections fail silently without context managers - always use `with get_connection():`
- Environment variables `DB_PATH`/`LOG_DIR` override defaults - check Docker/production configs