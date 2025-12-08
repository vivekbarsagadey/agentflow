"""
AgentFlow Core - Workflow Validator

Comprehensive validation of workflow specifications before execution.
Performs schema validation, semantic validation, and graph analysis.
"""

from typing import Any, Dict, List, Optional, Set

from pydantic import BaseModel, Field

from agentflow_core.api.models.workflow_model import (
    NodeType,
    SourceKind,
    WorkflowSpecModel,
)
from agentflow_core.utils.logger import get_logger

logger = get_logger(__name__)


# =============================================================================
# Validation Error Model
# =============================================================================


class ValidationError(BaseModel):
    """
    Represents a single validation error.
    
    Attributes:
        type: Error type/code
        message: Human-readable error message
        node_id: Related node ID (if applicable)
        field: Related field name (if applicable)
    """
    type: str = Field(..., description="Error type/code")
    message: str = Field(..., description="Error message")
    node_id: Optional[str] = Field(default=None, description="Related node ID")
    field: Optional[str] = Field(default=None, description="Related field")


# =============================================================================
# Error Types
# =============================================================================

ERROR_TYPES = {
    "MISSING_START_NODE": "start_node_missing",
    "INVALID_START_NODE": "start_node_invalid",
    "INVALID_EDGE_SOURCE": "edge_source_invalid",
    "INVALID_EDGE_TARGET": "edge_target_invalid",
    "INVALID_QUEUE_SOURCE": "queue_source_invalid",
    "INVALID_QUEUE_TARGET": "queue_target_invalid",
    "ORPHANED_NODE": "orphaned_node",
    "CYCLE_DETECTED": "cycle_detected",
    "INVALID_NODE_TYPE": "node_type_invalid",
    "MISSING_SOURCE": "source_missing",
    "INVALID_SOURCE_KIND": "source_kind_invalid",
    "MISSING_METADATA": "metadata_missing",
    "INVALID_METADATA": "metadata_invalid",
    "DUPLICATE_NODE_ID": "duplicate_node_id",
    "DUPLICATE_SOURCE_ID": "duplicate_source_id",
    "DUPLICATE_QUEUE_ID": "duplicate_queue_id",
    "EMPTY_NODES": "empty_nodes",
}


# =============================================================================
# Main Validation Function
# =============================================================================


def validate_workflow(spec: WorkflowSpecModel) -> List[ValidationError]:
    """
    Validate a workflow specification comprehensively.
    
    Performs the following validations:
    1. Schema validation (already done by Pydantic)
    2. Semantic validation (logical consistency)
    3. Graph structure validation (cycles, orphans)
    4. Source reference validation
    
    Args:
        spec: The workflow specification to validate
        
    Returns:
        List of validation errors (empty if valid)
        
    Example:
        >>> errors = validate_workflow(workflow_spec)
        >>> if not errors:
        ...     print("Workflow is valid!")
        ... else:
        ...     for error in errors:
        ...         print(f"{error.type}: {error.message}")
    """
    errors: List[ValidationError] = []
    
    logger.info("workflow_validation_started", node_count=len(spec.nodes))
    
    # Collect node and source IDs for reference validation
    node_ids = {node.id for node in spec.nodes}
    source_ids = {source.id for source in spec.sources}
    
    # Run all validations
    errors.extend(_validate_no_duplicates(spec))
    errors.extend(_validate_start_node(spec, node_ids))
    errors.extend(_validate_edges(spec, node_ids))
    errors.extend(_validate_queues(spec, node_ids))
    errors.extend(_validate_nodes(spec, source_ids))
    errors.extend(_validate_sources(spec))
    errors.extend(_validate_orphaned_nodes(spec, node_ids))
    # errors.extend(_detect_cycles(spec))  # Optional for MVP
    
    logger.info(
        "workflow_validation_completed",
        valid=len(errors) == 0,
        error_count=len(errors)
    )
    
    return errors


# =============================================================================
# Individual Validation Functions
# =============================================================================


def _validate_no_duplicates(spec: WorkflowSpecModel) -> List[ValidationError]:
    """Check for duplicate IDs in nodes, sources, and queues."""
    errors: List[ValidationError] = []
    
    # Check duplicate node IDs
    node_ids: Set[str] = set()
    for node in spec.nodes:
        if node.id in node_ids:
            errors.append(ValidationError(
                type=ERROR_TYPES["DUPLICATE_NODE_ID"],
                message=f"Duplicate node ID: '{node.id}'",
                node_id=node.id
            ))
        node_ids.add(node.id)
    
    # Check duplicate source IDs
    source_ids: Set[str] = set()
    for source in spec.sources:
        if source.id in source_ids:
            errors.append(ValidationError(
                type=ERROR_TYPES["DUPLICATE_SOURCE_ID"],
                message=f"Duplicate source ID: '{source.id}'",
                field="sources"
            ))
        source_ids.add(source.id)
    
    # Check duplicate queue IDs
    queue_ids: Set[str] = set()
    for queue in spec.queues:
        if queue.id in queue_ids:
            errors.append(ValidationError(
                type=ERROR_TYPES["DUPLICATE_QUEUE_ID"],
                message=f"Duplicate queue ID: '{queue.id}'",
                field="queues"
            ))
        queue_ids.add(queue.id)
    
    return errors


def _validate_start_node(
    spec: WorkflowSpecModel,
    node_ids: Set[str]
) -> List[ValidationError]:
    """Validate the start_node exists and is valid."""
    errors: List[ValidationError] = []
    
    if not spec.start_node:
        errors.append(ValidationError(
            type=ERROR_TYPES["MISSING_START_NODE"],
            message="start_node is required",
            field="start_node"
        ))
    elif spec.start_node not in node_ids:
        errors.append(ValidationError(
            type=ERROR_TYPES["INVALID_START_NODE"],
            message=f"start_node '{spec.start_node}' does not exist in nodes",
            field="start_node",
            node_id=spec.start_node
        ))
    
    return errors


def _validate_edges(
    spec: WorkflowSpecModel,
    node_ids: Set[str]
) -> List[ValidationError]:
    """Validate all edge source and target nodes exist."""
    errors: List[ValidationError] = []
    
    for i, edge in enumerate(spec.edges):
        # Validate source node
        if edge.from_node not in node_ids:
            errors.append(ValidationError(
                type=ERROR_TYPES["INVALID_EDGE_SOURCE"],
                message=f"Edge source '{edge.from_node}' does not exist in nodes",
                field=f"edges[{i}].from",
                node_id=edge.from_node
            ))
        
        # Validate target node(s)
        targets = edge.to if isinstance(edge.to, list) else [edge.to]
        for target in targets:
            if target not in node_ids:
                errors.append(ValidationError(
                    type=ERROR_TYPES["INVALID_EDGE_TARGET"],
                    message=f"Edge target '{target}' does not exist in nodes",
                    field=f"edges[{i}].to",
                    node_id=target
                ))
    
    return errors


def _validate_queues(
    spec: WorkflowSpecModel,
    node_ids: Set[str]
) -> List[ValidationError]:
    """Validate all queue source and target nodes exist."""
    errors: List[ValidationError] = []
    
    for i, queue in enumerate(spec.queues):
        # Validate source node
        if queue.from_node not in node_ids:
            errors.append(ValidationError(
                type=ERROR_TYPES["INVALID_QUEUE_SOURCE"],
                message=f"Queue source '{queue.from_node}' does not exist in nodes",
                field=f"queues[{i}].from",
                node_id=queue.from_node
            ))
        
        # Validate target node
        if queue.to not in node_ids:
            errors.append(ValidationError(
                type=ERROR_TYPES["INVALID_QUEUE_TARGET"],
                message=f"Queue target '{queue.to}' does not exist in nodes",
                field=f"queues[{i}].to",
                node_id=queue.to
            ))
    
    return errors


def _validate_nodes(
    spec: WorkflowSpecModel,
    source_ids: Set[str]
) -> List[ValidationError]:
    """Validate node configurations and source references."""
    errors: List[ValidationError] = []
    
    for node in spec.nodes:
        # Check node type is valid (already validated by Pydantic enum)
        
        # Validate metadata based on node type
        metadata = node.metadata or {}
        
        if node.type == NodeType.LLM:
            # LLM nodes should reference a source
            source_id = metadata.get("source_id")
            if source_id and source_id not in source_ids:
                errors.append(ValidationError(
                    type=ERROR_TYPES["MISSING_SOURCE"],
                    message=f"LLM node references non-existent source: '{source_id}'",
                    node_id=node.id,
                    field="metadata.source_id"
                ))
            
            # Check for prompt
            if not metadata.get("prompt") and not metadata.get("prompt_template"):
                errors.append(ValidationError(
                    type=ERROR_TYPES["MISSING_METADATA"],
                    message="LLM node requires 'prompt' or 'prompt_template' in metadata",
                    node_id=node.id,
                    field="metadata.prompt"
                ))
        
        elif node.type == NodeType.IMAGE:
            # Image nodes should reference a source
            source_id = metadata.get("source_id")
            if source_id and source_id not in source_ids:
                errors.append(ValidationError(
                    type=ERROR_TYPES["MISSING_SOURCE"],
                    message=f"Image node references non-existent source: '{source_id}'",
                    node_id=node.id,
                    field="metadata.source_id"
                ))
        
        elif node.type == NodeType.DB:
            # DB nodes should reference a source and have a query
            source_id = metadata.get("source_id")
            if source_id and source_id not in source_ids:
                errors.append(ValidationError(
                    type=ERROR_TYPES["MISSING_SOURCE"],
                    message=f"DB node references non-existent source: '{source_id}'",
                    node_id=node.id,
                    field="metadata.source_id"
                ))
            
            if not metadata.get("query"):
                errors.append(ValidationError(
                    type=ERROR_TYPES["MISSING_METADATA"],
                    message="DB node requires 'query' in metadata",
                    node_id=node.id,
                    field="metadata.query"
                ))
        
        elif node.type == NodeType.ROUTER:
            # Router nodes should have routing configuration
            if not metadata.get("routes") and not metadata.get("strategy"):
                errors.append(ValidationError(
                    type=ERROR_TYPES["MISSING_METADATA"],
                    message="Router node requires 'routes' or 'strategy' in metadata",
                    node_id=node.id,
                    field="metadata.routes"
                ))
    
    return errors


def _validate_sources(spec: WorkflowSpecModel) -> List[ValidationError]:
    """Validate source configurations."""
    errors: List[ValidationError] = []
    
    for source in spec.sources:
        config = source.config or {}
        
        if source.kind == SourceKind.LLM:
            # LLM sources should have model configuration
            if not config.get("model") and not config.get("model_name"):
                errors.append(ValidationError(
                    type=ERROR_TYPES["MISSING_METADATA"],
                    message=f"LLM source '{source.id}' requires 'model' in config",
                    field=f"sources.{source.id}.config.model"
                ))
        
        elif source.kind == SourceKind.DB:
            # DB sources should have connection configuration
            if not config.get("connection_string_env") and not config.get("connection_string"):
                errors.append(ValidationError(
                    type=ERROR_TYPES["MISSING_METADATA"],
                    message=f"DB source '{source.id}' requires 'connection_string_env' in config",
                    field=f"sources.{source.id}.config.connection_string_env"
                ))
    
    return errors


def _validate_orphaned_nodes(
    spec: WorkflowSpecModel,
    node_ids: Set[str]
) -> List[ValidationError]:
    """Detect nodes that have no incoming edges (except start_node)."""
    errors: List[ValidationError] = []
    
    # Build set of nodes with incoming edges
    nodes_with_incoming: Set[str] = set()
    for edge in spec.edges:
        targets = edge.to if isinstance(edge.to, list) else [edge.to]
        nodes_with_incoming.update(targets)
    
    # Also add targets from queues
    for queue in spec.queues:
        nodes_with_incoming.add(queue.to)
    
    # Start node doesn't need incoming edges
    nodes_with_incoming.add(spec.start_node)
    
    # Find orphaned nodes (nodes with no incoming edges)
    for node_id in node_ids:
        if node_id not in nodes_with_incoming:
            # This is an orphaned node
            errors.append(ValidationError(
                type=ERROR_TYPES["ORPHANED_NODE"],
                message=f"Node '{node_id}' has no incoming edges and is not reachable",
                node_id=node_id
            ))
    
    return errors


def _detect_cycles(spec: WorkflowSpecModel) -> List[ValidationError]:
    """
    Detect cycles in the workflow graph.
    
    Uses DFS to find back edges indicating cycles.
    This is optional for MVP as some workflows may intentionally have loops.
    """
    errors: List[ValidationError] = []
    
    # Build adjacency list
    adjacency: Dict[str, List[str]] = {node.id: [] for node in spec.nodes}
    for edge in spec.edges:
        targets = edge.to if isinstance(edge.to, list) else [edge.to]
        adjacency[edge.from_node].extend(targets)
    
    # DFS state
    WHITE, GRAY, BLACK = 0, 1, 2
    colors: Dict[str, int] = {node.id: WHITE for node in spec.nodes}
    
    def dfs(node_id: str, path: List[str]) -> Optional[List[str]]:
        """DFS to detect cycles. Returns cycle path if found."""
        colors[node_id] = GRAY
        path.append(node_id)
        
        for neighbor in adjacency.get(node_id, []):
            if colors.get(neighbor, WHITE) == GRAY:
                # Found a cycle
                cycle_start = path.index(neighbor)
                return path[cycle_start:]
            elif colors.get(neighbor, WHITE) == WHITE:
                result = dfs(neighbor, path)
                if result:
                    return result
        
        path.pop()
        colors[node_id] = BLACK
        return None
    
    # Run DFS from each unvisited node
    for node in spec.nodes:
        if colors[node.id] == WHITE:
            cycle = dfs(node.id, [])
            if cycle:
                errors.append(ValidationError(
                    type=ERROR_TYPES["CYCLE_DETECTED"],
                    message=f"Cycle detected: {' -> '.join(cycle)} -> {cycle[0]}",
                    node_id=cycle[0]
                ))
                break  # Only report first cycle
    
    return errors


# =============================================================================
# Validation Result Builder
# =============================================================================


def create_validation_result(
    errors: List[ValidationError]
) -> Dict[str, Any]:
    """
    Create a validation result dictionary.
    
    Args:
        errors: List of validation errors
        
    Returns:
        Dictionary with 'valid' boolean and 'errors' list
    """
    return {
        "valid": len(errors) == 0,
        "errors": [error.model_dump() for error in errors]
    }
