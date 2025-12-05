# src/api/routes.py
"""API route definitions for the betting‑markets service.

Provides endpoints:
- GET /api/v1/games – list games
- GET /api/v1/arbitrage – placeholder for arbitrage calculations
- GET /api/v1/status – LLM‑generated health summary (placeholder implementation)
"""

from flask import Blueprint, jsonify
from ..core.database import get_connection

# Import the LLM monitor for the status endpoint
from ..llm.monitor import summarise_status

api_bp = Blueprint('api', __name__, url_prefix='/api/v1')

@api_bp.route('/games')
def list_games():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT sport, game_id, home_team, away_team, start_time FROM games")
    rows = cur.fetchall()
    games = [dict(row) for row in rows]
    return jsonify(games)

@api_bp.route('/arbitrage')
def arbitrage():
    # Placeholder – real logic would compare odds across providers
    return jsonify({"message": "Arbitrage endpoint not yet implemented"})

@api_bp.route('/status')
def status():
    """Return an LLM‑generated health summary (currently a stub)."""
    report = summarise_status()
    # Return plain text (markdown) – callers can render as they wish
    return report, 200, {"Content-Type": "text/plain; charset=utf-8"}
