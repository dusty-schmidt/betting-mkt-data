# src/core/orchestration.py
"""Orchestration logic to run all providers in parallel and store results.

For simplicity this uses Python's threading to invoke each provider's fetch_odds method.
"""

import threading
from typing import List
from .database import init_db, get_connection
from ..providers import get_all_providers

def run_provider(provider, sport_id: str, results: List):
    try:
        odds = provider.fetch_odds(sport_id)
        results.extend(odds)
    except Exception as e:
        print(f"Provider {provider.__class__.__name__} failed: {e}")

def orchestrate(sport_id: str = "NFL"):
    """Initialize DB, run each provider, and persist results.
    """
    init_db()
    providers = get_all_providers()
    threads = []
    results = []
    for prov in providers:
        t = threading.Thread(target=run_provider, args=(prov, sport_id, results))
        t.start()
        threads.append(t)
    for t in threads:
        t.join()
    # Persist results (placeholder)
    conn = get_connection()
    cur = conn.cursor()
    for game in results:
        # Assuming game is a StandardizedGame instance
        cur.execute(
            "INSERT OR IGNORE INTO games (sport, game_id, home_team, away_team, start_time) VALUES (?, ?, ?, ?, ?)",
            (game.sport, game.game_id, getattr(game, 'home_team', None), getattr(game, 'away_team', None), getattr(game, 'start_time', None))
    conn.commit()
    conn.close()
