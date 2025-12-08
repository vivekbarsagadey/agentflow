"""
AgentFlow Core - Health Check Routes

Health and readiness endpoints for monitoring.
"""

from datetime import datetime
from typing import Any, Dict

from fastapi import APIRouter, status

from agentflow_core.utils.logger import get_logger

logger = get_logger(__name__)

# Create router
router = APIRouter(tags=["health"])


# =============================================================================
# Health Endpoints
# =============================================================================


@router.get(
    "/health",
    status_code=status.HTTP_200_OK,
    summary="Health check",
    description="Returns the health status of the service.",
)
async def health_check() -> Dict[str, Any]:
    """
    Basic health check endpoint.
    
    Returns:
        Health status with timestamp
    """
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "service": "agentflow-core"
    }


@router.get(
    "/health/live",
    status_code=status.HTTP_200_OK,
    summary="Liveness probe",
    description="Kubernetes liveness probe - returns 200 if the service is alive.",
)
async def liveness_probe() -> Dict[str, str]:
    """
    Kubernetes liveness probe.
    
    Returns:
        Simple ok status
    """
    return {"status": "alive"}


@router.get(
    "/health/ready",
    status_code=status.HTTP_200_OK,
    summary="Readiness probe",
    description="Kubernetes readiness probe - returns 200 if the service is ready to accept traffic.",
)
async def readiness_probe() -> Dict[str, Any]:
    """
    Kubernetes readiness probe.
    
    Checks if all dependencies are available.
    
    Returns:
        Readiness status with dependency checks
    """
    checks = {
        "langgraph": _check_langgraph(),
        "runtime_registry": _check_registry(),
    }
    
    all_ready = all(checks.values())
    
    return {
        "status": "ready" if all_ready else "not_ready",
        "checks": checks,
        "timestamp": datetime.utcnow().isoformat()
    }


@router.get(
    "/",
    status_code=status.HTTP_200_OK,
    summary="Root endpoint",
    description="Returns basic service information.",
)
async def root() -> Dict[str, Any]:
    """
    Root endpoint with service information.
    
    Returns:
        Service name and version
    """
    return {
        "service": "AgentFlow Core",
        "version": "1.0.0",
        "description": "Multi-Agent Workflow Orchestration Engine",
        "docs": "/docs",
        "health": "/health"
    }


# =============================================================================
# Dependency Checks
# =============================================================================


def _check_langgraph() -> bool:
    """Check if LangGraph is available."""
    try:
        from langgraph.graph import StateGraph
        return True
    except ImportError:
        return False


def _check_registry() -> bool:
    """Check if runtime registry is functioning."""
    try:
        from agentflow_core.runtime.registry import get_all_sources
        get_all_sources()
        return True
    except Exception:
        return False


def _check_gemini() -> bool:
    """Check if Gemini is configured."""
    import os
    return bool(os.getenv("GEMINI_API_KEY"))
