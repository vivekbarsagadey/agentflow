"""
AgentFlow Core - Structured Logging Utility

Provides consistent, structured logging across the entire application.
Uses structlog for JSON-formatted logs suitable for production environments.
"""

import logging
import sys
from typing import Any

import structlog


def setup_logging(
    log_level: str = "INFO",
    json_format: bool = False,
    app_name: str = "agentflow-core"
) -> None:
    """
    Configure structured logging for the application.
    
    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        json_format: If True, output JSON formatted logs (for production)
        app_name: Application name to include in logs
    """
    # Configure standard logging
    logging.basicConfig(
        format="%(message)s",
        stream=sys.stdout,
        level=getattr(logging, log_level.upper(), logging.INFO),
    )

    # Configure structlog processors
    shared_processors: list[Any] = [
        structlog.stdlib.add_log_level,
        structlog.stdlib.add_logger_name,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.UnicodeDecoder(),
    ]

    if json_format:
        # JSON format for production
        processors = shared_processors + [
            structlog.processors.format_exc_info,
            structlog.processors.JSONRenderer(),
        ]
    else:
        # Human-readable format for development
        processors = shared_processors + [
            structlog.dev.ConsoleRenderer(colors=True),
        ]

    structlog.configure(
        processors=processors,
        wrapper_class=structlog.stdlib.BoundLogger,
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        cache_logger_on_first_use=True,
    )


def get_logger(name: str | None = None) -> structlog.stdlib.BoundLogger:
    """
    Get a structured logger instance.
    
    Args:
        name: Logger name (usually __name__ of the module)
        
    Returns:
        A bound logger instance with structured logging capabilities
        
    Example:
        >>> logger = get_logger(__name__)
        >>> logger.info("workflow_started", workflow_id="wf_123", node_count=5)
    """
    return structlog.get_logger(name)


# Create default logger for the package
logger = get_logger("agentflow_core")


# Convenience functions for common log operations
def log_workflow_event(
    event: str,
    workflow_id: str,
    **kwargs: Any
) -> None:
    """Log a workflow-related event with consistent structure."""
    logger.info(
        event,
        workflow_id=workflow_id,
        **kwargs
    )


def log_node_event(
    event: str,
    node_id: str,
    node_type: str,
    **kwargs: Any
) -> None:
    """Log a node-related event with consistent structure."""
    logger.info(
        event,
        node_id=node_id,
        node_type=node_type,
        **kwargs
    )


def log_error(
    event: str,
    error: Exception,
    **kwargs: Any
) -> None:
    """Log an error with exception details."""
    logger.error(
        event,
        error_type=type(error).__name__,
        error_message=str(error),
        **kwargs,
        exc_info=True
    )


def log_api_request(
    method: str,
    path: str,
    status_code: int,
    duration_ms: float,
    **kwargs: Any
) -> None:
    """Log an API request with standard fields."""
    logger.info(
        "api_request",
        method=method,
        path=path,
        status_code=status_code,
        duration_ms=round(duration_ms, 2),
        **kwargs
    )
