"""Centralized logging configuration for the backend modules.

Usage notes:
- Importing this module calls `configure_logging()` as a side-effect to ensure a
    consistent default logging configuration is present for modules that execute
    at import time. The main application (or tests) may reconfigure logging
    later (e.g. to attach handlers, send logs to external services, or change
    formatting).

Environment variables:
- `JANDA_LOG_LEVEL` - optional, default `INFO`. (e.g. `DEBUG`, `INFO`)
- `JANDA_LOG_FORMAT` - optional, default `%(asctime)s %(levelname)s [%(name)s] %(message)s`.

This module intentionally uses `logging.basicConfig` only when no root
handlers are present to avoid duplicate log lines in environments that
already configure logging (e.g. test runners or web frameworks).
"""
import logging
import os


def configure_logging():
    # Allow environment to override default level, default to INFO
    level_name = os.getenv("JANDA_LOG_LEVEL", "INFO").upper()
    level = getattr(logging, level_name, logging.INFO)

    # Basic format including module and level
    fmt = os.getenv(
        "JANDA_LOG_FORMAT",
        "%(asctime)s %(levelname)s [%(name)s] %(message)s",
    )

    # Only configure basicConfig once to avoid duplicate handlers
    root = logging.getLogger()
    if not root.handlers:
        logging.basicConfig(level=level, format=fmt)


# Configure on import to ensure modules get consistent logging by default.
configure_logging()
