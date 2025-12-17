"""
AgentFlow Core - GraphState Definition

Defines the GraphState TypedDict used for state management across workflow execution.
State is passed between nodes and tracks the execution context.
"""

import operator
from typing import Annotated, Any, Dict, List, Optional, TypedDict


def merge_dict(left: Dict[str, Any], right: Dict[str, Any]) -> Dict[str, Any]:
    """Merge two dictionaries, with right taking precedence."""
    return {**left, **right}


def replace_value(left: Any, right: Any) -> Any:
    """Replace left with right (simple override)."""
    return right


def keep_first(left: Any, right: Any) -> Any:
    """Keep the first (left) value, ignore updates (right)."""
    return left if left else right


class GraphState(TypedDict, total=False):
    """
    State passed between nodes during workflow execution.
    
    This TypedDict defines all possible fields that can be present in the state.
    Fields are optional (total=False) to allow partial state at different stages.
    
    Uses Annotated types with reducers to properly accumulate state in LangGraph.
    
    Attributes:
        user_input: Original input from the user (immutable after initialization)
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
        current_node: List of currently executing nodes
        outputs: Dynamic outputs from nodes (stores custom output_key values)
    """
    
    # Input - use keep_first to prevent concurrent updates during parallel execution
    user_input: Annotated[str, keep_first]
    """Original input from the user (immutable after initialization)."""
    
    # Routing
    intent: Annotated[str, keep_first]
    """Classified intent from router node (immutable after routing)."""
    
    # Node Results - these are rarely used directly, outputs dict is preferred
    text_result: Annotated[str, keep_first]
    """Output from LLM node (legacy field, prefer outputs dict)."""
    
    image_result: Annotated[Dict[str, Any], merge_dict]
    """
    Output from image generation node (legacy field, prefer outputs dict).
    Typically contains:
    - url: Image URL
    - prompt: Prompt used
    - model: Model used
    - size: Image dimensions
    """
    
    db_result: Annotated[List[Dict[str, Any]], operator.add]
    """Results from database queries as list of records (legacy field)."""
    
    api_result: Annotated[Dict[str, Any], merge_dict]
    """Results from HTTP API calls (legacy field)."""
    
    # Aggregated Output
    final_output: Annotated[Any, keep_first]
    """Aggregated final result from aggregator node."""
    
    # Metrics - use operator.add to sum up tokens/cost from parallel branches
    tokens_used: Annotated[int, operator.add]
    """Total tokens consumed in this execution."""
    
    cost: Annotated[float, operator.add]
    """Estimated cost for this execution in USD."""
    
    # Execution Context
    metadata: Annotated[Dict[str, Any], merge_dict]
    """Additional execution metadata."""
    
    errors: Annotated[List[str], operator.add]
    """List of error messages encountered during execution."""
    
    execution_path: Annotated[List[str], operator.add]
    """List of node IDs executed in order."""
    
    current_node: Annotated[List[str], operator.add]
    """List of currently executing nodes (supports parallel execution)."""
    
    # Dynamic outputs - stores custom output_key values
    outputs: Annotated[Dict[str, Any], merge_dict]
    """Dynamic outputs from nodes (custom output_key values like 'summary', 'translation')."""


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
        "current_node": [],
        "outputs": {},  # Dynamic outputs storage
    }
    
    # Override with any provided values
    for key, value in kwargs.items():
        if key in GraphState.__annotations__:
            state[key] = value  # type: ignore
        else:
            # Store custom keys in outputs dict
            state["outputs"][key] = value  # type: ignore
    
    return state


def merge_state(base: GraphState, updates: Dict[str, Any]) -> GraphState:
    """
    Create a new state by merging updates into base state.
    
    This follows immutable state pattern - creates new state instead of modifying.
    Custom keys (not in GraphState) are stored in the 'outputs' dict.
    
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
        >>> # Custom keys are stored in outputs
        >>> new_state = merge_state(state, {"summary": "Custom output"})
        >>> print(new_state["outputs"]["summary"])
        'Custom output'
    """
    # Create shallow copy
    new_state: GraphState = dict(base)  # type: ignore
    new_outputs = dict(base.get("outputs", {}))
    
    # Process updates
    for key, value in updates.items():
        if key in GraphState.__annotations__:
            # Known key - update directly
            new_state[key] = value  # type: ignore
        else:
            # Custom key - store in outputs
            new_outputs[key] = value
    
    new_state["outputs"] = new_outputs  # type: ignore
    
    return new_state


def add_to_execution_path(state: GraphState, node_id: str) -> GraphState:
    """
    Add a node ID to the execution path.
    
    With LangGraph reducers, we only return the delta (new items to add).
    The reducer (operator.add) will append these to the existing list.
    
    Args:
        state: Current state
        node_id: Node ID to add
        
    Returns:
        State update with just the new node ID in execution_path
    """
    # Return only the NEW items to add (not the full list)
    # LangGraph's reducer will handle appending
    return {
        "execution_path": [node_id],
        "current_node": [node_id]  # Also a list for parallel execution support
    }  # type: ignore


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
