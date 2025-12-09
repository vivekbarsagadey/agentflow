"""
AgentFlow Core - Workflow API Routes

REST API endpoints for workflow validation, execution, and management.
"""

from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status

from agentflow_core.api.models.workflow_model import (
    ExecuteRequest,
    ExecuteResponse,
    ValidationResult,
    WorkflowSpecModel,
)
from agentflow_core.runtime.builder import build_graph_from_json
from agentflow_core.runtime.executor import create_execution_result, run_workflow
from agentflow_core.runtime.validator import validate_workflow
from agentflow_core.utils.id_generator import generate_workflow_id
from agentflow_core.utils.logger import get_logger, log_workflow_event

logger = get_logger(__name__)

# Create router
router = APIRouter(prefix="/workflows", tags=["workflows"])


# =============================================================================
# Validation Endpoints
# =============================================================================


@router.post(
    "/validate",
    response_model=ValidationResult,
    summary="Validate a workflow specification",
    description="Validates a workflow specification without executing it. Returns validation errors if any.",
)
async def validate_workflow_endpoint(
    spec: WorkflowSpecModel
) -> ValidationResult:
    """
    Validate a workflow specification.
    
    This endpoint validates the workflow specification for:
    - Schema correctness (Pydantic validation)
    - Node existence and types
    - Edge validity (source/target nodes exist)
    - Start node validation
    - Source reference validation
    
    Args:
        spec: The workflow specification to validate
        
    Returns:
        ValidationResult with valid flag and error list
    """
    try:
        # Generate a temporary workflow ID for logging
        workflow_id = spec.name or generate_workflow_id()
        
        log_workflow_event(
            "workflow_validation_requested",
            workflow_id,
            node_count=len(spec.nodes),
            edge_count=len(spec.edges)
        )
        
        # Run validation
        errors = validate_workflow(spec)
        
        logger.info(f"Validation completed with {len(errors)} errors")
        
        if errors:
            log_workflow_event(
                "workflow_validation_failed",
                workflow_id,
                error_count=len(errors)
            )
            
            # Convert ValidationError objects to ValidationErrorModel objects
            error_models = []
            for error in errors:
                try:
                    if hasattr(error, 'model_dump'):
                        error_models.append(error.model_dump())
                    else:
                        # Fallback: create ValidationErrorModel manually
                        error_models.append({
                            "type": getattr(error, 'type', 'unknown'),
                            "message": getattr(error, 'message', str(error)),
                            "node_id": getattr(error, 'node_id', None),
                            "field": getattr(error, 'field', None)
                        })
                except Exception as e:
                    logger.error(f"Error converting validation error: {e}")
                    error_models.append({
                        "type": "conversion_error",
                        "message": f"Failed to convert error: {str(error)}",
                        "node_id": None,
                        "field": None
                    })
            
            return ValidationResult(
                valid=False,
                errors=error_models
            )
        
        log_workflow_event("workflow_validation_passed", workflow_id)
        
        return ValidationResult(
            valid=True,
            errors=[]
        )
        
    except Exception as e:
        logger.error(f"Unexpected error in validate_workflow_endpoint: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "message": "Internal server error during validation",
                "error": str(e)
            }
        )


# =============================================================================
# Execution Endpoints
# =============================================================================


@router.post(
    "/execute",
    response_model=ExecuteResponse,
    summary="Execute a workflow",
    description="Validates and executes a workflow with the provided initial state.",
)
async def execute_workflow_endpoint(
    request: ExecuteRequest
) -> ExecuteResponse:
    """
    Execute a workflow with initial state.
    
    This endpoint:
    1. Validates the workflow specification
    2. Builds the LangGraph from the specification
    3. Executes the workflow with the provided initial state
    4. Returns the final state and execution metadata
    
    Args:
        request: ExecuteRequest with workflow and initial_state
        
    Returns:
        ExecuteResponse with status, final_state, and execution metadata
        
    Raises:
        HTTPException: 400 if validation fails
        HTTPException: 500 if execution fails
    """
    workflow = request.workflow
    initial_state = request.initial_state
    
    # Use workflow name or generate ID for logging
    workflow_id = workflow.name or generate_workflow_id()
    
    log_workflow_event(
        "workflow_execution_requested",
        workflow_id,
        node_count=len(workflow.nodes),
        edge_count=len(workflow.edges)
    )
    
    # Step 1: Validate workflow
    errors = validate_workflow(workflow)
    if errors:
        log_workflow_event(
            "workflow_execution_rejected",
            workflow_id,
            reason="validation_failed",
            error_count=len(errors)
        )
        
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "message": "Workflow validation failed",
                "errors": [e.model_dump() for e in errors]
            }
        )
    
    # Step 2: Build graph
    try:
        graph = build_graph_from_json(workflow)
    except Exception as e:
        log_workflow_event(
            "workflow_build_failed",
            workflow_id,
            error=str(e)
        )
        
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "message": "Failed to build workflow graph",
                "error": str(e)
            }
        )
    
    # Step 3: Execute workflow
    try:
        final_state = run_workflow(
            graph=graph,
            initial_state=initial_state,
            workflow_id=workflow.name or "unnamed"
        )
        
        log_workflow_event(
            "workflow_execution_completed",
            workflow_id,
            tokens_used=final_state.get("tokens_used", 0)
        )
        
        return ExecuteResponse(
            status="success",
            final_state=dict(final_state),
            execution_time_ms=final_state.get("metadata", {}).get("execution_time_ms", 0),
            tokens_used=final_state.get("tokens_used", 0)
        )
        
    except Exception as e:
        log_workflow_event(
            "workflow_execution_failed",
            workflow_id,
            error=str(e)
        )
        
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "message": "Workflow execution failed",
                "error": str(e)
            }
        )


# =============================================================================
# Utility Endpoints
# =============================================================================


@router.post(
    "/build",
    summary="Build a workflow graph",
    description="Validates and builds a workflow graph without executing it. Useful for testing.",
)
async def build_workflow_endpoint(
    spec: WorkflowSpecModel
) -> Dict[str, Any]:
    """
    Build a workflow graph without executing.
    
    This endpoint validates and builds the graph, returning build info.
    Useful for testing graph construction without side effects.
    
    Args:
        spec: Workflow specification
        
    Returns:
        Dictionary with build information
    """
    # Validate first
    errors = validate_workflow(spec)
    if errors:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "message": "Workflow validation failed",
                "errors": [e.model_dump() for e in errors]
            }
        )
    
    # Build graph
    try:
        graph = build_graph_from_json(spec, register_sources=False)
        
        return {
            "status": "success",
            "message": "Workflow graph built successfully",
            "node_count": len(spec.nodes),
            "edge_count": len(spec.edges),
            "start_node": spec.start_node,
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "message": "Failed to build workflow graph",
                "error": str(e)
            }
        )


@router.get(
    "/node-types",
    summary="Get available node types",
    description="Returns a list of all available node types.",
)
async def get_node_types() -> Dict[str, Any]:
    """
    Get available node types.
    
    Returns:
        Dictionary with node types and descriptions
    """
    from agentflow_core.nodes import NODE_FACTORIES
    
    return {
        "node_types": list(NODE_FACTORIES.keys()),
        "descriptions": {
            "input": "Entry point node that accepts user input",
            "router": "Conditional routing based on intent classification",
            "llm": "Language model node for text generation",
            "image": "Image generation node",
            "db": "Database query node (read-only)",
            "aggregator": "Combines results from multiple nodes",
        }
    }


@router.get(
    "/source-types",
    summary="Get available source types",
    description="Returns a list of all available source adapter types.",
)
async def get_source_types() -> Dict[str, Any]:
    """
    Get available source types.
    
    Returns:
        Dictionary with source types and descriptions
    """
    from agentflow_core.sources import SOURCE_FACTORIES
    
    return {
        "source_types": list(set(SOURCE_FACTORIES.keys())),
        "descriptions": {
            "llm": "Google Gemini language model",
            "gemini": "Google Gemini language model",
            "image": "Google Imagen/Gemini image generation",
            "imagen": "Google Imagen image generation",
            "db": "PostgreSQL database",
            "postgres": "PostgreSQL database",
            "api": "HTTP API client",
            "http": "HTTP API client",
        }
    }
