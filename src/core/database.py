"""Database setup for betting‑markets.

Uses SQLite via the built‑in ``sqlite3`` module for simplicity.
The ``get_connection`` function returns a connection that other modules can use.
"""
import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).parent.parent / "betting_markets.db"

def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Create tables if they don't exist."""
    with get_connection() as conn:
        cur = conn.cursor()
        # Simple table for standardized games/odds
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS games (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                sport TEXT NOT NULL,
                game_id TEXT NOT NULL,
                home_team TEXT,
                away_team TEXT,
                start_time TEXT,
                UNIQUE(sport, game_id)
            )
            """
        )
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS odds (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                game_id INTEGER NOT NULL,
                provider TEXT NOT NULL,
                market TEXT NOT NULL,
                odds REAL NOT NULL,
                FOREIGN KEY(game_id) REFERENCES games(id)
            )
            """
        )
        conn.commit()
