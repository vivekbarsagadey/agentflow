"""
AgentFlow Core - PostgreSQL Database Source Adapter

Adapter for PostgreSQL database connections and queries.
Provides a unified interface for database operations.
"""

import os
from contextlib import contextmanager
from typing import Any, Dict, Generator, List, Optional

from agentflow_core.utils.error_handler import SourceConnectionError
from agentflow_core.utils.logger import get_logger

logger = get_logger(__name__)


# =============================================================================
# Constants
# =============================================================================

DEFAULT_POOL_SIZE = 5
DEFAULT_MAX_OVERFLOW = 10
DEFAULT_POOL_TIMEOUT = 30
DEFAULT_QUERY_TIMEOUT = 30


# =============================================================================
# Database Client Factory
# =============================================================================


def create_postgres_client(config: Dict[str, Any]) -> Any:
    """
    Create a PostgreSQL connection pool from configuration.
    
    Args:
        config: Source configuration dictionary
            - connection_string_env: Environment variable name for connection string
            - connection_string: Direct connection string
            - pool_size: Connection pool size
            - max_overflow: Maximum overflow connections
            - pool_timeout: Pool timeout in seconds
    
    Returns:
        Connection pool or connection factory
        
    Raises:
        SourceConnectionError: If client creation fails
    """
    # Get connection string
    connection_string = config.get("connection_string")
    if not connection_string:
        env_var = config.get("connection_string_env", "DATABASE_URL")
        connection_string = os.getenv(env_var)
    
    if not connection_string:
        raise SourceConnectionError(
            message="PostgreSQL connection string not configured",
            source_id="postgres",
            source_kind="db"
        )
    
    # Try to import psycopg
    try:
        import psycopg
        from psycopg_pool import ConnectionPool
    except ImportError:
        # Fall back to basic connection if pool not available
        try:
            import psycopg
            
            logger.info("postgres_client_created_basic")
            
            # Return a connection factory
            return {
                "type": "factory",
                "connection_string": connection_string,
                "config": config,
            }
        except ImportError:
            raise SourceConnectionError(
                message="psycopg package not installed. Run: pip install psycopg[binary]",
                source_id="postgres",
                source_kind="db"
            )
    
    # Create connection pool
    pool_size = config.get("pool_size", DEFAULT_POOL_SIZE)
    max_overflow = config.get("max_overflow", DEFAULT_MAX_OVERFLOW)
    pool_timeout = config.get("pool_timeout", DEFAULT_POOL_TIMEOUT)
    
    try:
        pool = ConnectionPool(
            connection_string,
            min_size=1,
            max_size=pool_size + max_overflow,
            timeout=pool_timeout,
        )
        
        logger.info(
            "postgres_pool_created",
            pool_size=pool_size,
            max_overflow=max_overflow
        )
        
        return {
            "type": "pool",
            "pool": pool,
            "config": config,
        }
        
    except Exception as e:
        raise SourceConnectionError(
            message=f"Failed to create PostgreSQL pool: {str(e)}",
            source_id="postgres",
            source_kind="db"
        )


def get_postgres_client(config: Dict[str, Any]) -> Any:
    """Alias for create_postgres_client."""
    return create_postgres_client(config)


# =============================================================================
# Connection Management
# =============================================================================


@contextmanager
def get_connection(client: Dict[str, Any]) -> Generator[Any, None, None]:
    """
    Get a database connection from the client.
    
    Args:
        client: Client dictionary from create_postgres_client
        
    Yields:
        Database connection
    """
    import psycopg
    
    client_type = client.get("type", "factory")
    
    if client_type == "pool":
        pool = client["pool"]
        with pool.connection() as conn:
            yield conn
    else:
        # Factory mode - create new connection
        connection_string = client["connection_string"]
        with psycopg.connect(connection_string) as conn:
            yield conn


# =============================================================================
# Query Execution
# =============================================================================


def execute_query(
    client: Dict[str, Any],
    query: str,
    params: Optional[Dict[str, Any]] = None,
    timeout: int = DEFAULT_QUERY_TIMEOUT,
    fetch_all: bool = True
) -> List[Dict[str, Any]]:
    """
    Execute a query and return results.
    
    Args:
        client: Client dictionary from create_postgres_client
        query: SQL query to execute
        params: Query parameters
        timeout: Query timeout in seconds
        fetch_all: If True, fetch all results
        
    Returns:
        List of dictionaries representing rows
        
    Raises:
        SourceConnectionError: If query execution fails
    """
    try:
        with get_connection(client) as conn:
            # Set timeout
            conn.execute(f"SET statement_timeout = {timeout * 1000}")
            
            with conn.cursor() as cursor:
                # Execute query
                if params:
                    cursor.execute(query, params)
                else:
                    cursor.execute(query)
                
                # Fetch results
                if not cursor.description:
                    return []
                
                columns = [desc[0] for desc in cursor.description]
                
                if fetch_all:
                    rows = cursor.fetchall()
                else:
                    rows = [cursor.fetchone()] if cursor.fetchone() else []
                
                results = [
                    dict(zip(columns, row))
                    for row in rows
                    if row is not None
                ]
                
                logger.info(
                    "postgres_query_executed",
                    row_count=len(results),
                    column_count=len(columns)
                )
                
                return results
                
    except Exception as e:
        logger.error(
            "postgres_query_failed",
            error=str(e),
            query_preview=query[:100]
        )
        raise SourceConnectionError(
            message=f"PostgreSQL query failed: {str(e)}",
            source_id="postgres",
            source_kind="db"
        )


def execute_many(
    client: Dict[str, Any],
    query: str,
    params_list: List[Dict[str, Any]],
    timeout: int = DEFAULT_QUERY_TIMEOUT
) -> int:
    """
    Execute a query multiple times with different parameters.
    
    Args:
        client: Client dictionary
        query: SQL query to execute
        params_list: List of parameter dictionaries
        timeout: Query timeout
        
    Returns:
        Number of rows affected
    """
    try:
        with get_connection(client) as conn:
            conn.execute(f"SET statement_timeout = {timeout * 1000}")
            
            total_affected = 0
            with conn.cursor() as cursor:
                for params in params_list:
                    cursor.execute(query, params)
                    total_affected += cursor.rowcount or 0
                
                conn.commit()
            
            return total_affected
            
    except Exception as e:
        raise SourceConnectionError(
            message=f"PostgreSQL execute_many failed: {str(e)}",
            source_id="postgres",
            source_kind="db"
        )


# =============================================================================
# Utility Functions
# =============================================================================


def test_connection(client: Dict[str, Any]) -> bool:
    """
    Test if the database connection is working.
    
    Args:
        client: Client dictionary
        
    Returns:
        True if connection is working
    """
    try:
        result = execute_query(client, "SELECT 1 as test", timeout=5)
        return len(result) == 1 and result[0].get("test") == 1
    except Exception as e:
        logger.warning("postgres_connection_test_failed", error=str(e))
        return False


def get_tables(client: Dict[str, Any], schema: str = "public") -> List[str]:
    """
    Get list of tables in the database.
    
    Args:
        client: Client dictionary
        schema: Schema name
        
    Returns:
        List of table names
    """
    query = """
        SELECT table_name
        FROM information_schema.tables
        WHERE table_schema = %s
        AND table_type = 'BASE TABLE'
        ORDER BY table_name
    """
    
    results = execute_query(client, query, {"schema": schema})
    return [r["table_name"] for r in results]


def close_client(client: Dict[str, Any]) -> None:
    """
    Close the database client/pool.
    
    Args:
        client: Client dictionary
    """
    if client.get("type") == "pool":
        pool = client.get("pool")
        if pool:
            pool.close()
            logger.info("postgres_pool_closed")
