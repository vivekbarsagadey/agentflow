"""
AgentFlow Core - FastAPI Application

Main FastAPI application with all routers and middleware configured.
"""

# Load environment variables from .env file
import os
from pathlib import Path
from dotenv import load_dotenv

# Load .env from backend directory (parent of agentflow_core)
env_path = Path(__file__).parent.parent.parent / ".env"
load_dotenv(dotenv_path=env_path)
from contextlib import asynccontextmanager
from datetime import datetime
from typing import Any, Dict

from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from agentflow_core.api.routes import (
    health_router,
    sources_router,
    workflows_router,
)
from agentflow_core.utils.error_handler import AgentFlowError
from agentflow_core.utils.logger import get_logger

logger = get_logger(__name__)

# =============================================================================
# Application Configuration
# =============================================================================

# API Version
API_VERSION = "v1"

# CORS Configuration
CORS_ORIGINS = os.getenv("CORS_ORIGINS", "*").split(",")
CORS_METHODS = ["GET", "POST", "PUT", "DELETE", "OPTIONS"]
CORS_HEADERS = ["*"]


# =============================================================================
# Application Lifecycle
# =============================================================================


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan manager.
    
    Handles startup and shutdown events.
    """
    # Startup
    logger.info(
        "agentflow_core_starting",
        version=API_VERSION,
        environment=os.getenv("ENVIRONMENT", "development")
    )
    
    # Initialize runtime registry
    from agentflow_core.runtime.registry import get_registry
    registry = get_registry()
    logger.info(
        "runtime_registry_initialized",
        registered_sources=len(registry.sources)
    )
    
    yield
    
    # Shutdown
    logger.info("agentflow_core_shutting_down")


# =============================================================================
# Application Factory
# =============================================================================


def create_app() -> FastAPI:
    """
    Create and configure the FastAPI application.
    
    Returns:
        Configured FastAPI application instance
    """
    app = FastAPI(
        title="AgentFlow Core",
        description=(
            "JSON-driven workflow orchestration engine for multi-agent systems. "
            "AgentFlow Core provides visual workflow design, LangGraph-based execution, "
            "and configurable node types for LLM, Image, Database, and API integrations."
        ),
        version=API_VERSION,
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url="/openapi.json",
        lifespan=lifespan,
    )
    
    # ==========================================================================
    # Middleware
    # ==========================================================================
    
    # CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=CORS_METHODS,
        allow_headers=CORS_HEADERS,
    )
    
    # ==========================================================================
    # Exception Handlers
    # ==========================================================================
    
    @app.exception_handler(AgentFlowError)
    async def agentflow_error_handler(
        request: Request,
        exc: AgentFlowError
    ) -> JSONResponse:
        """Handle AgentFlow custom exceptions."""
        logger.error(
            "agentflow_error",
            error_type=type(exc).__name__,
            message=str(exc),
            path=request.url.path
        )
        
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={
                "error": {
                    "type": type(exc).__name__,
                    "message": str(exc),
                    "timestamp": datetime.utcnow().isoformat()
                }
            }
        )
    
    @app.exception_handler(Exception)
    async def general_exception_handler(
        request: Request,
        exc: Exception
    ) -> JSONResponse:
        """Handle unexpected exceptions."""
        logger.exception(
            "unexpected_error",
            error_type=type(exc).__name__,
            message=str(exc),
            path=request.url.path
        )
        
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "error": {
                    "type": "InternalServerError",
                    "message": "An unexpected error occurred",
                    "timestamp": datetime.utcnow().isoformat()
                }
            }
        )
    
    # ==========================================================================
    # Routers
    # ==========================================================================
    
    # Health routes (no prefix)
    app.include_router(health_router)
    
    # API v1 routes
    app.include_router(
        workflows_router,
        prefix=f"/api/{API_VERSION}"
    )
    app.include_router(
        sources_router,
        prefix=f"/api/{API_VERSION}"
    )
    
    logger.info(
        "routers_registered",
        routes=["health", "workflows", "sources"]
    )
    
    return app


# =============================================================================
# Application Instance
# =============================================================================

# Create the application instance
app = create_app()


# =============================================================================
# Development Server
# =============================================================================

if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "agentflow_core.api.main:app",
        host=os.getenv("HOST", "0.0.0.0"),
        port=int(os.getenv("PORT", "8000")),
        reload=os.getenv("ENVIRONMENT", "development") == "development",
        log_level="info"
    )
