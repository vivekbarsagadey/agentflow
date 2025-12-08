"""
AgentFlow Core - Main Entry Point

This module serves as the main entry point for the AgentFlow Core application.
It exports the FastAPI application instance for use with ASGI servers.
"""

import os
import sys

# Ensure the package is importable
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agentflow_core.api.main import app, create_app

# Export the app for uvicorn
__all__ = ["app", "create_app"]


def main():
    """
    Main entry point for development server.
    
    Run with: python -m agentflow_core.main
    Or: uvicorn agentflow_core.main:app --reload
    """
    import uvicorn
    
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", "8000"))
    reload = os.getenv("ENVIRONMENT", "development") == "development"
    
    print(f"Starting AgentFlow Core on http://{host}:{port}")
    print(f"API Documentation: http://{host}:{port}/docs")
    print(f"OpenAPI Schema: http://{host}:{port}/openapi.json")
    
    uvicorn.run(
        "agentflow_core.main:app",
        host=host,
        port=port,
        reload=reload,
        log_level="info"
    )


if __name__ == "__main__":
    main()
