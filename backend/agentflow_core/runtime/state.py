"""
AgentFlow Core - GraphState Definition

Defines the GraphState TypedDict used for state management across workflow execution.
State is passed between nodes and tracks the execution context.
"""

from typing import Any, Dict, List, Optional, TypedDict


class GraphState(TypedDict, total=False):
    """
    State passed between nodes during workflow execution.
    
    This TypedDict defines all possible fields that can be present in the state.
    Fields are optional (total=False) to allow partial state at different stages.
    
    Attributes:
        user_input: Original input from the user
        intent: Classified intent from router node
        text_result: Output from LLM node
        image_result: Output from image generation node
        db_result: Results from database queries
        api_result: Results from HTTP API calls
        final_output: Aggregated final result
        tokens_used: Total tokens consumed in this execution
        cost: Estimated cost for this execution
        metadata: Additional execution metadata
        errors: List of errors encountered during execution
        execution_path: List of node IDs executed in order
        current_node: ID of the currently executing node
    """
    
    # Input
    user_input: str
    """Original input from the user."""
    
    # Routing
    intent: str
    """Classified intent from router node."""
    
    # Node Results
    text_result: str
    """Output from LLM node."""
    
    image_result: Dict[str, Any]
    """
    Output from image generation node.
    Typically contains:
    - url: Image URL
    - prompt: Prompt used
    - model: Model used
    - size: Image dimensions
    """
    
    db_result: List[Dict[str, Any]]
    """Results from database queries as list of records."""
    
    api_result: Dict[str, Any]
    """Results from HTTP API calls."""
    
    # Aggregated Output
    final_output: Any
    """Aggregated final result from aggregator node."""
    
    # Metrics
    tokens_used: int
    """Total tokens consumed in this execution."""
    
    cost: float
    """Estimated cost for this execution in USD."""
    
    # Execution Context
    metadata: Dict[str, Any]
    """Additional execution metadata."""
    
    errors: List[str]
    """List of error messages encountered during execution."""
    
    execution_path: List[str]
    """List of node IDs executed in order."""
    
    current_node: str
    """ID of the currently executing node."""


def create_initial_state(
    user_input: str = "",
    **kwargs: Any
) -> GraphState:
    """
    Create an initial GraphState with default values.
    
    Args:
        user_input: The initial user input
        **kwargs: Additional state fields to set
        
    Returns:
        A new GraphState with initialized fields
        
    Example:
        >>> state = create_initial_state("Tell me a joke")
        >>> print(state["user_input"])
        'Tell me a joke'
    """
    state: GraphState = {
        "user_input": user_input,
        "intent": "",
        "text_result": "",
        "image_result": {},
        "db_result": [],
        "api_result": {},
        "final_output": None,
        "tokens_used": 0,
        "cost": 0.0,
        "metadata": {},
        "errors": [],
        "execution_path": [],
        "current_node": "",
    }
    
    # Override with any provided values
    for key, value in kwargs.items():
        if key in GraphState.__annotations__:
            state[key] = value  # type: ignore
    
    return state


def merge_state(base: GraphState, updates: Dict[str, Any]) -> GraphState:
    """
    Create a new state by merging updates into base state.
    
    This follows immutable state pattern - creates new state instead of modifying.
    
    Args:
        base: The base state to start from
        updates: Updates to apply
        
    Returns:
        New state with updates applied
        
    Example:
        >>> state = create_initial_state("Hello")
        >>> new_state = merge_state(state, {"text_result": "Hi there!"})
        >>> print(new_state["text_result"])
        'Hi there!'
    """
    new_state: GraphState = dict(base)  # type: ignore
    
    for key, value in updates.items():
        if key in GraphState.__annotations__:
            new_state[key] = value  # type: ignore
    
    return new_state


def add_to_execution_path(state: GraphState, node_id: str) -> GraphState:
    """
    Add a node ID to the execution path.
    
    Args:
        state: Current state
        node_id: Node ID to add
        
    Returns:
        New state with updated execution path
    """
    execution_path = list(state.get("execution_path", []))
    execution_path.append(node_id)
    return merge_state(state, {
        "execution_path": execution_path,
        "current_node": node_id
    })


def add_error(state: GraphState, error: str) -> GraphState:
    """
    Add an error message to the state.
    
    Args:
        state: Current state
        error: Error message to add
        
    Returns:
        New state with error added
    """
    errors = list(state.get("errors", []))
    errors.append(error)
    return merge_state(state, {"errors": errors})


def add_tokens(state: GraphState, tokens: int, cost: float = 0.0) -> GraphState:
    """
    Add token usage and cost to the state.
    
    Args:
        state: Current state
        tokens: Number of tokens to add
        cost: Cost to add
        
    Returns:
        New state with updated metrics
    """
    current_tokens = state.get("tokens_used", 0)
    current_cost = state.get("cost", 0.0)
    return merge_state(state, {
        "tokens_used": current_tokens + tokens,
        "cost": current_cost + cost
    })
