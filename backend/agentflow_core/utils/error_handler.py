"""
AgentFlow Core - Error Handler

Defines custom exceptions and error handling utilities for the application.
All exceptions inherit from AgentFlowError for consistent error handling.
"""

from typing import Any


class AgentFlowError(Exception):
    """
    Base exception for all AgentFlow errors.
    
    All custom exceptions should inherit from this class.
    Provides consistent error structure with error codes and context.
    """
    
    def __init__(
        self,
        message: str,
        error_code: str = "AGENTFLOW_ERROR",
        context: dict[str, Any] | None = None
    ) -> None:
        """
        Initialize the error.
        
        Args:
            message: Human-readable error message
            error_code: Machine-readable error code
            context: Additional context for debugging
        """
        super().__init__(message)
        self.message = message
        self.error_code = error_code
        self.context = context or {}
    
    def to_dict(self) -> dict[str, Any]:
        """Convert error to dictionary for API responses."""
        return {
            "error": self.error_code,
            "message": self.message,
            "context": self.context,
        }


class ValidationError(AgentFlowError):
    """
    Raised when workflow or data validation fails.
    
    Contains details about what failed validation.
    """
    
    def __init__(
        self,
        message: str,
        field: str | None = None,
        errors: list[dict[str, Any]] | None = None
    ) -> None:
        super().__init__(
            message=message,
            error_code="VALIDATION_ERROR",
            context={
                "field": field,
                "errors": errors or [],
            }
        )
        self.field = field
        self.errors = errors or []


class WorkflowExecutionError(AgentFlowError):
    """
    Raised when workflow execution fails.
    
    Contains the workflow ID and node where failure occurred.
    """
    
    def __init__(
        self,
        message: str,
        workflow_id: str | None = None,
        node_id: str | None = None,
        partial_state: dict[str, Any] | None = None
    ) -> None:
        super().__init__(
            message=message,
            error_code="WORKFLOW_EXECUTION_ERROR",
            context={
                "workflow_id": workflow_id,
                "node_id": node_id,
                "partial_state": partial_state,
            }
        )
        self.workflow_id = workflow_id
        self.node_id = node_id
        self.partial_state = partial_state


class NodeExecutionError(AgentFlowError):
    """
    Raised when a specific node fails to execute.
    
    Contains node-specific error details.
    """
    
    def __init__(
        self,
        message: str,
        node_id: str,
        node_type: str,
        original_error: Exception | None = None
    ) -> None:
        super().__init__(
            message=message,
            error_code="NODE_EXECUTION_ERROR",
            context={
                "node_id": node_id,
                "node_type": node_type,
                "original_error": str(original_error) if original_error else None,
            }
        )
        self.node_id = node_id
        self.node_type = node_type
        self.original_error = original_error


class SourceNotFoundError(AgentFlowError):
    """
    Raised when a referenced source is not found in the registry.
    """
    
    def __init__(self, source_id: str) -> None:
        super().__init__(
            message=f"Source '{source_id}' not found in registry",
            error_code="SOURCE_NOT_FOUND",
            context={"source_id": source_id}
        )
        self.source_id = source_id


class SourceConnectionError(AgentFlowError):
    """
    Raised when a source connection fails (e.g., API, database).
    """
    
    def __init__(
        self,
        message: str,
        source_id: str,
        source_kind: str
    ) -> None:
        super().__init__(
            message=message,
            error_code="SOURCE_CONNECTION_ERROR",
            context={
                "source_id": source_id,
                "source_kind": source_kind,
            }
        )
        self.source_id = source_id
        self.source_kind = source_kind


class RateLimitExceededError(AgentFlowError):
    """
    Raised when rate limit is exceeded for a queue or source.
    """
    
    def __init__(
        self,
        message: str,
        queue_id: str | None = None,
        retry_after_seconds: float | None = None
    ) -> None:
        super().__init__(
            message=message,
            error_code="RATE_LIMIT_EXCEEDED",
            context={
                "queue_id": queue_id,
                "retry_after_seconds": retry_after_seconds,
            }
        )
        self.queue_id = queue_id
        self.retry_after_seconds = retry_after_seconds


class TimeoutError(AgentFlowError):
    """
    Raised when workflow or node execution times out.
    """
    
    def __init__(
        self,
        message: str,
        timeout_seconds: float,
        node_id: str | None = None
    ) -> None:
        super().__init__(
            message=message,
            error_code="EXECUTION_TIMEOUT",
            context={
                "timeout_seconds": timeout_seconds,
                "node_id": node_id,
            }
        )
        self.timeout_seconds = timeout_seconds
        self.node_id = node_id


def format_exception_for_api(error: Exception) -> dict[str, Any]:
    """
    Format any exception for API response.
    
    Args:
        error: The exception to format
        
    Returns:
        Dictionary suitable for API error response
    """
    if isinstance(error, AgentFlowError):
        return error.to_dict()
    
    # Generic exception handling
    return {
        "error": "INTERNAL_ERROR",
        "message": str(error),
        "context": {
            "error_type": type(error).__name__,
        }
    }
