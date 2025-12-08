"""
AgentFlow Core - Database Node

Database node that executes read-only queries against databases.
Supports PostgreSQL (primary) and other databases.
"""

import os
import re
from typing import Any, Dict, List, Optional

from agentflow_core.nodes.base_node import (
    NodeCallable,
    create_node_wrapper,
    get_metadata_value,
    interpolate_template,
)
from agentflow_core.runtime.registry import get_source, has_source
from agentflow_core.runtime.state import GraphState, merge_state
from agentflow_core.utils.error_handler import NodeExecutionError
from agentflow_core.utils.logger import get_logger

logger = get_logger(__name__)


# =============================================================================
# Constants
# =============================================================================

# SQL keywords that indicate write operations (blocked)
WRITE_KEYWORDS = {
    "INSERT", "UPDATE", "DELETE", "DROP", "CREATE", "ALTER",
    "TRUNCATE", "REPLACE", "MERGE", "GRANT", "REVOKE", "EXECUTE",
}


# =============================================================================
# Database Node Factory
# =============================================================================


def create_db_node(
    node_id: str,
    metadata: Optional[Dict[str, Any]] = None
) -> NodeCallable:
    """
    Create a database node that executes read-only queries.
    
    The database node executes SQL queries against configured databases.
    Only SELECT queries are allowed for safety.
    
    Args:
        node_id: Unique identifier for this node
        metadata: Configuration options:
            - source_id: ID of the database source to use
            - query: Static SQL query
            - query_template: Query template with {placeholders}
            - params: Query parameters dictionary
            - output_key: State key for output (default: "db_result")
            - limit: Max rows to return (default: 100)
            - timeout: Query timeout in seconds (default: 30)
    
    Returns:
        A callable that performs database queries
        
    Example:
        >>> node = create_db_node("db_1", {
        ...     "source_id": "postgres-main",
        ...     "query_template": "SELECT * FROM users WHERE name LIKE '%{user_input}%'",
        ...     "limit": 10
        ... })
    """
    _metadata = metadata or {}
    
    def execute(state: GraphState, meta: Dict[str, Any]) -> GraphState:
        """Execute database node logic."""
        source_id = get_metadata_value(meta, "source_id")
        query = get_metadata_value(meta, "query")
        query_template = get_metadata_value(meta, "query_template")
        params = get_metadata_value(meta, "params", {})
        output_key = get_metadata_value(meta, "output_key", "db_result")
        limit = get_metadata_value(meta, "limit", 100)
        timeout = get_metadata_value(meta, "timeout", 30)
        
        # Build query from template or static query
        if query_template:
            final_query = interpolate_template(query_template, state)
        elif query:
            final_query = query
        else:
            raise NodeExecutionError(
                message="No query provided for database node",
                node_id=node_id,
                node_type="db"
            )
        
        # Validate query is read-only
        if not _is_read_only_query(final_query):
            raise NodeExecutionError(
                message="Only SELECT queries are allowed. Write operations are blocked.",
                node_id=node_id,
                node_type="db"
            )
        
        # Add LIMIT if not present
        if limit and "LIMIT" not in final_query.upper():
            final_query = f"{final_query.rstrip(';')} LIMIT {limit}"
        
        # Get source configuration
        source_config = _get_db_source_config(source_id, meta)
        
        # Execute query
        results = _execute_query(
            source_config=source_config,
            query=final_query,
            params=params,
            timeout=timeout,
            node_id=node_id
        )
        
        logger.info(
            "db_node_completed",
            node_id=node_id,
            row_count=len(results)
        )
        
        # Update state
        return merge_state(state, {output_key: results})
    
    return create_node_wrapper(node_id, "db", execute, _metadata)


# =============================================================================
# Query Validation
# =============================================================================


def _is_read_only_query(query: str) -> bool:
    """
    Check if a query is read-only (SELECT only).
    
    Args:
        query: SQL query string
        
    Returns:
        True if query is read-only, False otherwise
    """
    # Normalize query
    normalized = query.upper().strip()
    
    # Remove comments
    normalized = re.sub(r"--.*$", "", normalized, flags=re.MULTILINE)
    normalized = re.sub(r"/\*.*?\*/", "", normalized, flags=re.DOTALL)
    
    # Check for write keywords
    words = set(re.findall(r"\b\w+\b", normalized))
    
    for keyword in WRITE_KEYWORDS:
        if keyword in words:
            logger.warning(
                "write_operation_blocked",
                keyword=keyword,
                query_preview=query[:100]
            )
            return False
    
    # Must start with SELECT, WITH, or EXPLAIN
    first_word = normalized.split()[0] if normalized.split() else ""
    if first_word not in ("SELECT", "WITH", "EXPLAIN"):
        logger.warning(
            "non_select_query_blocked",
            first_word=first_word
        )
        return False
    
    return True


# =============================================================================
# Database Source Configuration
# =============================================================================


def _get_db_source_config(
    source_id: Optional[str],
    metadata: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Get database source configuration.
    """
    # Try to get registered source
    if source_id and has_source(source_id):
        source = get_source(source_id)
        return source.get("config", {})
    
    # Check for inline configuration
    if metadata.get("connection_string_env") or metadata.get("connection_string"):
        return {
            "connection_string_env": metadata.get("connection_string_env", "DATABASE_URL"),
            "connection_string": metadata.get("connection_string"),
            "provider": metadata.get("provider", "postgresql"),
        }
    
    # Default to PostgreSQL from environment
    return {
        "connection_string_env": "DATABASE_URL",
        "provider": "postgresql",
    }


# =============================================================================
# Query Execution
# =============================================================================


def _execute_query(
    source_config: Dict[str, Any],
    query: str,
    params: Dict[str, Any],
    timeout: int,
    node_id: str
) -> List[Dict[str, Any]]:
    """
    Execute a database query and return results.
    
    Returns:
        List of dictionaries representing rows
    """
    provider = source_config.get("provider", "postgresql")
    
    if provider in ("postgresql", "postgres"):
        return _execute_postgresql(
            source_config=source_config,
            query=query,
            params=params,
            timeout=timeout,
            node_id=node_id
        )
    else:
        raise NodeExecutionError(
            message=f"Unsupported database provider: {provider}",
            node_id=node_id,
            node_type="db"
        )


def _execute_postgresql(
    source_config: Dict[str, Any],
    query: str,
    params: Dict[str, Any],
    timeout: int,
    node_id: str
) -> List[Dict[str, Any]]:
    """
    Execute query against PostgreSQL.
    
    Returns:
        List of dictionaries representing rows
    """
    # Get connection string
    connection_string = source_config.get("connection_string")
    if not connection_string:
        env_var = source_config.get("connection_string_env", "DATABASE_URL")
        connection_string = os.getenv(env_var)
    
    if not connection_string:
        logger.warning(
            "database_connection_not_configured",
            returning_empty=True
        )
        return []
    
    try:
        import psycopg
    except ImportError:
        raise NodeExecutionError(
            message="psycopg package not installed. Run: pip install psycopg[binary]",
            node_id=node_id,
            node_type="db"
        )
    
    try:
        # Connect and execute
        with psycopg.connect(connection_string) as conn:
            conn.execute(f"SET statement_timeout = {timeout * 1000}")
            
            with conn.cursor() as cursor:
                # Execute with parameters if provided
                if params:
                    cursor.execute(query, params)
                else:
                    cursor.execute(query)
                
                # Fetch results
                if cursor.description:
                    columns = [desc[0] for desc in cursor.description]
                    rows = cursor.fetchall()
                    
                    # Convert to list of dicts
                    results = [
                        dict(zip(columns, row))
                        for row in rows
                    ]
                    
                    logger.info(
                        "postgresql_query_success",
                        row_count=len(results),
                        column_count=len(columns)
                    )
                    
                    return results
                
                return []
                
    except Exception as e:
        logger.error(
            "postgresql_query_failed",
            error=str(e),
            query_preview=query[:100]
        )
        raise NodeExecutionError(
            message=f"Database query failed: {str(e)}",
            node_id=node_id,
            node_type="db",
            original_error=e
        )
