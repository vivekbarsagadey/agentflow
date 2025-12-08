"""
AgentFlow Core - HTTP API Source Adapter

Adapter for generic HTTP API calls.
Provides a unified interface for external API operations.
"""

import os
from typing import Any, Dict, List, Literal, Optional

from agentflow_core.utils.error_handler import SourceConnectionError
from agentflow_core.utils.logger import get_logger

logger = get_logger(__name__)


# =============================================================================
# Constants
# =============================================================================

DEFAULT_TIMEOUT = 30
DEFAULT_RETRIES = 3
SUPPORTED_METHODS = ["GET", "POST", "PUT", "PATCH", "DELETE"]


# =============================================================================
# HTTP Client Factory
# =============================================================================


def create_http_client(config: Dict[str, Any]) -> Any:
    """
    Create an HTTP client from configuration.
    
    Args:
        config: Source configuration dictionary
            - base_url: Base URL for API
            - headers: Default headers
            - auth_type: Authentication type (api_key, bearer, basic)
            - api_key_env: Environment variable for API key
            - timeout: Request timeout
            - retries: Number of retries
    
    Returns:
        Configured httpx client or client config
        
    Raises:
        SourceConnectionError: If client creation fails
    """
    try:
        import httpx
    except ImportError:
        raise SourceConnectionError(
            message="httpx package not installed. Run: pip install httpx",
            source_id="http",
            source_kind="api"
        )
    
    base_url = config.get("base_url", "")
    timeout = config.get("timeout", DEFAULT_TIMEOUT)
    
    # Build headers
    headers = dict(config.get("headers", {}))
    
    # Add authentication
    auth_type = config.get("auth_type")
    if auth_type == "api_key":
        api_key_env = config.get("api_key_env", "API_KEY")
        api_key = os.getenv(api_key_env) or config.get("api_key")
        if api_key:
            header_name = config.get("api_key_header", "X-API-Key")
            headers[header_name] = api_key
    elif auth_type == "bearer":
        token_env = config.get("token_env", "API_TOKEN")
        token = os.getenv(token_env) or config.get("token")
        if token:
            headers["Authorization"] = f"Bearer {token}"
    
    # Create client
    client = httpx.Client(
        base_url=base_url,
        headers=headers,
        timeout=timeout,
    )
    
    logger.info(
        "http_client_created",
        base_url=base_url,
        auth_type=auth_type
    )
    
    return {
        "client": client,
        "config": config,
    }


def get_http_client(config: Dict[str, Any]) -> Any:
    """Alias for create_http_client."""
    return create_http_client(config)


# =============================================================================
# Request Execution
# =============================================================================


def make_request(
    client_wrapper: Dict[str, Any],
    method: Literal["GET", "POST", "PUT", "PATCH", "DELETE"],
    url: str,
    data: Optional[Dict[str, Any]] = None,
    params: Optional[Dict[str, Any]] = None,
    headers: Optional[Dict[str, str]] = None,
    **kwargs: Any
) -> Dict[str, Any]:
    """
    Make an HTTP request.
    
    Args:
        client_wrapper: Client wrapper from create_http_client
        method: HTTP method
        url: URL path (relative to base_url or absolute)
        data: Request body (JSON)
        params: Query parameters
        headers: Additional headers
        **kwargs: Additional request options
        
    Returns:
        Dictionary with:
            - status_code: HTTP status code
            - data: Response data (JSON or text)
            - headers: Response headers
            - success: True if 2xx status
    """
    client = client_wrapper["client"]
    config = client_wrapper["config"]
    retries = config.get("retries", DEFAULT_RETRIES)
    
    # Merge headers
    request_headers = dict(headers or {})
    
    last_error = None
    for attempt in range(retries):
        try:
            response = client.request(
                method=method.upper(),
                url=url,
                json=data if data else None,
                params=params,
                headers=request_headers,
                **kwargs
            )
            
            # Parse response
            try:
                response_data = response.json()
            except Exception:
                response_data = response.text
            
            result = {
                "status_code": response.status_code,
                "data": response_data,
                "headers": dict(response.headers),
                "success": 200 <= response.status_code < 300,
            }
            
            logger.info(
                "http_request_completed",
                method=method,
                url=url,
                status_code=response.status_code,
                attempt=attempt + 1
            )
            
            return result
            
        except Exception as e:
            last_error = e
            logger.warning(
                "http_request_failed",
                method=method,
                url=url,
                attempt=attempt + 1,
                error=str(e)
            )
            
            if attempt < retries - 1:
                import time
                time.sleep(2 ** attempt)  # Exponential backoff
    
    # All retries failed
    raise SourceConnectionError(
        message=f"HTTP request failed after {retries} attempts: {str(last_error)}",
        source_id="http",
        source_kind="api"
    )


# =============================================================================
# Convenience Methods
# =============================================================================


def get(
    client_wrapper: Dict[str, Any],
    url: str,
    params: Optional[Dict[str, Any]] = None,
    **kwargs: Any
) -> Dict[str, Any]:
    """Make a GET request."""
    return make_request(client_wrapper, "GET", url, params=params, **kwargs)


def post(
    client_wrapper: Dict[str, Any],
    url: str,
    data: Optional[Dict[str, Any]] = None,
    **kwargs: Any
) -> Dict[str, Any]:
    """Make a POST request."""
    return make_request(client_wrapper, "POST", url, data=data, **kwargs)


def put(
    client_wrapper: Dict[str, Any],
    url: str,
    data: Optional[Dict[str, Any]] = None,
    **kwargs: Any
) -> Dict[str, Any]:
    """Make a PUT request."""
    return make_request(client_wrapper, "PUT", url, data=data, **kwargs)


def delete(
    client_wrapper: Dict[str, Any],
    url: str,
    **kwargs: Any
) -> Dict[str, Any]:
    """Make a DELETE request."""
    return make_request(client_wrapper, "DELETE", url, **kwargs)


# =============================================================================
# Utility Functions
# =============================================================================


def close_client(client_wrapper: Dict[str, Any]) -> None:
    """
    Close the HTTP client.
    
    Args:
        client_wrapper: Client wrapper
    """
    client = client_wrapper.get("client")
    if client:
        client.close()
        logger.info("http_client_closed")
