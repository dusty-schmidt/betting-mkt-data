# Project Documentation Rules (Non-Obvious Only)

- Database filename discrepancy: code uses `betting_markets.db` but some docs mention `betting.db`
- Port discrepancy: server runs on 5000 but some docs mention 8000
- Custom workflow script `dev-workflow.sh` automates git + work-log management (not standard git)
- Providers auto-discovered via importlib - place new providers in `src.providers.*` subdirectories
- Config file `config.yaml` uses nested structure: `sport.provider: seconds` (not flat)
- Environment variables `DB_PATH`/`LOG_DIR` override hardcoded defaults for Docker/production
- Work logs auto-managed in `dev-docs/work-logs/` with timestamp naming convention
- Known issues documented in `dev-docs/TASKS.md` with specific issue numbers (#1-#8)