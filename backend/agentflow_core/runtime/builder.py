"""
AgentFlow Core - Runtime Graph Builder

Converts WorkflowSpec JSON to executable LangGraph StateGraph.
This is the core compilation layer that transforms workflow definitions
into runnable graphs.
"""

from typing import Any, Callable, Dict, List, Optional, Union

from langgraph.graph import END, StateGraph

from agentflow_core.api.models.workflow_model import (
    EdgeModel,
    NodeModel,
    WorkflowSpecModel,
)
from agentflow_core.nodes import (
    NODE_FACTORIES,
    create_aggregator_node,
    create_db_node,
    create_image_node,
    create_input_node,
    create_llm_node,
    create_router_node,
)
from agentflow_core.runtime.registry import register_sources_from_spec
from agentflow_core.runtime.state import GraphState
from agentflow_core.utils.error_handler import ValidationError
from agentflow_core.utils.logger import get_logger

logger = get_logger(__name__)


# =============================================================================
# Main Builder Function
# =============================================================================


def build_graph_from_json(
    spec: WorkflowSpecModel,
    register_sources: bool = True
) -> StateGraph:
    """
    Build a LangGraph StateGraph from a WorkflowSpec.
    
    This is the main entry point for workflow compilation.
    It converts the JSON specification into an executable graph.
    
    Args:
        spec: The workflow specification to compile
        register_sources: Whether to register sources in the registry
        
    Returns:
        Compiled LangGraph StateGraph
        
    Example:
        >>> spec = WorkflowSpecModel.model_validate(workflow_json)
        >>> graph = build_graph_from_json(spec)
        >>> result = graph.invoke(initial_state)
    """
    logger.info(
        "building_graph",
        node_count=len(spec.nodes),
        edge_count=len(spec.edges),
        start_node=spec.start_node
    )
    
    # Register sources for node access
    if register_sources and spec.sources:
        sources_data = [s.model_dump() for s in spec.sources]
        register_sources_from_spec(sources_data)
    
    # Create graph builder
    builder = StateGraph(GraphState)
    
    # Build node ID to callable mapping
    node_callables = _create_node_callables(spec.nodes)
    
    # Add nodes to graph
    for node_id, callable_fn in node_callables.items():
        builder.add_node(node_id, callable_fn)
        logger.debug("node_added", node_id=node_id)
    
    # Set entry point
    builder.set_entry_point(spec.start_node)
    
    # Add edges
    _add_edges(builder, spec.edges, spec.nodes)
    
    # Compile the graph
    compiled = builder.compile()
    
    logger.info("graph_built_successfully")
    
    return compiled


# =============================================================================
# Node Creation
# =============================================================================


def _create_node_callables(
    nodes: List[NodeModel]
) -> Dict[str, Callable[[GraphState], GraphState]]:
    """
    Create callable functions for each node.
    
    Args:
        nodes: List of node models
        
    Returns:
        Dictionary mapping node IDs to callable functions
    """
    callables: Dict[str, Callable[[GraphState], GraphState]] = {}
    
    for node in nodes:
        node_type = node.type.value  # NodeType enum to string
        metadata = node.metadata or {}
        
        callable_fn = create_node_callable(node_type, node.id, metadata)
        callables[node.id] = callable_fn
    
    return callables


def create_node_callable(
    node_type: str,
    node_id: str,
    metadata: Dict[str, Any]
) -> Callable[[GraphState], GraphState]:
    """
    Create a callable for a specific node type.
    
    Args:
        node_type: Type of node (input, router, llm, etc.)
        node_id: Unique node identifier
        metadata: Node configuration
        
    Returns:
        Callable that processes GraphState
        
    Raises:
        ValueError: If node type is not supported
    """
    # Map node type to factory function
    factory = NODE_FACTORIES.get(node_type.lower())
    
    if factory is None:
        supported = ", ".join(NODE_FACTORIES.keys())
        raise ValueError(
            f"Unsupported node type: '{node_type}'. "
            f"Supported types: {supported}"
        )
    
    return factory(node_id, metadata)


# =============================================================================
# Edge Construction
# =============================================================================


def _add_edges(
    builder: StateGraph,
    edges: List[EdgeModel],
    nodes: List[NodeModel]
) -> None:
    """
    Add edges to the graph builder.
    
    Handles both simple and conditional edges.
    
    Args:
        builder: StateGraph builder instance
        edges: List of edge models
        nodes: List of node models (for type lookup)
    """
    # Build node type lookup
    node_types = {node.id: node.type.value for node in nodes}
    
    # Track which nodes have outgoing edges
    nodes_with_edges = set()
    
    for edge in edges:
        from_node = edge.from_node
        to_nodes = edge.to if isinstance(edge.to, list) else [edge.to]
        condition = edge.condition
        
        nodes_with_edges.add(from_node)
        
        # Check if this is a router node with conditional edges
        from_node_type = node_types.get(from_node, "")
        
        if from_node_type == "router" and len(to_nodes) > 1:
            # Conditional edge based on router intent
            _add_conditional_edge(builder, from_node, to_nodes, condition)
        elif condition:
            # Conditional edge with explicit condition
            _add_conditional_edge(builder, from_node, to_nodes, condition)
        else:
            # Simple edge
            for to_node in to_nodes:
                if to_node.lower() == "end" or to_node == "__end__":
                    builder.add_edge(from_node, END)
                else:
                    builder.add_edge(from_node, to_node)
                logger.debug("edge_added", from_node=from_node, to_node=to_node)
    
    # Add END edges for nodes without outgoing edges (except aggregators which might be terminal)
    for node in nodes:
        if node.id not in nodes_with_edges:
            # Check if this node type is typically terminal
            if node.type.value == "aggregator":
                builder.add_edge(node.id, END)
                logger.debug("terminal_edge_added", node_id=node.id)


def _add_conditional_edge(
    builder: StateGraph,
    from_node: str,
    to_nodes: List[str],
    condition: Optional[str]
) -> None:
    """
    Add a conditional edge to the graph.
    
    Args:
        builder: StateGraph builder
        from_node: Source node ID
        to_nodes: List of possible target nodes
        condition: Condition expression (optional)
    """
    # Create routing function based on intent
    def routing_function(state: GraphState) -> str:
        """Route based on intent field in state."""
        intent = state.get("intent", "")
        
        # Try to match intent to a target node
        for target in to_nodes:
            # Check if intent matches target node name
            if intent.lower() == target.lower():
                return target
            # Check if intent is contained in target name
            if intent.lower() in target.lower():
                return target
        
        # Default to first target
        return to_nodes[0] if to_nodes else END
    
    # Build path map for conditional edges
    path_map = {node: node for node in to_nodes}
    
    # Add conditional edge
    builder.add_conditional_edges(
        from_node,
        routing_function,
        path_map
    )
    
    logger.debug(
        "conditional_edge_added",
        from_node=from_node,
        targets=to_nodes
    )


# =============================================================================
# Builder Utilities
# =============================================================================


def validate_and_build(
    spec: WorkflowSpecModel
) -> StateGraph:
    """
    Validate workflow spec and build graph.
    
    This is a convenience function that validates before building.
    
    Args:
        spec: Workflow specification
        
    Returns:
        Compiled graph
        
    Raises:
        ValidationError: If validation fails
    """
    from agentflow_core.runtime.validator import validate_workflow
    
    errors = validate_workflow(spec)
    if errors:
        error_messages = [e.message for e in errors]
        raise ValidationError(
            message="Workflow validation failed",
            errors=[e.model_dump() for e in errors]
        )
    
    return build_graph_from_json(spec)


def build_from_dict(
    workflow_dict: Dict[str, Any]
) -> StateGraph:
    """
    Build graph from a dictionary.
    
    Convenience function for building from raw JSON/dict.
    
    Args:
        workflow_dict: Workflow specification as dictionary
        
    Returns:
        Compiled graph
    """
    spec = WorkflowSpecModel.model_validate(workflow_dict)
    return build_graph_from_json(spec)


# =============================================================================
# Graph Inspection
# =============================================================================


def get_graph_info(graph: StateGraph) -> Dict[str, Any]:
    """
    Get information about a compiled graph.
    
    Args:
        graph: Compiled StateGraph
        
    Returns:
        Dictionary with graph information
    """
    return {
        "type": "StateGraph",
        "compiled": True,
    }
