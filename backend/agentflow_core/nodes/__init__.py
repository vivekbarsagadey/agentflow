"""
AgentFlow Core - Node Implementations

Exports all node types and utilities.
"""

from agentflow_core.nodes.base_node import (
    BaseNode,
    NodeCallable,
    create_node_wrapper,
    get_metadata_value,
    interpolate_template,
)
from agentflow_core.nodes.input_node import create_input_node
from agentflow_core.nodes.router_node import (
    RoutingStrategy,
    create_router_node,
    create_routing_function,
    get_route_condition_function,
)
from agentflow_core.nodes.llm_node import create_llm_node
from agentflow_core.nodes.image_node import create_image_node
from agentflow_core.nodes.db_node import create_db_node
from agentflow_core.nodes.aggregator_node import (
    AggregationStrategy,
    create_aggregator_node,
    create_final_output,
)

# Node type to factory function mapping
NODE_FACTORIES = {
    "input": create_input_node,
    "router": create_router_node,
    "llm": create_llm_node,
    "image": create_image_node,
    "db": create_db_node,
    "aggregator": create_aggregator_node,
}


def create_node(
    node_type: str,
    node_id: str,
    metadata: dict | None = None
) -> NodeCallable:
    """
    Create a node of the specified type.
    
    Args:
        node_type: Type of node to create
        node_id: Unique identifier for the node
        metadata: Node-specific configuration
        
    Returns:
        A callable that executes the node logic
        
    Raises:
        ValueError: If node type is not supported
        
    Example:
        >>> node = create_node("llm", "llm_1", {"prompt": "Hello"})
        >>> result = node(initial_state)
    """
    factory = NODE_FACTORIES.get(node_type.lower())
    
    if factory is None:
        supported = ", ".join(NODE_FACTORIES.keys())
        raise ValueError(
            f"Unsupported node type: '{node_type}'. "
            f"Supported types: {supported}"
        )
    
    return factory(node_id, metadata)


__all__ = [
    # Base
    "BaseNode",
    "NodeCallable",
    "create_node_wrapper",
    "get_metadata_value",
    "interpolate_template",
    # Node factories
    "create_node",
    "create_input_node",
    "create_router_node",
    "create_llm_node",
    "create_image_node",
    "create_db_node",
    "create_aggregator_node",
    # Strategies and utilities
    "RoutingStrategy",
    "AggregationStrategy",
    "create_routing_function",
    "get_route_condition_function",
    "create_final_output",
    # Registry
    "NODE_FACTORIES",
]
