# src/llm/monitor.py
"""LLM‑based monitoring utilities.

Collects runtime information (logs, DB stats) and asks the LLM for a short
summary or remediation suggestion.
"""
import json
import sqlite3
from pathlib import Path
from typing import List

from ..core.logger import get_logger
from ..core.database import get_connection
from .client import LLMClient

log = get_logger(__name__)

client = LLMClient()   # uses the stub implementation

def _load_recent_logs(lines: int = 20) -> str:
    """Read the tail of the log file (fast, no external deps)."""
    log_file = Path(__file__).resolve().parents[3] / "logs" / "app.log"
    if not log_file.is_file():
        return ""
    with open(log_file, "r", encoding="utf-8") as f:
        return "".join(f.readlines()[-lines:])

def _db_stats() -> dict:
    """Return a tiny snapshot of the DB – row counts per table."""
    stats = {}
    try:
        with get_connection() as conn:
            cur = conn.cursor()
            for tbl in ("games", "odds"):
                try:
                    cur.execute(f"SELECT COUNT(*) FROM {tbl}")
                    stats[tbl] = cur.fetchone()[0]
                except Exception:
                    stats[tbl] = 0
    except Exception:
        pass
    return stats

def summarise_status() -> str:
    """Ask the LLM to produce a short health report."""
    prompt = (
        "You are a monitoring assistant for a betting‑odds aggregation service. "
        "Based on the following information, write a concise markdown status report (max 5 lines).\n\n"
        f"Log tail (most recent 20 lines):\n```\n{_load_recent_logs()}\n```\n"
        f"Database row counts: {json.dumps(_db_stats())}\n"
    )
    log.debug("Sending status prompt to LLM")
    return client.call(prompt)

def handle_failure(provider_name: str, error: Exception) -> str:
    """When a provider fails, ask the LLM for a remediation suggestion."""
    prompt = (
        f"The provider '{provider_name}' raised an exception:\n```\n{repr(error)}\n```\n"
        "Suggest a short next step (e.g., retry after X seconds, rotate headers, "
        "or skip until next scheduled run). Return only the suggestion."
    )
    log.debug("Sending failure prompt to LLM")
    return client.call(prompt)
