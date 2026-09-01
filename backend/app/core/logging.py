"""Structured logging and observability configuration for ReviewAI."""

import contextvars
import json
import logging
import sys
from datetime import datetime, timezone
from typing import Any, Dict, Optional

# Context variables for distributed tracing and request correlation
request_id_ctx: contextvars.ContextVar[Optional[str]] = contextvars.ContextVar("request_id", default=None)
analysis_id_ctx: contextvars.ContextVar[Optional[str]] = contextvars.ContextVar("analysis_id", default=None)


class JSONFormatter(logging.Formatter):
    """Structured JSON log formatter for production observability."""

    def format(self, record: logging.LogRecord) -> str:
        log_entry: Dict[str, Any] = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "line": record.lineno,
        }

        # Include tracing IDs if present in context
        req_id = request_id_ctx.get()
        if req_id:
            log_entry["request_id"] = req_id

        ana_id = analysis_id_ctx.get()
        if ana_id:
            log_entry["analysis_id"] = ana_id

        # Attach exception info if logged
        if record.exc_info:
            log_entry["exception"] = self.formatException(record.exc_info)

        return json.dumps(log_entry)


class StandardConsoleFormatter(logging.Formatter):
    """Clean developer-friendly console log formatter."""

    COLOR_MAP = {
        logging.DEBUG: "\033[36m",    # Cyan
        logging.INFO: "\033[32m",     # Green
        logging.WARNING: "\033[33m",  # Yellow
        logging.ERROR: "\033[31m",    # Red
        logging.CRITICAL: "\033[35m", # Magenta
    }
    RESET = "\033[0m"

    def format(self, record: logging.LogRecord) -> str:
        color = self.COLOR_MAP.get(record.levelno, self.RESET)
        req_id = request_id_ctx.get()
        prefix = f"[{req_id[:8]}] " if req_id else ""
        timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
        message = record.getMessage()

        # Sanitize sensitive patterns if needed
        formatted = f"{timestamp} | {color}{record.levelname:<8}{self.RESET} | {record.name} | {prefix}{message}"
        if record.exc_info:
            formatted += f"\n{self.formatException(record.exc_info)}"
        return formatted


def setup_logging(level: str = "INFO", json_format: bool = False) -> logging.Logger:
    """Configure root and application loggers."""
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, level.upper(), logging.INFO))

    # Clear existing handlers
    root_logger.handlers.clear()

    handler = logging.StreamHandler(sys.stdout)
    if json_format:
        handler.setFormatter(JSONFormatter())
    else:
        handler.setFormatter(StandardConsoleFormatter())

    root_logger.addHandler(handler)
    return logging.getLogger("reviewai")


logger = logging.getLogger("reviewai")
