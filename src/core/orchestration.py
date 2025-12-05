# src/core/orchestration.py
"""Orchestration logic to run all providers in parallel and store results.

For simplicity this uses Python's threading to invoke each provider's fetch_odds method.
"""

import threading
from typing import List
from .database import init_db, get_connection
from .logger import get_logger
from ..providers import get_all_providers

log = get_logger(__name__)

# Thread lock for shared data
_results_lock = threading.Lock()

def run_provider(provider, sport_id: str, results: List):
    """Run a single provider and append results to shared list (thread-safe)."""
    try:
        odds = provider.fetch_odds(sport_id)
        with _results_lock:
            results.extend(odds)
    except Exception as e:
        log.error(
            f"Provider {provider.__class__.__name__} failed",
            exc_info=True,
            extra={"provider": provider.__class__.__name__, "sport": sport_id}
        )

def orchestrate(sport_id: str = "NFL"):
    """Initialize DB, run each provider, and persist results."""
    init_db()
    providers = get_all_providers()
    threads = []
    results = []
    
    log.info(f"Starting orchestration for {sport_id} with {len(providers)} providers")
    
    for prov in providers:
        t = threading.Thread(target=run_provider, args=(prov, sport_id, results))
        t.start()
        threads.append(t)
    
    for t in threads:
        t.join()
    
    log.info(f"Orchestration complete. Collected {len(results)} games")
    
    # Persist results
    with get_connection() as conn:
        cur = conn.cursor()
        games_inserted = 0
        odds_inserted = 0
        
        for game in results:
            # Insert game
            cur.execute(
                """INSERT OR IGNORE INTO games (sport, game_id, home_team, away_team, start_time) 
                   VALUES (?, ?, ?, ?, ?)""",
                (game.sport, game.game_id, 
                 getattr(game, 'home_team', None), 
                 getattr(game, 'away_team', None), 
                 getattr(game, 'start_time', None))
            )
            if cur.rowcount > 0:
                games_inserted += 1
            
            # Get game's DB ID
            cur.execute(
                "SELECT id FROM games WHERE sport = ? AND game_id = ?",
                (game.sport, game.game_id)
            )
            game_db_id = cur.fetchone()[0]
            
            # Insert odds (if game has odds data)
            if hasattr(game, 'odds') and game.odds:
                for odd in game.odds:
                    cur.execute(
                        """INSERT INTO odds (game_id, provider, market, odds) 
                           VALUES (?, ?, ?, ?)""",
                        (game_db_id, 
                         getattr(odd, 'provider', 'unknown'),
                         getattr(odd, 'market', 'unknown'),
                         getattr(odd, 'odds', 0.0))
                    )
                    odds_inserted += 1
        
        conn.commit()
        log.info(f"Persisted {games_inserted} games and {odds_inserted} odds to database")
