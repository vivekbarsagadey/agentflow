"""
AgentFlow Core - Router Node

Conditional routing node that classifies intent and directs flow.
Supports keyword-based, rule-based, and LLM-based routing strategies.
"""

import re
from typing import Any, Callable, Dict, List, Optional, Tuple

from agentflow_core.nodes.base_node import (
    NodeCallable,
    create_node_wrapper,
    get_metadata_value,
)
from agentflow_core.runtime.state import GraphState, merge_state
from agentflow_core.utils.logger import get_logger

logger = get_logger(__name__)


# =============================================================================
# Routing Strategies
# =============================================================================


class RoutingStrategy:
    """Constants for routing strategy types."""
    KEYWORD = "keyword"
    PATTERN = "pattern"
    RULES = "rules"
    LLM = "llm"
    DEFAULT = "default"


# =============================================================================
# Main Router Node Factory
# =============================================================================


def create_router_node(
    node_id: str,
    metadata: Optional[Dict[str, Any]] = None
) -> NodeCallable:
    """
    Create a router node that classifies intent.
    
    The router node analyzes input and determines the routing intent.
    It supports multiple routing strategies.
    
    Args:
        node_id: Unique identifier for this node
        metadata: Configuration options:
            - strategy: Routing strategy (keyword, pattern, rules, llm)
            - routes: List of route definitions
            - default_intent: Default intent if no match
            - input_key: Key to read from state (default: "user_input")
            
    Route definition format:
        {
            "intent": "greeting",
            "keywords": ["hello", "hi", "hey"],  # For keyword strategy
            "pattern": "^(hello|hi).*",          # For pattern strategy
            "condition": "contains('help')",      # For rules strategy
        }
    
    Returns:
        A callable that performs routing
        
    Example:
        >>> node = create_router_node("router_1", {
        ...     "strategy": "keyword",
        ...     "routes": [
        ...         {"intent": "greeting", "keywords": ["hello", "hi"]},
        ...         {"intent": "question", "keywords": ["what", "how", "why"]},
        ...     ],
        ...     "default_intent": "general"
        ... })
    """
    _metadata = metadata or {}
    
    def execute(state: GraphState, meta: Dict[str, Any]) -> GraphState:
        """Execute router node logic."""
        strategy = get_metadata_value(meta, "strategy", RoutingStrategy.KEYWORD)
        routes = get_metadata_value(meta, "routes", [])
        default_intent = get_metadata_value(meta, "default_intent", "unknown")
        input_key = get_metadata_value(meta, "input_key", "user_input")
        
        # Get input to route
        input_value = str(state.get(input_key, ""))
        
        # Determine intent based on strategy
        intent = default_intent
        
        if strategy == RoutingStrategy.KEYWORD:
            intent = _route_by_keyword(input_value, routes, default_intent)
        elif strategy == RoutingStrategy.PATTERN:
            intent = _route_by_pattern(input_value, routes, default_intent)
        elif strategy == RoutingStrategy.RULES:
            intent = _route_by_rules(input_value, routes, default_intent, state)
        elif strategy == RoutingStrategy.LLM:
            # LLM-based routing (requires source)
            intent = _route_by_llm(input_value, routes, default_intent, meta, state)
        else:
            logger.warning("unknown_routing_strategy", strategy=strategy)
        
        logger.info(
            "router_classified",
            node_id=node_id,
            intent=intent,
            strategy=strategy
        )
        
        return merge_state(state, {"intent": intent})
    
    return create_node_wrapper(node_id, "router", execute, _metadata)


# =============================================================================
# Routing Strategy Implementations
# =============================================================================


def _route_by_keyword(
    input_value: str,
    routes: List[Dict[str, Any]],
    default_intent: str
) -> str:
    """
    Route based on keyword matching.
    
    Checks if any keywords from routes are present in the input.
    """
    input_lower = input_value.lower()
    
    for route in routes:
        intent = route.get("intent")
        keywords = route.get("keywords", [])
        
        if not intent or not keywords:
            continue
        
        for keyword in keywords:
            if keyword.lower() in input_lower:
                return intent
    
    return default_intent


def _route_by_pattern(
    input_value: str,
    routes: List[Dict[str, Any]],
    default_intent: str
) -> str:
    """
    Route based on regex pattern matching.
    """
    for route in routes:
        intent = route.get("intent")
        pattern = route.get("pattern")
        
        if not intent or not pattern:
            continue
        
        try:
            if re.match(pattern, input_value, re.IGNORECASE):
                return intent
        except re.error as e:
            logger.warning("invalid_regex_pattern", pattern=pattern, error=str(e))
    
    return default_intent


def _route_by_rules(
    input_value: str,
    routes: List[Dict[str, Any]],
    default_intent: str,
    state: GraphState
) -> str:
    """
    Route based on rule evaluation.
    
    Supports simple condition expressions.
    """
    for route in routes:
        intent = route.get("intent")
        condition = route.get("condition")
        
        if not intent or not condition:
            continue
        
        if _evaluate_condition(condition, input_value, state):
            return intent
    
    return default_intent


def _evaluate_condition(
    condition: str,
    input_value: str,
    state: GraphState
) -> bool:
    """
    Evaluate a simple condition expression.
    
    Supported functions:
    - contains('text'): Check if input contains text
    - starts_with('text'): Check if input starts with text
    - ends_with('text'): Check if input ends with text
    - length_gt(n): Check if input length > n
    - length_lt(n): Check if input length < n
    - equals('text'): Check if input equals text
    """
    input_lower = input_value.lower()
    
    # Parse condition
    if condition.startswith("contains("):
        match = re.match(r"contains\(['\"](.+)['\"]\)", condition)
        if match:
            return match.group(1).lower() in input_lower
    
    elif condition.startswith("starts_with("):
        match = re.match(r"starts_with\(['\"](.+)['\"]\)", condition)
        if match:
            return input_lower.startswith(match.group(1).lower())
    
    elif condition.startswith("ends_with("):
        match = re.match(r"ends_with\(['\"](.+)['\"]\)", condition)
        if match:
            return input_lower.endswith(match.group(1).lower())
    
    elif condition.startswith("length_gt("):
        match = re.match(r"length_gt\((\d+)\)", condition)
        if match:
            return len(input_value) > int(match.group(1))
    
    elif condition.startswith("length_lt("):
        match = re.match(r"length_lt\((\d+)\)", condition)
        if match:
            return len(input_value) < int(match.group(1))
    
    elif condition.startswith("equals("):
        match = re.match(r"equals\(['\"](.+)['\"]\)", condition)
        if match:
            return input_lower == match.group(1).lower()
    
    logger.warning("unsupported_condition", condition=condition)
    return False


def _route_by_llm(
    input_value: str,
    routes: List[Dict[str, Any]],
    default_intent: str,
    metadata: Dict[str, Any],
    state: GraphState
) -> str:
    """
    Route based on LLM classification.
    
    Uses an LLM to classify the intent of the input.
    """
    # Note: For MVP, we'll use keyword routing as fallback
    # Full LLM routing will be implemented with source integration
    logger.info("llm_routing_not_implemented_using_keyword_fallback")
    return _route_by_keyword(input_value, routes, default_intent)


# =============================================================================
# Routing Utilities
# =============================================================================


def get_route_condition_function(
    intent: str,
    routes: List[Dict[str, Any]]
) -> Callable[[GraphState], bool]:
    """
    Create a condition function for conditional edges in LangGraph.
    
    Args:
        intent: The intent to check for
        routes: Route definitions (not used in condition function)
        
    Returns:
        A callable that returns True if state intent matches
        
    Example:
        >>> condition = get_route_condition_function("greeting", routes)
        >>> if condition(state):
        ...     # Route to greeting handler
    """
    def condition(state: GraphState) -> bool:
        return state.get("intent") == intent
    
    return condition


def create_routing_function(
    routes: List[Dict[str, Any]],
    default_node: str
) -> Callable[[GraphState], str]:
    """
    Create a routing function for LangGraph conditional edges.
    
    Args:
        routes: List of route definitions with intent -> node_id mapping
        default_node: Default node if no intent matches
        
    Returns:
        A callable that returns the next node ID based on intent
    """
    # Build intent -> node mapping
    intent_to_node: Dict[str, str] = {}
    for route in routes:
        intent = route.get("intent")
        target_node = route.get("target_node") or route.get("to")
        if intent and target_node:
            intent_to_node[intent] = target_node
    
    def routing_function(state: GraphState) -> str:
        intent = state.get("intent", "")
        return intent_to_node.get(intent, default_node)
    
    return routing_function
