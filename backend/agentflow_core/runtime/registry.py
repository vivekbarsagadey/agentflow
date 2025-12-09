"""
AgentFlow Core - Runtime Registry

Central registry for storing and retrieving sources at runtime.
Provides thread-safe access to source configurations.
"""

from threading import Lock
from typing import Any, Dict, List, Optional

from agentflow_core.utils.error_handler import SourceNotFoundError
from agentflow_core.utils.logger import get_logger

logger = get_logger(__name__)


# =============================================================================
# Global Registry Storage
# =============================================================================

_sources: Dict[str, Dict[str, Any]] = {}
_sources_lock = Lock()

_compiled_graphs: Dict[str, Any] = {}
_graphs_lock = Lock()

_active_executions: Dict[str, Dict[str, Any]] = {}
_executions_lock = Lock()


# =============================================================================
# Registry View Class
# =============================================================================


class RegistryView:
    """Read-only view of the registry for inspection."""
    
    @property
    def sources(self) -> Dict[str, Dict[str, Any]]:
        """Get a copy of all registered sources."""
        with _sources_lock:
            return dict(_sources)
    
    @property
    def source_count(self) -> int:
        """Get the number of registered sources."""
        with _sources_lock:
            return len(_sources)


def get_registry() -> RegistryView:
    """
    Get a read-only view of the registry.
    
    Returns:
        RegistryView instance for inspecting registry state
    """
    return RegistryView()


# =============================================================================
# Source Registry Functions
# =============================================================================


def register_source(source_id: str, source_config: Dict[str, Any]) -> None:
    """
    Register a source configuration.
    
    Args:
        source_id: Unique identifier for the source
        source_config: Source configuration dictionary
        
    Example:
        >>> register_source("gemini-llm", {
        ...     "kind": "llm",
        ...     "model": "gemini-1.5-flash",
        ...     "api_key_env": "GEMINI_API_KEY"
        ... })
    """
    with _sources_lock:
        _sources[source_id] = source_config
        logger.info("source_registered", source_id=source_id, kind=source_config.get("kind"))


def get_source(source_id: str) -> Dict[str, Any]:
    """
    Retrieve a source configuration.
    
    Args:
        source_id: The source ID to retrieve
        
    Returns:
        The source configuration dictionary
        
    Raises:
        SourceNotFoundError: If source is not registered
        
    Example:
        >>> config = get_source("gemini-llm")
        >>> print(config["model"])
        'gemini-1.5-flash'
    """
    with _sources_lock:
        if source_id not in _sources:
            logger.warning("source_not_found", source_id=source_id)
            raise SourceNotFoundError(source_id)
        return _sources[source_id].copy()  # Return copy for safety


def unregister_source(source_id: str) -> bool:
    """
    Unregister a source.
    
    Args:
        source_id: The source ID to unregister
        
    Returns:
        True if source was removed, False if not found
    """
    with _sources_lock:
        if source_id in _sources:
            del _sources[source_id]
            logger.info("source_unregistered", source_id=source_id)
            return True
        return False


def list_sources() -> List[Dict[str, Any]]:
    """
    List all registered sources.
    
    Returns:
        List of source configurations with IDs
    """
    with _sources_lock:
        return [
            {"id": source_id, **config}
            for source_id, config in _sources.items()
        ]


def has_source(source_id: str) -> bool:
    """
    Check if a source is registered.
    
    Args:
        source_id: The source ID to check
        
    Returns:
        True if source exists, False otherwise
    """
    with _sources_lock:
        return source_id in _sources


def clear_sources() -> None:
    """Clear all registered sources."""
    with _sources_lock:
        _sources.clear()
        logger.info("sources_cleared")


def register_sources_from_spec(sources: List[Dict[str, Any]]) -> None:
    """
    Register multiple sources from a workflow spec.
    
    Args:
        sources: List of source configurations from WorkflowSpec
    """
    for source in sources:
        source_id = source.get("id")
        if source_id:
            register_source(source_id, source)


# =============================================================================
# Compiled Graph Registry (Optional Caching)
# =============================================================================


def cache_compiled_graph(workflow_id: str, graph: Any) -> None:
    """
    Cache a compiled graph for reuse.
    
    Args:
        workflow_id: Unique workflow identifier
        graph: Compiled LangGraph instance
    """
    with _graphs_lock:
        _compiled_graphs[workflow_id] = graph
        logger.info("graph_cached", workflow_id=workflow_id)


def get_cached_graph(workflow_id: str) -> Optional[Any]:
    """
    Retrieve a cached compiled graph.
    
    Args:
        workflow_id: The workflow ID to retrieve
        
    Returns:
        Cached graph if exists, None otherwise
    """
    with _graphs_lock:
        return _compiled_graphs.get(workflow_id)


def invalidate_cached_graph(workflow_id: str) -> bool:
    """
    Invalidate a cached graph.
    
    Args:
        workflow_id: The workflow ID to invalidate
        
    Returns:
        True if graph was cached and removed, False otherwise
    """
    with _graphs_lock:
        if workflow_id in _compiled_graphs:
            del _compiled_graphs[workflow_id]
            logger.info("graph_cache_invalidated", workflow_id=workflow_id)
            return True
        return False


def clear_graph_cache() -> None:
    """Clear all cached graphs."""
    with _graphs_lock:
        _compiled_graphs.clear()
        logger.info("graph_cache_cleared")


# =============================================================================
# Active Executions Tracking
# =============================================================================


def register_execution(
    execution_id: str,
    workflow_id: str,
    metadata: Optional[Dict[str, Any]] = None
) -> None:
    """
    Register an active execution.
    
    Args:
        execution_id: Unique execution identifier
        workflow_id: The workflow being executed
        metadata: Optional execution metadata
    """
    import time
    
    with _executions_lock:
        _active_executions[execution_id] = {
            "workflow_id": workflow_id,
            "started_at": time.time(),
            "status": "running",
            "metadata": metadata or {},
        }
        logger.info(
            "execution_registered",
            execution_id=execution_id,
            workflow_id=workflow_id
        )


def complete_execution(
    execution_id: str,
    status: str = "completed",
    result: Optional[Dict[str, Any]] = None
) -> None:
    """
    Mark an execution as complete.
    
    Args:
        execution_id: The execution to complete
        status: Final status (completed, failed, timeout)
        result: Optional result data
    """
    import time
    
    with _executions_lock:
        if execution_id in _active_executions:
            _active_executions[execution_id]["status"] = status
            _active_executions[execution_id]["completed_at"] = time.time()
            _active_executions[execution_id]["result"] = result
            logger.info(
                "execution_completed",
                execution_id=execution_id,
                status=status
            )


def get_execution(execution_id: str) -> Optional[Dict[str, Any]]:
    """
    Get execution details.
    
    Args:
        execution_id: The execution ID to retrieve
        
    Returns:
        Execution details if found, None otherwise
    """
    with _executions_lock:
        return _active_executions.get(execution_id, {}).copy() if execution_id in _active_executions else None


def list_active_executions() -> List[Dict[str, Any]]:
    """
    List all active (running) executions.
    
    Returns:
        List of active execution details
    """
    with _executions_lock:
        return [
            {"execution_id": exec_id, **details}
            for exec_id, details in _active_executions.items()
            if details.get("status") == "running"
        ]


def clear_executions() -> None:
    """Clear all execution records."""
    with _executions_lock:
        _active_executions.clear()
        logger.info("executions_cleared")


# =============================================================================
# Registry Reset (for testing)
# =============================================================================


def reset_registry() -> None:
    """
    Reset entire registry (for testing purposes).
    
    Clears all sources, cached graphs, and execution records.
    """
    clear_sources()
    clear_graph_cache()
    clear_executions()
    logger.info("registry_reset")
