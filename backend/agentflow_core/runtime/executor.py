"""
AgentFlow Core - Workflow Executor

Executes compiled LangGraph workflows with initial state and returns results.
Provides execution management, error handling, and result tracking.
"""

import time
from typing import Any, Dict, Optional

from langgraph.graph import StateGraph

from agentflow_core.api.models.workflow_model import WorkflowSpecModel
from agentflow_core.runtime.builder import build_graph_from_json
from agentflow_core.runtime.registry import (
    complete_execution,
    register_execution,
)
from agentflow_core.runtime.state import GraphState, create_initial_state
from agentflow_core.utils.error_handler import WorkflowExecutionError
from agentflow_core.utils.id_generator import generate_execution_id
from agentflow_core.utils.logger import get_logger, log_workflow_event

logger = get_logger(__name__)


# =============================================================================
# Main Executor Functions
# =============================================================================


def run_workflow(
    graph: StateGraph,
    initial_state: Dict[str, Any],
    execution_id: Optional[str] = None,
    workflow_id: Optional[str] = None,
    timeout: Optional[int] = None
) -> GraphState:
    """
    Execute a compiled workflow graph with initial state.
    
    This is the main execution function for running workflows.
    
    Args:
        graph: Compiled LangGraph StateGraph
        initial_state: Initial state dictionary
        execution_id: Optional execution ID for tracking
        workflow_id: Optional workflow ID for tracking
        timeout: Optional timeout in seconds
        
    Returns:
        Final GraphState after execution
        
    Raises:
        WorkflowExecutionError: If execution fails
        
    Example:
        >>> graph = build_graph_from_json(spec)
        >>> initial_state = {"user_input": "Hello, world!"}
        >>> result = run_workflow(graph, initial_state)
        >>> print(result["final_output"])
    """
    # Generate execution ID if not provided
    exec_id = execution_id or generate_execution_id()
    
    # Prepare initial state
    state = _prepare_initial_state(initial_state)
    
    # Track execution start
    start_time = time.time()
    register_execution(exec_id, workflow_id or "unknown", {
        "initial_state": initial_state,
        "timeout": timeout,
    })
    
    log_workflow_event(
        "workflow_execution_started",
        workflow_id=workflow_id or "unknown",
        execution_id=exec_id
    )
    
    try:
        # Execute the graph
        result = graph.invoke(state)
        
        # Calculate execution time
        execution_time_ms = (time.time() - start_time) * 1000
        
        # Track successful completion
        complete_execution(exec_id, "completed", {
            "execution_time_ms": execution_time_ms,
            "tokens_used": result.get("tokens_used", 0),
        })
        
        log_workflow_event(
            "workflow_execution_completed",
            workflow_id=workflow_id or "unknown",
            execution_id=exec_id,
            execution_time_ms=round(execution_time_ms, 2),
            tokens_used=result.get("tokens_used", 0)
        )
        
        # Add execution metadata to result
        result["metadata"] = {
            **result.get("metadata", {}),
            "execution_id": exec_id,
            "execution_time_ms": execution_time_ms,
        }
        
        return result
        
    except Exception as e:
        # Calculate execution time
        execution_time_ms = (time.time() - start_time) * 1000
        
        # Track failed execution
        complete_execution(exec_id, "failed", {
            "error": str(e),
            "execution_time_ms": execution_time_ms,
        })
        
        log_workflow_event(
            "workflow_execution_failed",
            workflow_id=workflow_id or "unknown",
            execution_id=exec_id,
            error=str(e)
        )
        
        raise WorkflowExecutionError(
            message=f"Workflow execution failed: {str(e)}",
            workflow_id=workflow_id,
            partial_state=state
        )


def execute_workflow(
    spec: WorkflowSpecModel,
    initial_state: Dict[str, Any],
    **kwargs: Any
) -> GraphState:
    """
    Build and execute a workflow from specification.
    
    This is a convenience function that combines building and execution.
    
    Args:
        spec: Workflow specification
        initial_state: Initial state dictionary
        **kwargs: Additional arguments for run_workflow
        
    Returns:
        Final GraphState after execution
        
    Example:
        >>> spec = WorkflowSpecModel.model_validate(workflow_json)
        >>> result = execute_workflow(spec, {"user_input": "Hello"})
    """
    # Build the graph
    graph = build_graph_from_json(spec)
    
    # Run the workflow
    return run_workflow(
        graph=graph,
        initial_state=initial_state,
        workflow_id=spec.name or "unnamed",
        **kwargs
    )


def execute_workflow_from_dict(
    workflow_dict: Dict[str, Any],
    initial_state: Dict[str, Any],
    **kwargs: Any
) -> GraphState:
    """
    Execute a workflow from a dictionary specification.
    
    Args:
        workflow_dict: Workflow specification as dictionary
        initial_state: Initial state dictionary
        **kwargs: Additional arguments
        
    Returns:
        Final GraphState after execution
    """
    spec = WorkflowSpecModel.model_validate(workflow_dict)
    return execute_workflow(spec, initial_state, **kwargs)


# =============================================================================
# State Preparation
# =============================================================================


def _prepare_initial_state(
    initial_state: Dict[str, Any]
) -> GraphState:
    """
    Prepare the initial state for execution.
    
    Ensures all required fields are present and properly typed.
    Supports both predefined GraphState keys and custom keys.
    
    Args:
        initial_state: User-provided initial state
        
    Returns:
        Properly formatted GraphState
    """
    # Start with default state
    state = create_initial_state(
        user_input=initial_state.get("user_input", "")
    )
    
    # Merge user-provided state (allow all keys for flexibility)
    for key, value in initial_state.items():
        state[key] = value  # type: ignore
    
    return state


# =============================================================================
# Execution Result Helpers
# =============================================================================


def create_execution_result(
    final_state: GraphState,
    execution_time_ms: float,
    status: str = "success"
) -> Dict[str, Any]:
    """
    Create a structured execution result.
    
    Args:
        final_state: Final GraphState
        execution_time_ms: Execution time in milliseconds
        status: Execution status
        
    Returns:
        Structured result dictionary
    """
    return {
        "status": status,
        "final_state": dict(final_state),
        "execution_time_ms": round(execution_time_ms, 2),
        "tokens_used": final_state.get("tokens_used", 0),
        "cost": final_state.get("cost", 0.0),
        "execution_path": final_state.get("execution_path", []),
    }


def extract_final_output(
    state: GraphState,
    include_metadata: bool = False
) -> Any:
    """
    Extract the final output from state.
    
    Args:
        state: Final GraphState
        include_metadata: Whether to include execution metadata
        
    Returns:
        Final output value
    """
    final_output = state.get("final_output")
    
    if not include_metadata:
        # If final_output is a dict with 'result' key, extract it
        if isinstance(final_output, dict) and "result" in final_output:
            return final_output["result"]
        return final_output
    
    return final_output


# =============================================================================
# Streaming Execution (for future use)
# =============================================================================


async def stream_workflow(
    graph: StateGraph,
    initial_state: Dict[str, Any],
    **kwargs: Any
):
    """
    Execute a workflow with streaming output.
    
    Yields intermediate states as the workflow executes.
    
    Note: Currently not implemented. Use run_workflow for sync execution.
    """
    raise NotImplementedError("Streaming execution not yet implemented")


# =============================================================================
# Batch Execution
# =============================================================================


def run_workflow_batch(
    graph: StateGraph,
    initial_states: list[Dict[str, Any]],
    **kwargs: Any
) -> list[GraphState]:
    """
    Execute a workflow with multiple initial states.
    
    Args:
        graph: Compiled graph
        initial_states: List of initial states
        **kwargs: Additional arguments for run_workflow
        
    Returns:
        List of final states
    """
    results = []
    
    for i, initial_state in enumerate(initial_states):
        try:
            result = run_workflow(
                graph=graph,
                initial_state=initial_state,
                execution_id=f"{kwargs.get('execution_id', 'batch')}_{i}",
                **kwargs
            )
            results.append(result)
        except Exception as e:
            # Add error state
            error_state = create_initial_state(
                user_input=initial_state.get("user_input", "")
            )
            error_state["errors"] = [str(e)]  # type: ignore
            results.append(error_state)
    
    return results
