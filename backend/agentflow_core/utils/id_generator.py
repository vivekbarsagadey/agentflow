"""
AgentFlow Core - ID Generator Utility

Provides functions to generate unique, prefixed IDs for various entities.
Uses UUID4 for uniqueness with readable prefixes.
"""

import uuid
from typing import Literal


# Entity prefixes following AgentFlow conventions
ID_PREFIXES = {
    "workflow": "wf_",
    "node": "node_",
    "queue": "queue_",
    "source": "src_",
    "execution": "exec_",
}


def generate_id(
    prefix: Literal["workflow", "node", "queue", "source", "execution"] = "workflow",
    length: int = 12
) -> str:
    """
    Generate a unique ID with a prefix.
    
    Args:
        prefix: The entity type prefix
        length: Length of the random part (default 12)
        
    Returns:
        A unique ID string like 'wf_abc123def456'
        
    Example:
        >>> generate_id("workflow")
        'wf_a1b2c3d4e5f6'
    """
    # Generate UUID and take first `length` characters
    random_part = uuid.uuid4().hex[:length]
    return f"{ID_PREFIXES.get(prefix, 'id_')}{random_part}"


def generate_workflow_id() -> str:
    """Generate a unique workflow ID."""
    return generate_id("workflow")


def generate_node_id() -> str:
    """Generate a unique node ID."""
    return generate_id("node")


def generate_queue_id() -> str:
    """Generate a unique queue ID."""
    return generate_id("queue")


def generate_source_id() -> str:
    """Generate a unique source ID."""
    return generate_id("source")


def generate_execution_id() -> str:
    """Generate a unique execution ID."""
    return generate_id("execution")


def is_valid_id(entity_id: str, entity_type: str | None = None) -> bool:
    """
    Validate that an ID follows the expected format.
    
    Args:
        entity_id: The ID to validate
        entity_type: Optional entity type to check prefix
        
    Returns:
        True if valid, False otherwise
    """
    if not entity_id or not isinstance(entity_id, str):
        return False
    
    if entity_type:
        expected_prefix = ID_PREFIXES.get(entity_type)
        if expected_prefix and not entity_id.startswith(expected_prefix):
            return False
    
    # Check that ID has a prefix and random part
    parts = entity_id.split("_", 1)
    if len(parts) != 2:
        return False
    
    # Random part should be alphanumeric
    return parts[1].isalnum()
