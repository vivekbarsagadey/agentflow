```prompt
---
description: Create FastAPI endpoint with router, service, and schema for AgentFlow backend
tools:
  - create_file
  - read_file
  - semantic_search
  - list_code_usages
---

# Create FastAPI Endpoint for AgentFlow

You are creating a new FastAPI endpoint for AgentFlow, a JSON-driven workflow orchestration engine built on LangGraph. Follow the established patterns in the codebase.

## AgentFlow Architecture Context

AgentFlow is a visual workflow orchestration platform with:
- **Backend**: Python 3.11+, FastAPI, LangGraph, Pydantic, PostgreSQL, Redis
- **Core Concepts**: Nodes (input, router, llm, image, db, aggregator), Edges, Queues, Sources
- **Workflow Structure**: WorkflowSpec with nodes[], edges[], queues[], sources[], start_node

## Project Structure

```
backend/agentflow_core/
├── api/
│   ├── main.py              # FastAPI app with CORS, lifespan
│   ├── models/
│   │   └── workflow_model.py # API request/response models
│   └── routes/
│       ├── health.py         # Health check endpoints
│       ├── sources.py        # Source CRUD endpoints
│       └── workflows.py      # Workflow CRUD & execution
├── nodes/                    # Node implementations
├── runtime/                  # LangGraph runtime (builder, executor)
├── sources/                  # External integrations (OpenAI, Postgres)
└── utils/                    # Logging, error handling, ID generation
```

## 1. API Route Template

Create route at `backend/agentflow_core/api/routes/{resource}.py`:

```python
"""
{Resource} API routes for AgentFlow.
"""
from fastapi import APIRouter, HTTPException, status
from typing import List

from agentflow_core.api.models.workflow_model import (
    {Resource}Request,
    {Resource}Response,
)
from agentflow_core.utils.logger import get_logger
from agentflow_core.utils.id_generator import generate_id

logger = get_logger(__name__)
router = APIRouter(prefix="/{resource}", tags=["{Resource}"])


@router.get("", response_model=List[{Resource}Response])
async def list_{resources}() -> List[{Resource}Response]:
    """
    List all {resources}.
    
    Returns:
        List of {resource} objects
    """
    logger.info("Listing {resources}")
    # TODO: Implement retrieval logic
    return []


@router.get("/{{{resource}_id}}", response_model={Resource}Response)
async def get_{resource}({resource}_id: str) -> {Resource}Response:
    """
    Get a specific {resource} by ID.
    
    Args:
        {resource}_id: Unique identifier
        
    Returns:
        {Resource} object
        
    Raises:
        HTTPException: 404 if not found
    """
    logger.info(f"Getting {resource}: {{{resource}_id}}")
    # TODO: Implement retrieval logic
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"{Resource} not found: {{{resource}_id}}"
    )


@router.post("", response_model={Resource}Response, status_code=status.HTTP_201_CREATED)
async def create_{resource}(request: {Resource}Request) -> {Resource}Response:
    """
    Create a new {resource}.
    
    Args:
        request: {Resource} creation request
        
    Returns:
        Created {resource} object
    """
    logger.info(f"Creating {resource}")
    {resource}_id = generate_id("{resource}")
    
    # TODO: Implement creation logic
    return {Resource}Response(
        id={resource}_id,
        **request.model_dump()
    )


@router.put("/{{{resource}_id}}", response_model={Resource}Response)
async def update_{resource}(
    {resource}_id: str,
    request: {Resource}Request
) -> {Resource}Response:
    """
    Update an existing {resource}.
    
    Args:
        {resource}_id: Unique identifier
        request: Updated {resource} data
        
    Returns:
        Updated {resource} object
        
    Raises:
        HTTPException: 404 if not found
    """
    logger.info(f"Updating {resource}: {{{resource}_id}}")
    # TODO: Implement update logic
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"{Resource} not found: {{{resource}_id}}"
    )


@router.delete("/{{{resource}_id}}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_{resource}({resource}_id: str) -> None:
    """
    Delete a {resource}.
    
    Args:
        {resource}_id: Unique identifier
        
    Raises:
        HTTPException: 404 if not found
    """
    logger.info(f"Deleting {resource}: {{{resource}_id}}")
    # TODO: Implement deletion logic
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"{Resource} not found: {{{resource}_id}}"
    )
```

## 2. Pydantic Model Template

Add to `backend/agentflow_core/api/models/workflow_model.py`:

```python
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from datetime import datetime


class {Resource}Request(BaseModel):
    """Request model for creating/updating {resource}."""
    
    name: str = Field(..., description="{Resource} name")
    description: Optional[str] = Field(None, description="{Resource} description")
    config: Dict[str, Any] = Field(default_factory=dict, description="Configuration")
    
    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "name": "example_{resource}",
                    "description": "An example {resource}",
                    "config": {"key": "value"}
                }
            ]
        }
    }


class {Resource}Response(BaseModel):
    """Response model for {resource}."""
    
    id: str = Field(..., description="Unique identifier")
    name: str = Field(..., description="{Resource} name")
    description: Optional[str] = Field(None, description="{Resource} description")
    config: Dict[str, Any] = Field(default_factory=dict, description="Configuration")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
```

## 3. Register Route in Main App

Update `backend/agentflow_core/api/main.py`:

```python
from agentflow_core.api.routes import health, workflows, sources, {resource}

# Register routers
app.include_router(health.router)
app.include_router(workflows.router)
app.include_router(sources.router)
app.include_router({resource}.router)  # Add new router
```

## 4. AgentFlow-Specific Patterns

### Workflow Execution Endpoint

```python
@router.post("/{workflow_id}/execute", response_model=ExecutionResponse)
async def execute_workflow(
    workflow_id: str,
    request: ExecutionRequest
) -> ExecutionResponse:
    """Execute a workflow with the LangGraph runtime."""
    from agentflow_core.runtime.builder import WorkflowBuilder
    from agentflow_core.runtime.executor import WorkflowExecutor
    
    # Load workflow spec
    workflow_spec = await get_workflow(workflow_id)
    
    # Build LangGraph
    builder = WorkflowBuilder(workflow_spec)
    graph = builder.build()
    
    # Execute
    executor = WorkflowExecutor(graph)
    result = await executor.execute(request.input_data)
    
    return ExecutionResponse(
        execution_id=generate_id("exec"),
        workflow_id=workflow_id,
        status="completed",
        result=result
    )
```

### Source Configuration Endpoint

```python
@router.post("/sources", response_model=SourceResponse)
async def create_source(request: SourceRequest) -> SourceResponse:
    """Create a new source (LLM, DB, API integration)."""
    from agentflow_core.sources import get_source_class
    
    # Validate source type
    source_class = get_source_class(request.type)
    if not source_class:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unknown source type: {request.type}"
        )
    
    # Validate configuration
    source = source_class(**request.config)
    await source.validate_connection()
    
    return SourceResponse(
        id=generate_id("src"),
        **request.model_dump()
    )
```

## 5. Testing Endpoint

Create test at `backend/tests/test_{resource}.py`:

```python
import pytest
from fastapi.testclient import TestClient
from agentflow_core.api.main import app

client = TestClient(app)


class Test{Resource}API:
    """Test {resource} API endpoints."""
    
    def test_create_{resource}(self):
        """Test creating a new {resource}."""
        response = client.post(
            "/{resource}",
            json={
                "name": "test_{resource}",
                "description": "Test description",
                "config": {"key": "value"}
            }
        )
        
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "test_{resource}"
        assert data["id"].startswith("{resource}_")
    
    def test_list_{resources}(self):
        """Test listing {resources}."""
        response = client.get("/{resource}")
        
        assert response.status_code == 200
        assert isinstance(response.json(), list)
    
    def test_get_{resource}_not_found(self):
        """Test getting non-existent {resource}."""
        response = client.get("/{resource}/nonexistent")
        
        assert response.status_code == 404
```

## Critical Checklist

- [ ] Route follows RESTful conventions
- [ ] Pydantic models have proper validation
- [ ] Error handling with HTTPException
- [ ] Logging with structured logger
- [ ] ID generation using utility
- [ ] Route registered in main.py
- [ ] Tests cover CRUD operations
- [ ] Docstrings with Args/Returns/Raises
```
