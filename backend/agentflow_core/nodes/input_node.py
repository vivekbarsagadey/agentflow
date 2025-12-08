"""
AgentFlow Core - Input Node

Entry point node that accepts and processes user input.
Passes state through with minimal transformation.
"""

from typing import Any, Callable, Dict, Optional

from agentflow_core.nodes.base_node import (
    NodeCallable,
    create_node_wrapper,
    get_metadata_value,
)
from agentflow_core.runtime.state import GraphState, merge_state
from agentflow_core.utils.logger import get_logger

logger = get_logger(__name__)


def create_input_node(
    node_id: str,
    metadata: Optional[Dict[str, Any]] = None
) -> NodeCallable:
    """
    Create an input node that accepts user input.
    
    The input node is typically the entry point of a workflow.
    It can optionally transform or validate the input.
    
    Args:
        node_id: Unique identifier for this node
        metadata: Optional configuration:
            - input_key: Key to read from state (default: "user_input")
            - output_key: Key to write to state (default: same as input_key)
            - transform: Optional transform function name
            - validate: Optional validation rules
    
    Returns:
        A callable that processes input state
        
    Example:
        >>> node = create_input_node("input_1", {"input_key": "user_input"})
        >>> state = {"user_input": "Hello, world!"}
        >>> result = node(state)
    """
    _metadata = metadata or {}
    
    def execute(state: GraphState, meta: Dict[str, Any]) -> GraphState:
        """Execute input node logic."""
        input_key = get_metadata_value(meta, "input_key", "user_input")
        output_key = get_metadata_value(meta, "output_key", input_key)
        
        # Get input value
        input_value = state.get(input_key, "")
        
        # Optional: Apply transform
        transform = get_metadata_value(meta, "transform")
        if transform:
            input_value = _apply_transform(input_value, transform)
        
        # Optional: Validate input
        validate = get_metadata_value(meta, "validate")
        if validate:
            _validate_input(input_value, validate)
        
        logger.info(
            "input_node_processed",
            node_id=node_id,
            input_length=len(str(input_value))
        )
        
        # Update state
        updates: Dict[str, Any] = {}
        if output_key != input_key:
            updates[output_key] = input_value
        
        # Add input processing metadata
        updates["metadata"] = {
            **state.get("metadata", {}),
            "input_processed": True,
            "input_node_id": node_id,
        }
        
        return merge_state(state, updates)
    
    return create_node_wrapper(node_id, "input", execute, _metadata)


def _apply_transform(value: Any, transform: str) -> Any:
    """Apply a named transform to the input value."""
    transforms = {
        "lowercase": lambda v: v.lower() if isinstance(v, str) else v,
        "uppercase": lambda v: v.upper() if isinstance(v, str) else v,
        "strip": lambda v: v.strip() if isinstance(v, str) else v,
        "trim": lambda v: v.strip() if isinstance(v, str) else v,
    }
    
    transform_fn = transforms.get(transform.lower())
    if transform_fn:
        return transform_fn(value)
    
    logger.warning("unknown_transform", transform=transform)
    return value


def _validate_input(value: Any, rules: Dict[str, Any]) -> None:
    """Validate input against rules."""
    # Min length check
    min_length = rules.get("min_length")
    if min_length and isinstance(value, str) and len(value) < min_length:
        raise ValueError(f"Input must be at least {min_length} characters")
    
    # Max length check
    max_length = rules.get("max_length")
    if max_length and isinstance(value, str) and len(value) > max_length:
        raise ValueError(f"Input must be at most {max_length} characters")
    
    # Required check
    required = rules.get("required", False)
    if required and not value:
        raise ValueError("Input is required")
