"""
AgentFlow Core - Sources API Routes

REST API endpoints for source configuration management.
"""

from typing import Any, Dict, List

from fastapi import APIRouter, HTTPException, status

from agentflow_core.api.models.workflow_model import SourceModel
from agentflow_core.runtime.registry import (
    clear_registry,
    get_all_sources,
    get_source,
    register_source,
    unregister_source,
)
from agentflow_core.sources import SOURCE_FACTORIES, create_source_client
from agentflow_core.utils.logger import get_logger

logger = get_logger(__name__)

# Create router
router = APIRouter(prefix="/sources", tags=["sources"])


# =============================================================================
# Source Management Endpoints
# =============================================================================


@router.get(
    "/",
    summary="List registered sources",
    description="Returns a list of all registered source configurations.",
)
async def list_sources() -> Dict[str, Any]:
    """
    List all registered sources.
    
    Returns:
        Dictionary with source IDs and their configurations
    """
    sources = get_all_sources()
    
    # Mask sensitive data
    masked_sources = {}
    for source_id, config in sources.items():
        masked_sources[source_id] = _mask_sensitive_config(config)
    
    return {
        "sources": masked_sources,
        "count": len(masked_sources)
    }


@router.get(
    "/{source_id}",
    summary="Get source configuration",
    description="Returns the configuration for a specific source.",
)
async def get_source_config(source_id: str) -> Dict[str, Any]:
    """
    Get a specific source configuration.
    
    Args:
        source_id: The source identifier
        
    Returns:
        Source configuration (with sensitive data masked)
    """
    try:
        config = get_source(source_id)
        return _mask_sensitive_config(config)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"message": str(e)}
        )


@router.post(
    "/",
    status_code=status.HTTP_201_CREATED,
    summary="Register a source",
    description="Registers a new source configuration.",
)
async def register_source_endpoint(source: SourceModel) -> Dict[str, Any]:
    """
    Register a new source configuration.
    
    Args:
        source: Source configuration
        
    Returns:
        Registration confirmation
    """
    try:
        # Register in the registry
        register_source(source.id, source.model_dump())
        
        logger.info("source_registered", source_id=source.id, kind=source.kind)
        
        return {
            "status": "registered",
            "source_id": source.id,
            "kind": source.kind
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"message": f"Failed to register source: {str(e)}"}
        )


@router.delete(
    "/{source_id}",
    summary="Unregister a source",
    description="Removes a source configuration from the registry.",
)
async def unregister_source_endpoint(source_id: str) -> Dict[str, Any]:
    """
    Unregister a source configuration.
    
    Args:
        source_id: The source identifier to remove
        
    Returns:
        Confirmation message
    """
    try:
        unregister_source(source_id)
        
        logger.info("source_unregistered", source_id=source_id)
        
        return {
            "status": "unregistered",
            "source_id": source_id
        }
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"message": str(e)}
        )


@router.post(
    "/{source_id}/test",
    summary="Test source connection",
    description="Tests the connection to a registered source.",
)
async def test_source_connection(source_id: str) -> Dict[str, Any]:
    """
    Test connection to a source.
    
    Args:
        source_id: The source identifier to test
        
    Returns:
        Connection test result
    """
    try:
        config = get_source(source_id)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"message": str(e)}
        )
    
    kind = config.get("kind", "unknown")
    
    try:
        # Attempt to create client
        client = create_source_client(kind, config.get("config", config))
        
        # Test based on source type
        if kind in ("db", "postgres", "postgresql"):
            from agentflow_core.sources import test_postgres_connection
            success = test_postgres_connection(client)
        else:
            # For other types, client creation success is enough
            success = True
        
        return {
            "source_id": source_id,
            "kind": kind,
            "connected": success,
            "message": "Connection successful" if success else "Connection test failed"
        }
        
    except Exception as e:
        return {
            "source_id": source_id,
            "kind": kind,
            "connected": False,
            "message": f"Connection failed: {str(e)}"
        }


@router.delete(
    "/",
    summary="Clear all sources",
    description="Removes all source configurations from the registry.",
)
async def clear_all_sources() -> Dict[str, Any]:
    """
    Clear all registered sources.
    
    Returns:
        Confirmation message
    """
    clear_registry()
    
    logger.info("all_sources_cleared")
    
    return {
        "status": "cleared",
        "message": "All sources have been unregistered"
    }


# =============================================================================
# Source Type Endpoints
# =============================================================================


@router.get(
    "/types/available",
    summary="Get available source types",
    description="Returns a list of all available source types that can be configured.",
)
async def get_available_source_types() -> Dict[str, Any]:
    """
    Get available source types.
    
    Returns:
        List of available source types with descriptions
    """
    types = {
        "llm": {
            "name": "Gemini LLM",
            "description": "Google Gemini language model for text generation",
            "required_config": ["api_key_env"],
            "optional_config": ["model", "temperature", "max_tokens"]
        },
        "image": {
            "name": "Gemini Image",
            "description": "Google Imagen for image generation",
            "required_config": ["api_key_env"],
            "optional_config": ["size", "quality"]
        },
        "db": {
            "name": "PostgreSQL Database",
            "description": "PostgreSQL database for data queries",
            "required_config": ["connection_string_env"],
            "optional_config": ["pool_size", "timeout"]
        },
        "api": {
            "name": "HTTP API",
            "description": "Generic HTTP API client",
            "required_config": ["base_url"],
            "optional_config": ["headers", "auth_type", "timeout"]
        }
    }
    
    return {
        "types": types,
        "count": len(types)
    }


# =============================================================================
# Utility Functions
# =============================================================================


def _mask_sensitive_config(config: Dict[str, Any]) -> Dict[str, Any]:
    """
    Mask sensitive configuration values.
    
    Args:
        config: Configuration dictionary
        
    Returns:
        Configuration with sensitive values masked
    """
    sensitive_keys = [
        "api_key", "password", "secret", "token",
        "connection_string", "credentials"
    ]
    
    masked = dict(config)
    
    for key in list(masked.keys()):
        lower_key = key.lower()
        for sensitive in sensitive_keys:
            if sensitive in lower_key:
                masked[key] = "***MASKED***"
                break
    
    # Handle nested config
    if "config" in masked and isinstance(masked["config"], dict):
        masked["config"] = _mask_sensitive_config(masked["config"])
    
    return masked
