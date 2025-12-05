# src/core/logger.py
"""Central logging configuration.

All modules should import ``logger = get_logger(__name__)`` and use ``logger.info``/``debug``/``error`` etc.
The logs are written to ``logs/app.log`` with a rotating file handler (5 MB per file, keep 5 backups).
"""

import logging
import os
from logging.handlers import RotatingFileHandler

LOG_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "logs"))
os.makedirs(LOG_DIR, exist_ok=True)

LOG_FILE = os.path.join(LOG_DIR, "app.log")

formatter = logging.Formatter(
    "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

handler = RotatingFileHandler(LOG_FILE, maxBytes=5 * 1024 * 1024, backupCount=5)
handler.setFormatter(formatter)

root_logger = logging.getLogger()
root_logger.setLevel(logging.INFO)
root_logger.addHandler(handler)

def get_logger(name: str) -> logging.Logger:
    """Return a child logger with the given name."""
    return logging.getLogger(name)
