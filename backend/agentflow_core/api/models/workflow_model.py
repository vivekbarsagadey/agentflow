"""
AgentFlow Core - Workflow Data Models

Pydantic models for WorkflowSpec and related components.
These models provide type-safe validation for all workflow specifications.
"""

from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Literal, Optional, Union

from pydantic import BaseModel, Field, field_validator, model_validator


# =============================================================================
# Enums
# =============================================================================


class NodeType(str, Enum):
    """Supported node types in AgentFlow workflows."""
    INPUT = "input"
    ROUTER = "router"
    LLM = "llm"
    IMAGE = "image"
    DB = "db"
    AGGREGATOR = "aggregator"


class SourceKind(str, Enum):
    """Supported source kinds for external integrations."""
    LLM = "llm"
    IMAGE = "image"
    DB = "db"
    API = "api"


# =============================================================================
# Node Models
# =============================================================================


class NodeModel(BaseModel):
    """
    Represents a node in the workflow graph.
    
    Attributes:
        id: Unique identifier for the node
        type: Node type (input, router, llm, image, db, aggregator)
        metadata: Node-specific configuration
    """
    id: str = Field(..., min_length=1, max_length=100, description="Unique node identifier")
    type: NodeType = Field(..., description="Node type")
    metadata: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Node-specific configuration"
    )
    
    @field_validator("id")
    @classmethod
    def validate_id(cls, v: str) -> str:
        """Validate node ID format."""
        if not v.replace("_", "").replace("-", "").isalnum():
            raise ValueError("Node ID must be alphanumeric with underscores or hyphens")
        return v


# =============================================================================
# Edge Models
# =============================================================================


class EdgeModel(BaseModel):
    """
    Represents a connection between nodes.
    
    Attributes:
        from_node: Source node ID (aliased from 'from' in JSON)
        to: Target node ID(s) - can be single or multiple for conditional routing
        condition: Optional condition expression for conditional edges
    """
    from_node: str = Field(..., alias="from", description="Source node ID")
    to: Union[str, List[str]] = Field(..., description="Target node ID(s)")
    condition: Optional[str] = Field(
        default=None,
        description="Condition expression for routing"
    )
    
    model_config = {
        "populate_by_name": True,  # Allow both 'from' and 'from_node'
    }
    
    @field_validator("to")
    @classmethod
    def validate_to(cls, v: Union[str, List[str]]) -> Union[str, List[str]]:
        """Validate target node(s)."""
        if isinstance(v, list):
            if len(v) == 0:
                raise ValueError("Edge must have at least one target node")
            for node_id in v:
                if not node_id:
                    raise ValueError("Target node ID cannot be empty")
        elif not v:
            raise ValueError("Target node ID cannot be empty")
        return v


# =============================================================================
# Queue Models
# =============================================================================


class QueueBandwidthModel(BaseModel):
    """
    Bandwidth configuration for rate limiting.
    
    Attributes:
        max_messages_per_second: Maximum messages per second
        max_requests_per_minute: Maximum requests per minute
        max_tokens_per_minute: Maximum tokens per minute (for LLM nodes)
    """
    max_messages_per_second: Optional[int] = Field(
        default=None,
        ge=1,
        description="Maximum messages per second"
    )
    max_requests_per_minute: Optional[int] = Field(
        default=None,
        ge=1,
        description="Maximum requests per minute"
    )
    max_tokens_per_minute: Optional[int] = Field(
        default=None,
        ge=1,
        description="Maximum tokens per minute"
    )


class QueueModel(BaseModel):
    """
    Represents a rate-limited queue between nodes.
    
    Attributes:
        id: Unique queue identifier
        from_node: Source node ID
        to: Target node ID
        bandwidth: Optional bandwidth configuration
    """
    id: str = Field(..., min_length=1, description="Unique queue identifier")
    from_node: str = Field(..., alias="from", description="Source node ID")
    to: str = Field(..., description="Target node ID")
    bandwidth: Optional[QueueBandwidthModel] = Field(
        default=None,
        description="Bandwidth configuration"
    )
    
    model_config = {
        "populate_by_name": True,
    }


# =============================================================================
# Source Models
# =============================================================================


class SourceModel(BaseModel):
    """
    External service configuration (LLM, DB, API, etc.).
    
    Attributes:
        id: Unique source identifier
        kind: Source type (llm, image, db, api)
        config: Source-specific configuration
    """
    id: str = Field(..., min_length=1, description="Unique source identifier")
    kind: SourceKind = Field(..., description="Source type")
    config: Dict[str, Any] = Field(
        default_factory=dict,
        description="Source-specific configuration"
    )
    
    @field_validator("config")
    @classmethod
    def validate_config(cls, v: Dict[str, Any], info) -> Dict[str, Any]:
        """Validate config has required fields based on source kind."""
        # Note: Detailed validation happens in source adapters
        return v


# =============================================================================
# WorkflowSpec Model
# =============================================================================


class WorkflowSpecModel(BaseModel):
    """
    Complete workflow specification.
    
    This is the main model representing an entire AgentFlow workflow.
    It contains all nodes, edges, queues, sources, and the start node.
    
    Attributes:
        nodes: List of nodes in the workflow
        edges: List of edges connecting nodes
        queues: Optional list of rate-limited queues
        sources: List of external source configurations
        start_node: ID of the entry point node
    """
    nodes: List[NodeModel] = Field(..., min_length=1, description="Workflow nodes")
    edges: List[EdgeModel] = Field(default_factory=list, description="Node connections")
    queues: List[QueueModel] = Field(default_factory=list, description="Rate-limited queues")
    sources: List[SourceModel] = Field(default_factory=list, description="External sources")
    start_node: str = Field(..., description="Entry point node ID")
    
    # Optional metadata
    name: Optional[str] = Field(default=None, max_length=200, description="Workflow name")
    description: Optional[str] = Field(default=None, description="Workflow description")
    version: Optional[str] = Field(default="1.0.0", description="Workflow version")
    
    @model_validator(mode="after")
    def validate_workflow(self) -> "WorkflowSpecModel":
        """Validate workflow consistency."""
        node_ids = {node.id for node in self.nodes}
        
        # Validate start_node exists
        if self.start_node not in node_ids:
            raise ValueError(f"start_node '{self.start_node}' does not exist in nodes")
        
        # Validate edge references
        for edge in self.edges:
            if edge.from_node not in node_ids:
                raise ValueError(f"Edge source '{edge.from_node}' does not exist in nodes")
            
            targets = edge.to if isinstance(edge.to, list) else [edge.to]
            for target in targets:
                if target not in node_ids:
                    raise ValueError(f"Edge target '{target}' does not exist in nodes")
        
        # Validate queue references
        for queue in self.queues:
            if queue.from_node not in node_ids:
                raise ValueError(f"Queue source '{queue.from_node}' does not exist in nodes")
            if queue.to not in node_ids:
                raise ValueError(f"Queue target '{queue.to}' does not exist in nodes")
        
        return self
    
    def get_node(self, node_id: str) -> Optional[NodeModel]:
        """Get a node by ID."""
        for node in self.nodes:
            if node.id == node_id:
                return node
        return None
    
    def get_source(self, source_id: str) -> Optional[SourceModel]:
        """Get a source by ID."""
        for source in self.sources:
            if source.id == source_id:
                return source
        return None


# =============================================================================
# Request/Response Models
# =============================================================================


class ExecuteRequest(BaseModel):
    """
    Request model for workflow execution.
    
    Attributes:
        workflow: The workflow specification to execute
        initial_state: Initial state to pass to the workflow
    """
    workflow: WorkflowSpecModel = Field(..., description="Workflow specification")
    initial_state: Dict[str, Any] = Field(
        default_factory=dict,
        description="Initial state for execution"
    )


class ExecuteResponse(BaseModel):
    """
    Response model for workflow execution.
    
    Attributes:
        status: Execution status (success, error)
        final_state: Final state after execution
        execution_time_ms: Execution time in milliseconds
        tokens_used: Total tokens consumed (if applicable)
        cost: Estimated cost (if applicable)
    """
    status: Literal["success", "error"] = Field(..., description="Execution status")
    final_state: Dict[str, Any] = Field(
        default_factory=dict,
        description="Final workflow state"
    )
    execution_time_ms: Optional[float] = Field(
        default=None,
        description="Execution time in milliseconds"
    )
    tokens_used: Optional[int] = Field(default=None, description="Tokens consumed")
    cost: Optional[float] = Field(default=None, description="Estimated cost")
    error: Optional[str] = Field(default=None, description="Error message if failed")


class ValidationErrorModel(BaseModel):
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


class ValidationResult(BaseModel):
    """
    Result of workflow validation.
    
    Attributes:
        valid: Whether the workflow is valid
        errors: List of validation errors (empty if valid)
    """
    valid: bool = Field(..., description="Whether workflow is valid")
    errors: List[ValidationErrorModel] = Field(
        default_factory=list,
        description="Validation errors"
    )


# =============================================================================
# API Models
# =============================================================================


class HealthResponse(BaseModel):
    """Health check response."""
    status: Literal["healthy", "unhealthy"] = Field(default="healthy")
    version: str = Field(default="0.1.0")
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class ErrorResponse(BaseModel):
    """Standard error response."""
    error: str = Field(..., description="Error code")
    message: str = Field(..., description="Error message")
    context: Optional[Dict[str, Any]] = Field(default=None, description="Additional context")
