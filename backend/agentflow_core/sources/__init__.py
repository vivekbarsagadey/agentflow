"""
AgentFlow Core - Source Adapters

Exports all source adapters for external integrations.
"""

from agentflow_core.sources.llm_gemini import (
    create_gemini_client,
    generate_chat,
    generate_text,
    get_gemini_client,
)
from agentflow_core.sources.image_gemini import (
    create_image_client,
    generate_image,
    get_image_client,
)
from agentflow_core.sources.db_postgres import (
    close_client as close_postgres_client,
    create_postgres_client,
    execute_query,
    get_postgres_client,
    get_tables,
    test_connection as test_postgres_connection,
)
from agentflow_core.sources.api_http import (
    close_client as close_http_client,
    create_http_client,
    delete,
    get,
    get_http_client,
    make_request,
    post,
    put,
)

# Source type to factory mapping
SOURCE_FACTORIES = {
    "llm": create_gemini_client,
    "gemini": create_gemini_client,
    "image": create_image_client,
    "imagen": create_image_client,
    "db": create_postgres_client,
    "postgres": create_postgres_client,
    "postgresql": create_postgres_client,
    "api": create_http_client,
    "http": create_http_client,
}


def create_source_client(kind: str, config: dict) -> any:
    """
    Create a source client of the specified kind.
    
    Args:
        kind: Source kind (llm, image, db, api)
        config: Source configuration
        
    Returns:
        Configured client instance
        
    Raises:
        ValueError: If source kind is not supported
    """
    factory = SOURCE_FACTORIES.get(kind.lower())
    
    if factory is None:
        supported = ", ".join(set(SOURCE_FACTORIES.keys()))
        raise ValueError(
            f"Unsupported source kind: '{kind}'. "
            f"Supported kinds: {supported}"
        )
    
    return factory(config)


__all__ = [
    # Factory
    "create_source_client",
    "SOURCE_FACTORIES",
    # Gemini LLM
    "create_gemini_client",
    "get_gemini_client",
    "generate_text",
    "generate_chat",
    # Gemini Image
    "create_image_client",
    "get_image_client",
    "generate_image",
    # PostgreSQL
    "create_postgres_client",
    "get_postgres_client",
    "execute_query",
    "test_postgres_connection",
    "get_tables",
    "close_postgres_client",
    # HTTP
    "create_http_client",
    "get_http_client",
    "make_request",
    "get",
    "post",
    "put",
    "delete",
    "close_http_client",
]
