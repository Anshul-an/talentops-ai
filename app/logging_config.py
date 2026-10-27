import json
import logging
import os
import sys
from datetime import datetime, timezone
from typing import Any, Optional

LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()


class StructuredFormatter(logging.Formatter):
    """Formats log records with timestamp, level, logger name, and optional structured metadata."""

    def format(self, record: logging.LogRecord) -> str:
        timestamp = datetime.now(timezone.utc).isoformat()
        extra_data = getattr(record, "extra_data", None)
        base = f"{timestamp} [{record.levelname}] [{record.name}] {record.getMessage()}"
        if extra_data:
            try:
                base += f" | {json.dumps(extra_data, default=str)}"
            except Exception:
                base += f" | {extra_data}"
        return base


def setup_logging(level: Optional[str] = None) -> None:
    lvl = getattr(logging, (level or LOG_LEVEL).upper(), logging.INFO)
    root = logging.getLogger("talentops")
    root.setLevel(lvl)
    if not root.handlers:
        handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(StructuredFormatter())
        root.addHandler(handler)


def get_logger(name: str) -> logging.Logger:
    setup_logging()
    return logging.getLogger(f"talentops.{name}")
