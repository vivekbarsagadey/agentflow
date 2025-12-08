"""
AgentFlow Core - Base Node Interface

Defines the common interface and utilities for all node types.
All node implementations should follow the patterns defined here.
"""

from abc import ABC, abstractmethod
from typing import Any, Callable, Dict, Optional

from agentflow_core.runtime.state import GraphState, add_to_execution_path
from agentflow_core.utils.logger import get_logger, log_node_event

logger = get_logger(__name__)


# Type alias for node callable
NodeCallable = Callable[[GraphState], GraphState]


class BaseNode(ABC):
    """
    Abstract base class for all node types.
    
    Provides common functionality and interface for nodes.
    While AgentFlow prefers functional patterns, this class
    can be used when OOP is more appropriate.
    """
    
    def __init__(
        self,
        node_id: str,
        node_type: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Initialize a node.
        
        Args:
            node_id: Unique identifier for this node
            node_type: The type of node (input, router, llm, etc.)
            metadata: Node-specific configuration
        """
        self.node_id = node_id
        self.node_type = node_type
        self.metadata = metadata or {}
    
    @abstractmethod
    def execute(self, state: GraphState) -> GraphState:
        """
        Execute the node logic.
        
        Args:
            state: Current graph state
            
        Returns:
            Updated graph state
        """
        pass
    
    def __call__(self, state: GraphState) -> GraphState:
        """Make node callable for LangGraph integration."""
        log_node_event("node_started", self.node_id, self.node_type)
        
        # Add node to execution path
        state = add_to_execution_path(state, self.node_id)
        
        try:
            result = self.execute(state)
            log_node_event(
                "node_completed",
                self.node_id,
                self.node_type
            )
            return result
        except Exception as e:
            log_node_event(
                "node_failed",
                self.node_id,
                self.node_type,
                error=str(e)
            )
            raise


def create_node_wrapper(
    node_id: str,
    node_type: str,
    execute_fn: Callable[[GraphState, Dict[str, Any]], GraphState],
    metadata: Optional[Dict[str, Any]] = None
) -> NodeCallable:
    """
    Create a wrapped node callable with logging and error handling.
    
    This is the preferred functional approach for creating nodes.
    
    Args:
        node_id: Unique identifier for the node
        node_type: The type of node
        execute_fn: Function that performs the actual node logic
        metadata: Node-specific configuration
        
    Returns:
        A callable that wraps the execution with logging
        
    Example:
        >>> def my_logic(state: GraphState, metadata: Dict) -> GraphState:
        ...     return {**state, "result": "done"}
        >>> node = create_node_wrapper("my_node", "custom", my_logic, {})
        >>> result = node(initial_state)
    """
    _metadata = metadata or {}
    
    def wrapper(state: GraphState) -> GraphState:
        log_node_event("node_started", node_id, node_type)
        
        # Add node to execution path
        updated_state = add_to_execution_path(state, node_id)
        
        try:
            result = execute_fn(updated_state, _metadata)
            log_node_event("node_completed", node_id, node_type)
            return result
        except Exception as e:
            log_node_event(
                "node_failed",
                node_id,
                node_type,
                error=str(e)
            )
            raise
    
    # Set function name for debugging
    wrapper.__name__ = f"node_{node_id}"
    wrapper.__doc__ = f"Node {node_id} ({node_type})"
    
    return wrapper


def get_metadata_value(
    metadata: Dict[str, Any],
    key: str,
    default: Any = None,
    required: bool = False
) -> Any:
    """
    Get a value from node metadata with validation.
    
    Args:
        metadata: Node metadata dictionary
        key: Key to retrieve
        default: Default value if not found
        required: If True, raises error when key is missing
        
    Returns:
        The value from metadata or default
        
    Raises:
        ValueError: If required key is missing
    """
    value = metadata.get(key, default)
    if required and value is None:
        raise ValueError(f"Required metadata key '{key}' is missing")
    return value


def interpolate_template(
    template: str,
    state: GraphState
) -> str:
    """
    Interpolate a template string with values from state.
    
    Supports {variable_name} syntax for substitution.
    
    Args:
        template: Template string with {placeholders}
        state: Current graph state
        
    Returns:
        Interpolated string
        
    Example:
        >>> template = "Hello {user_input}, your intent is {intent}"
        >>> state = {"user_input": "world", "intent": "greeting"}
        >>> result = interpolate_template(template, state)
        >>> print(result)
        'Hello world, your intent is greeting'
    """
    try:
        # Use format_map to handle missing keys gracefully
        class SafeDict(dict):
            def __missing__(self, key: str) -> str:
                return f"{{{key}}}"  # Keep placeholder if not found
        
        safe_state = SafeDict(state)
        return template.format_map(safe_state)
    except Exception as e:
        logger.warning(
            "template_interpolation_failed",
            template=template[:100],
            error=str(e)
        )
        return template
