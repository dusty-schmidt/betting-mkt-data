# tests/test_api.py
"""Basic health‑check tests for the Betting Markets API.

These tests verify that the three implemented endpoints return a successful
HTTP status code and that the response payload matches the expected shape.
The fixtures from ``tests/conftest.py`` provide a Flask ``client`` that can
make requests without running a live server.
"""

import json

def test_games_endpoint(client):
    """GET /api/v1/games should return 200 and a JSON list (may be empty)."""
    response = client.get("/api/v1/games")
    assert response.status_code == 200
    # Ensure the response is JSON and decodes to a list
    data = json.loads(response.data)
    assert isinstance(data, list)

def test_arbitrage_endpoint(client):
    """GET /api/v1/arbitrage returns the placeholder message."""
    response = client.get("/api/v1/arbitrage")
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data.get("message") == "Arbitrage endpoint not yet implemented"

def test_status_endpoint(client):
    """GET /api/v1/status returns the LLM stub text with a 200 status."""
    response = client.get("/api/v1/status")
    assert response.status_code == 200
    # The stub returns plain text, not JSON
    text = response.data.decode("utf-8")
    assert "LLM‑STUB" in text
    assert "Prompt length" in text
