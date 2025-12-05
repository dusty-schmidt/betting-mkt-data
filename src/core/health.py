"""System health check utilities.

Provides functions to verify system components are properly initialized.
"""
from pathlib import Path
from src.core.logger import get_logger
from src.core.database import DB_PATH, get_connection

log = get_logger(__name__)


def check_system() -> dict:
    """Verify database file exists and log the status.
    
    Returns:
        dict: Status information with keys:
            - database_exists (bool): Whether the database file exists
            - database_path (str): Path to the database file
            - database_accessible (bool): Whether the database is accessible
            - status (str): Overall status message
    """
    result = {
        "database_exists": False,
        "database_path": str(DB_PATH),
        "database_accessible": False,
        "status": "unknown"
    }
    
    # Check if database file exists
    db_file = Path(DB_PATH)
    result["database_exists"] = db_file.exists()
    
    if not result["database_exists"]:
        log.warning(f"Database file does not exist at {DB_PATH}")
        result["status"] = "database_missing"
        return result
    
    # Try to connect to database
    try:
        with get_connection() as conn:
            cur = conn.cursor()
            # Verify we can query the database
            cur.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = [row[0] for row in cur.fetchall()]
            
            result["database_accessible"] = True
            result["tables"] = tables
            result["status"] = "ok"
            
            log.info(f"System health check passed - Database accessible at {DB_PATH} with {len(tables)} tables")
            
    except Exception as e:
        log.error(f"Database connection failed: {e}", exc_info=True)
        result["status"] = "database_error"
        result["error"] = str(e)
    
    return result