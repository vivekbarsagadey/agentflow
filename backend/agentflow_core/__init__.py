"""
AgentFlow Core - Multi-Agent Workflow Orchestration Engine

A Python-based workflow orchestration engine built on FastAPI and LangGraph.
Provides JSON-driven workflow specification, multi-agent execution, and REST API.

Key Features:
- JSON-driven workflow specification (WorkflowSpec)
- Multi-agent workflow execution via LangGraph runtime
- Extensible node types (Input, Router, LLM, Image, DB, Aggregator)
- Source management (LLM providers, databases, APIs)
- Queue-based rate limiting with bandwidth controls
- REST API for validation, execution, and workflow management

Example:
    >>> from agentflow_core.runtime.builder import build_graph_from_json
    >>> from agentflow_core.runtime.executor import run_workflow
    >>> 
    >>> # Build and execute a workflow
    >>> graph = build_graph_from_json(workflow_spec)
    >>> result = run_workflow(graph, initial_state)
"""

__version__ = "0.1.0"
__author__ = "AgentFlow Team"
__email__ = "team@agentflow.dev"

# Re-export key components for easy access
from agentflow_core.api.models.workflow_model import (
    EdgeModel,
    ExecuteRequest,
    ExecuteResponse,
    NodeModel,
    QueueBandwidthModel,
    QueueModel,
    SourceModel,
    ValidationResult,
    WorkflowSpecModel,
)
from agentflow_core.runtime.state import GraphState
from agentflow_core.utils.error_handler import (
    AgentFlowError,
    NodeExecutionError,
    SourceNotFoundError,
    ValidationError,
    WorkflowExecutionError,
)
from agentflow_core.utils.logger import get_logger, setup_logging

__all__ = [
    # Version info
    "__version__",
    "__author__",
    "__email__",
    # Models
    "WorkflowSpecModel",
    "NodeModel",
    "EdgeModel",
    "QueueModel",
    "QueueBandwidthModel",
    "SourceModel",
    "ExecuteRequest",
    "ExecuteResponse",
    "ValidationResult",
    # State
    "GraphState",
    # Errors
    "AgentFlowError",
    "ValidationError",
    "WorkflowExecutionError",
    "NodeExecutionError",
    "SourceNotFoundError",
    # Logging
    "get_logger",
    "setup_logging",
]
