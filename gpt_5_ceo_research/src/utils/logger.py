"""
Structured logging configuration using structlog.

This module provides a setup_logger function that configures structlog with:
- JSON output for production
- Pretty console output for development
- Timestamp on all log entries
- Respects LOG_LEVEL from settings
- Simple KISS principle implementation
"""

import logging
import sys
from typing import Any, Dict, Optional

import structlog
from structlog.types import Processor

try:
    from ..config.settings import get_settings
except ImportError:
    # Fallback for when module is imported from different context
    try:
        from src.config.settings import get_settings
    except ImportError:
        from config.settings import get_settings


def _is_development() -> bool:
    """
    Detect if we're running in development mode.

    Returns:
        True if development mode detected, False for production
    """
    # Simple heuristics for development detection
    return (
        # Check if we're in a development environment
        sys.argv[0].endswith(('python', 'python.exe')) or
        # Check if running from common dev directories
        any(dev_indicator in sys.argv[0].lower() for dev_indicator in ['venv', 'test', 'dev', 'debug']) or
        # Check if LOG_LEVEL is DEBUG (common in dev)
        get_settings().log_level == 'DEBUG'
    )


def _add_timestamp(logger: Any, method_name: str, event_dict: Dict[str, Any]) -> Dict[str, Any]:
    """Add ISO timestamp to log entries."""
    import datetime
    event_dict['timestamp'] = datetime.datetime.utcnow().isoformat() + 'Z'
    return event_dict


def setup_logger() -> structlog.stdlib.BoundLogger:
    """
    Configure and return a structlog logger instance.

    Configures structlog with:
    - Development: Pretty console output with colors
    - Production: JSON output for structured logging
    - Timestamp added to all entries
    - Respects LOG_LEVEL from settings

    Returns:
        Configured structlog logger instance
    """
    settings = get_settings()

    # Convert string log level to logging constant
    log_level = getattr(logging, settings.log_level.upper())

    # Configure standard library logging with UTF-8 encoding
    import io

    # Wrap stdout with UTF-8 encoding to handle Unicode characters on Windows
    utf8_stdout = io.TextIOWrapper(
        sys.stdout.buffer if hasattr(sys.stdout, 'buffer') else sys.stdout,
        encoding='utf-8',
        errors='replace',  # Replace unsupported characters instead of crashing
        line_buffering=True
    )

    logging.basicConfig(
        format="%(message)s",
        stream=utf8_stdout,
        level=log_level,
    )

    # Determine output format based on environment
    is_dev = _is_development()

    # Common processors for both environments
    processors: list[Processor] = [
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
        _add_timestamp,
    ]

    # Add environment-specific processor
    if is_dev:
        # Development: Pretty console output
        processors.append(
            structlog.dev.ConsoleRenderer(colors=True)
        )
    else:
        # Production: JSON output
        processors.append(
            structlog.processors.JSONRenderer()
        )

    # Configure structlog
    structlog.configure(
        processors=processors,
        wrapper_class=structlog.stdlib.BoundLogger,
        logger_factory=structlog.stdlib.LoggerFactory(),
        cache_logger_on_first_use=True,
    )

    # Return configured logger
    return structlog.get_logger()


def get_logger(name: Optional[str] = None) -> structlog.stdlib.BoundLogger:
    """
    Get a logger instance for a specific module.

    Args:
        name: Logger name, defaults to the calling module name

    Returns:
        Configured structlog logger instance with the specified name
    """
    if name is None:
        # Get the calling module name
        import inspect
        frame = inspect.currentframe()
        if frame and frame.f_back:
            name = frame.f_back.f_globals.get('__name__', 'unknown')

    return structlog.get_logger(name)


# Initialize logger on module import
_default_logger: Optional[structlog.stdlib.BoundLogger] = None


def _get_default_logger() -> structlog.stdlib.BoundLogger:
    """Get or create the default logger instance."""
    global _default_logger
    if _default_logger is None:
        _default_logger = setup_logger()
    return _default_logger


# Convenience functions for direct usage
def debug(msg: str, **kwargs: Any) -> None:
    """Log debug message."""
    _get_default_logger().debug(msg, **kwargs)


def info(msg: str, **kwargs: Any) -> None:
    """Log info message."""
    _get_default_logger().info(msg, **kwargs)


def warning(msg: str, **kwargs: Any) -> None:
    """Log warning message."""
    _get_default_logger().warning(msg, **kwargs)


def error(msg: str, **kwargs: Any) -> None:
    """Log error message."""
    _get_default_logger().error(msg, **kwargs)


def critical(msg: str, **kwargs: Any) -> None:
    """Log critical message."""
    _get_default_logger().critical(msg, **kwargs)