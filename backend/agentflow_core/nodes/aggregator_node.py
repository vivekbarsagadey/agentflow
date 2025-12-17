"""
AgentFlow Core - Aggregator Node

Aggregator node that combines results from multiple nodes into final output.
Supports various aggregation strategies.
"""

from typing import Any, Callable, Dict, List, Optional

from agentflow_core.nodes.base_node import (
    NodeCallable,
    create_node_wrapper,
    get_metadata_value,
    interpolate_template,
)
from agentflow_core.runtime.state import GraphState, merge_state
from agentflow_core.utils.logger import get_logger

logger = get_logger(__name__)


# =============================================================================
# Aggregation Strategies
# =============================================================================


class AggregationStrategy:
    """Constants for aggregation strategy types."""
    MERGE = "merge"
    PRIORITY = "priority"
    TEMPLATE = "template"
    CONCAT = "concat"
    SELECT = "select"
    CUSTOM = "custom"


# =============================================================================
# Aggregator Node Factory
# =============================================================================


def create_aggregator_node(
    node_id: str,
    metadata: Optional[Dict[str, Any]] = None
) -> NodeCallable:
    """
    Create an aggregator node that combines results.
    
    The aggregator node collects results from the state and combines
    them into a final output using the specified strategy.
    
    Args:
        node_id: Unique identifier for this node
        metadata: Configuration options:
            - strategy: Aggregation strategy (merge, priority, template, concat)
            - output_key: State key for output (default: "final_output")
            - source_keys: List of state keys to aggregate
            - template: Output template for template strategy
            - priority_order: Priority order for priority strategy
            - separator: Separator for concat strategy
            - include_metadata: Whether to include execution metadata
    
    Strategies:
        - merge: Combine all source values into a dictionary
        - priority: Select first non-empty value from priority order
        - template: Format output using a template
        - concat: Concatenate text values with separator
        - select: Select specific key from state
    
    Returns:
        A callable that performs aggregation
        
    Example:
        >>> node = create_aggregator_node("agg_1", {
        ...     "strategy": "merge",
        ...     "source_keys": ["text_result", "image_result", "db_result"]
        ... })
    """
    _metadata = metadata or {}
    
    def execute(state: GraphState, meta: Dict[str, Any]) -> GraphState:
        """Execute aggregator node logic."""
        strategy = get_metadata_value(meta, "strategy", AggregationStrategy.MERGE)
        output_key = get_metadata_value(meta, "output_key", "final_output")
        source_keys = get_metadata_value(
            meta,
            "source_keys",
            ["text_result", "image_result", "db_result"]
        )
        include_metadata = get_metadata_value(meta, "include_metadata", True)
        
        # Aggregate based on strategy
        if strategy == AggregationStrategy.MERGE:
            result = _aggregate_merge(state, source_keys)
        elif strategy == AggregationStrategy.PRIORITY:
            priority_order = get_metadata_value(meta, "priority_order", source_keys)
            result = _aggregate_priority(state, priority_order)
        elif strategy == AggregationStrategy.TEMPLATE:
            template = get_metadata_value(meta, "template", "")
            result = _aggregate_template(state, template)
        elif strategy == AggregationStrategy.CONCAT:
            separator = get_metadata_value(meta, "separator", "\n\n")
            result = _aggregate_concat(state, source_keys, separator)
        elif strategy == AggregationStrategy.SELECT:
            select_key = get_metadata_value(meta, "select_key", "text_result")
            result = state.get(select_key)
        else:
            logger.warning("unknown_aggregation_strategy", strategy=strategy)
            result = _aggregate_merge(state, source_keys)
        
        # Optionally include execution metadata
        if include_metadata:
            final_result = {
                "result": result,
                "execution_path": state.get("execution_path", []),
                "tokens_used": state.get("tokens_used", 0),
                "cost": state.get("cost", 0.0),
            }
        else:
            final_result = result
        
        logger.info(
            "aggregator_node_completed",
            node_id=node_id,
            strategy=strategy,
            result_type=type(result).__name__
        )
        
        return merge_state(state, {output_key: final_result})
    
    return create_node_wrapper(node_id, "aggregator", execute, _metadata)


# =============================================================================
# Aggregation Strategy Implementations
# =============================================================================


def _aggregate_merge(
    state: GraphState,
    source_keys: List[str]
) -> Dict[str, Any]:
    """
    Merge all source values into a dictionary.
    
    Looks for keys in both the state and state["outputs"].
    
    Args:
        state: Current graph state
        source_keys: List of keys to merge
        
    Returns:
        Dictionary with all non-empty values
    """
    result: Dict[str, Any] = {}
    outputs = state.get("outputs", {})
    
    for key in source_keys:
        # First check direct state, then outputs
        value = state.get(key)
        if value is None or value == "" or value == [] or value == {}:
            value = outputs.get(key)
        
        if value is not None and value != "" and value != [] and value != {}:
            result[key] = value
    
    return result


def _aggregate_priority(
    state: GraphState,
    priority_order: List[str]
) -> Any:
    """
    Select first non-empty value from priority order.
    
    Looks for keys in both the state and state["outputs"].
    
    Args:
        state: Current graph state
        priority_order: List of keys in priority order
        
    Returns:
        First non-empty value found
    """
    outputs = state.get("outputs", {})
    
    for key in priority_order:
        # First check direct state, then outputs
        value = state.get(key)
        if value is None or value == "" or value == [] or value == {}:
            value = outputs.get(key)
        
        if value is not None and value != "" and value != [] and value != {}:
            return value
    
    return None


def _aggregate_template(
    state: GraphState,
    template: str
) -> str:
    """
    Format output using a template.
    
    Args:
        state: Current graph state
        template: Template string with {placeholders}
        
    Returns:
        Formatted string
        
    Example:
        >>> template = "Result: {text_result}\nImage: {image_result[url]}"
    """
    if not template:
        # Default template
        template = """
Result:
{text_result}

Image: {image_result}

Data: {db_result}
        """.strip()
    
    return interpolate_template(template, state)


def _aggregate_concat(
    state: GraphState,
    source_keys: List[str],
    separator: str
) -> str:
    """
    Concatenate text values with separator.
    
    Looks for keys in both the state and state["outputs"].
    
    Args:
        state: Current graph state
        source_keys: Keys to concatenate
        separator: Separator between values
        
    Returns:
        Concatenated string
    """
    parts: List[str] = []
    outputs = state.get("outputs", {})
    
    for key in source_keys:
        # First check direct state, then outputs
        value = state.get(key)
        if value is None or value == "" or value == [] or value == {}:
            value = outputs.get(key)
        
        if value:
            if isinstance(value, str):
                parts.append(value)
            elif isinstance(value, dict):
                # For dicts, use a formatted representation
                parts.append(f"{key}: {value}")
            elif isinstance(value, list):
                # For lists, join items
                parts.append(f"{key}: {', '.join(str(v) for v in value)}")
            else:
                parts.append(str(value))
    
    return separator.join(parts)


# =============================================================================
# Utility Functions
# =============================================================================


def create_final_output(
    state: GraphState,
    include_keys: Optional[List[str]] = None,
    exclude_keys: Optional[List[str]] = None
) -> Dict[str, Any]:
    """
    Create a final output dictionary from state.
    
    Args:
        state: Current graph state
        include_keys: If provided, only include these keys
        exclude_keys: If provided, exclude these keys
        
    Returns:
        Final output dictionary
    """
    output: Dict[str, Any] = {}
    
    # Default keys to include
    default_keys = [
        "text_result", "image_result", "db_result", "api_result",
        "final_output", "intent", "tokens_used", "cost"
    ]
    
    keys_to_include = include_keys or default_keys
    keys_to_exclude = set(exclude_keys or [])
    
    for key in keys_to_include:
        if key not in keys_to_exclude:
            value = state.get(key)
            if value is not None:
                output[key] = value
    
    return output
