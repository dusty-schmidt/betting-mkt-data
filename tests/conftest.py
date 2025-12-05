# conftest.py
"""Pytest fixtures for the Betting Markets project.

Provides a Flask app fixture that can be used by tests to make requests
against the API without running a live server.
"""

import pytest
from src.api.factory import create_app

@pytest.fixture(scope="session")
def app():
    """Create and configure a Flask app for the test session."""
    app = create_app()
    app.config.update({"TESTING": True})
    return app

@pytest.fixture(scope="function")
def client(app):
    """Flask test client for making HTTP requests in tests."""
    return app.test_client()
