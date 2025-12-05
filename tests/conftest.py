import pytest
import tempfile
import os
from pathlib import Path
from unittest.mock import patch
from src.api.factory import create_app
from src.core.database import init_db

@pytest.fixture(scope="session")
def app():
    """Create and configure a Flask app for the test session using a temp DB."""
    # Create a temporary file for the database
    db_fd, db_path = tempfile.mkstemp()
    os.close(db_fd)
    
    # Patch the DB_PATH in the database module
    with patch("src.core.database.DB_PATH", Path(db_path)):
        # Initialize the database schema
        init_db()
        
        app = create_app()
        app.config.update({"TESTING": True})
        
        yield app
        
    # Cleanup
    import gc
    gc.collect()
    try:
        os.unlink(db_path)
    except PermissionError:
        pass

@pytest.fixture(scope="function")
def client(app):
    """Flask test client for making HTTP requests in tests."""
    return app.test_client()
