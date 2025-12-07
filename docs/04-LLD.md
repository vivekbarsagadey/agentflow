# Low-Level Design (LLD)

# AgentFlow — Multi-Agent Workflow Orchestration Platform

**Version:** 1.0  
**Date:** December 7, 2025  
**Status:** Approved  
**Audience:** Backend Engineers, Frontend Engineers, QA Engineers, Architects

---

## Table of Contents

1. [Backend architecture](#1-backend-architecture)
2. [Data models](#2-data-models)
3. [Runtime engine](#3-runtime-engine)
4. [Node implementations](#4-node-implementations)
5. [Source adapters](#5-source-adapters)
6. [API layer](#6-api-layer)
7. [Frontend architecture](#7-frontend-architecture)
8. [Component specifications](#8-component-specifications)
9. [State management](#9-state-management)
10. [Error handling](#10-error-handling)
11. [Testing strategy](#11-testing-strategy)

---

## 1. Backend architecture

### 1.1 Technology stack

| Component | Technology | Version |
|-----------|------------|---------|
| Runtime | Python | 3.11+ |
| Web Framework | FastAPI | 0.100+ |
| Workflow Engine | LangGraph | Latest |
| Validation | Pydantic | 2.0+ |
| Async Support | AsyncIO | Built-in |
| Database Driver | psycopg | 3.1+ |
| LLM Integration | OpenAI SDK | 1.0+ |
| HTTP Client | httpx | 0.24+ |
| Rate Limiting | Redis | 7+ |

### 1.2 Project structure

```
backend/agentflow_core/
├── __init__.py
├── api/
│   ├── __init__.py
│   ├── main.py                    # FastAPI app entry point
│   ├── models/
│   │   ├── __init__.py
│   │   └── workflow_model.py      # Pydantic models
│   └── routes/
│       ├── __init__.py
│       ├── workflows.py           # Workflow CRUD + execute
│       ├── sources.py             # Source management
│       └── health.py              # Health checks
├── runtime/
│   ├── __init__.py
│   ├── builder.py                 # JSON → LangGraph
│   ├── executor.py                # Graph execution
│   ├── validator.py               # Validation logic
│   ├── registry.py                # Runtime state
│   ├── rate_limiter.py            # Queue management
│   └── state.py                   # GraphState definition
├── nodes/
│   ├── __init__.py
│   ├── base_node.py               # Base node interface
│   ├── input_node.py
│   ├── router_node.py
│   ├── llm_node.py
│   ├── image_node.py
│   ├── db_node.py
│   └── aggregator_node.py
├── sources/
│   ├── __init__.py
│   ├── llm_openai.py              # OpenAI LLM adapter
│   ├── image_openai.py            # DALL-E adapter
│   ├── db_postgres.py             # PostgreSQL adapter
│   └── api_http.py                # HTTP API adapter
├── schemas/
│   ├── workflow_schema.json
│   ├── node_schema.json
│   └── queue_schema.json
└── utils/
    ├── __init__.py
    ├── logger.py                  # Logging configuration
    ├── error_handler.py           # Error handling
    └── id_generator.py            # ID generation utilities
```

---

## 2. Data models

### 2.1 GraphState model

**File:** `runtime/state.py`

```python
from typing import TypedDict, Any, Optional

class GraphState(TypedDict, total=False):
    """State object passed between nodes during workflow execution."""
    
    # Input data
    user_input: str
    
    # Routing
    intent: str
    
    # Results by node type
    text_result: Optional[str]
    image_result: Optional[Any]
    db_result: Optional[Any]
    
    # Final output
    final_output: Optional[Any]
    
    # Metadata
    tokens_used: int
    cost: float
    execution_time: float
    metadata: dict
    
    # Error tracking
    errors: list
```

### 2.2 WorkflowSpec model

**File:** `api/models/workflow_model.py`

```python
from pydantic import BaseModel, Field
from typing import List, Optional, Any, Dict, Union

class NodeModel(BaseModel):
    """Represents a node in the workflow graph."""
    id: str = Field(..., description="Unique node identifier")
    type: str = Field(..., description="Node type: input, router, llm, image, db, aggregator")
    metadata: Optional[Dict[str, Any]] = Field(default=None, description="Node-specific metadata")

class EdgeModel(BaseModel):
    """Represents a connection between nodes."""
    from_node: str = Field(..., alias="from", description="Source node ID")
    to: Union[str, List[str]] = Field(..., description="Destination node ID(s)")
    condition: Optional[str] = Field(default=None, description="Conditional expression")

class BandwidthModel(BaseModel):
    """Bandwidth configuration for rate limiting."""
    max_messages_per_second: Optional[int] = None
    max_requests_per_minute: Optional[int] = None
    max_tokens_per_minute: Optional[int] = None
    burst_size: Optional[int] = None

class SubQueueModel(BaseModel):
    """Sub-queue with weighted distribution."""
    id: str
    weight: float = Field(ge=0.0, le=1.0)

class QueueModel(BaseModel):
    """Represents a rate-limited queue between nodes."""
    id: str
    from_node: str = Field(..., alias="from")
    to: str
    bandwidth: Optional[BandwidthModel] = None
    sub_queues: Optional[List[SubQueueModel]] = None

class SourceModel(BaseModel):
    """External service configuration."""
    id: str
    kind: str = Field(..., description="Source type: llm, image, db, api")
    config: Dict[str, Any] = Field(..., description="Kind-specific configuration")

class WorkflowSpecModel(BaseModel):
    """Complete workflow specification."""
    nodes: List[NodeModel]
    edges: List[EdgeModel]
    queues: List[QueueModel] = Field(default_factory=list)
    sources: List[SourceModel]
    start_node: str
    
    class Config:
        populate_by_name = True
```

### 2.3 Execution models

```python
class ExecuteRequest(BaseModel):
    """Request to execute a workflow."""
    workflow: WorkflowSpecModel
    initial_state: Dict[str, Any]

class ExecuteResponse(BaseModel):
    """Response from workflow execution."""
    status: str
    execution_id: str
    final_state: Dict[str, Any]
    metrics: Dict[str, Any]

class ValidationError(BaseModel):
    """Validation error details."""
    code: str
    message: str
    field: Optional[str] = None
    node_id: Optional[str] = None

class ValidationResponse(BaseModel):
    """Response from workflow validation."""
    valid: bool
    errors: List[ValidationError]
    warnings: List[str] = Field(default_factory=list)
```

---

## 3. Runtime engine

### 3.1 Validator module

**File:** `runtime/validator.py`

```python
from typing import List, Dict, Set
from agentflow_core.api.models.workflow_model import WorkflowSpecModel, ValidationError

def validate_workflow(spec: WorkflowSpecModel) -> List[ValidationError]:
    """
    Validates a workflow specification.
    
    Performs:
    - Schema validation (via Pydantic)
    - Referential integrity checks
    - Logical consistency checks
    """
    errors = []
    
    # Collect all node IDs
    node_ids = {node.id for node in spec.nodes}
    
    # Validate start node exists
    if spec.start_node not in node_ids:
        errors.append(ValidationError(
            code="E005",
            message=f"Start node '{spec.start_node}' does not exist",
            field="start_node"
        ))
    
    # Validate unique node IDs
    node_id_list = [node.id for node in spec.nodes]
    if len(node_id_list) != len(set(node_id_list)):
        errors.append(ValidationError(
            code="E009",
            message="Duplicate node IDs found",
            field="nodes"
        ))
    
    # Collect source IDs
    source_ids = {source.id for source in spec.sources}
    
    # Validate edges
    for edge in spec.edges:
        if edge.from_node not in node_ids:
            errors.append(ValidationError(
                code="E006",
                message=f"Edge references non-existent source node '{edge.from_node}'",
                field="edges"
            ))
        
        to_nodes = edge.to if isinstance(edge.to, list) else [edge.to]
        for to_node in to_nodes:
            if to_node not in node_ids:
                errors.append(ValidationError(
                    code="E006",
                    message=f"Edge references non-existent destination node '{to_node}'",
                    field="edges"
                ))
    
    # Validate queues
    for queue in spec.queues:
        if queue.from_node not in node_ids:
            errors.append(ValidationError(
                code="E007",
                message=f"Queue '{queue.id}' references non-existent source node '{queue.from_node}'",
                field="queues",
                node_id=queue.id
            ))
        
        if queue.to not in node_ids:
            errors.append(ValidationError(
                code="E007",
                message=f"Queue '{queue.id}' references non-existent destination node '{queue.to}'",
                field="queues",
                node_id=queue.id
            ))
    
    # Validate nodes with sources
    for node in spec.nodes:
        if node.type in ['llm', 'image', 'db']:
            source_id = node.metadata.get('source') if node.metadata else None
            if not source_id:
                errors.append(ValidationError(
                    code="E014",
                    message=f"Node '{node.id}' of type '{node.type}' requires a source",
                    field="nodes",
                    node_id=node.id
                ))
            elif source_id not in source_ids:
                errors.append(ValidationError(
                    code="E008",
                    message=f"Node '{node.id}' references non-existent source '{source_id}'",
                    field="nodes",
                    node_id=node.id
                ))
    
    return errors

def detect_cycles(spec: WorkflowSpecModel) -> bool:
    """Detects cycles in the workflow graph."""
    # Build adjacency list
    graph = {}
    for edge in spec.edges:
        if edge.from_node not in graph:
            graph[edge.from_node] = []
        to_nodes = edge.to if isinstance(edge.to, list) else [edge.to]
        graph[edge.from_node].extend(to_nodes)
    
    # DFS-based cycle detection
    visited = set()
    rec_stack = set()
    
    def has_cycle(node):
        visited.add(node)
        rec_stack.add(node)
        
        for neighbor in graph.get(node, []):
            if neighbor not in visited:
                if has_cycle(neighbor):
                    return True
            elif neighbor in rec_stack:
                return True
        
        rec_stack.remove(node)
        return False
    
    for node_id in graph:
        if node_id not in visited:
            if has_cycle(node_id):
                return True
    
    return False
```

### 3.2 Registry module

**File:** `runtime/registry.py`

```python
from typing import Dict, Any
from agentflow_core.api.models.workflow_model import SourceModel, QueueModel

class WorkflowRegistry:
    """Stores runtime state for workflow execution."""
    
    def __init__(self):
        self.sources: Dict[str, SourceModel] = {}
        self.queues: Dict[str, QueueModel] = {}
        self.node_metadata: Dict[str, Dict[str, Any]] = {}
        self.last_usage: Dict[str, float] = {}
    
    def clear(self):
        """Clears all registry data."""
        self.sources.clear()
        self.queues.clear()
        self.node_metadata.clear()
        self.last_usage.clear()
    
    def register_source(self, source: SourceModel):
        """Registers a source."""
        self.sources[source.id] = source
    
    def register_queue(self, queue: QueueModel):
        """Registers a queue."""
        self.queues[queue.id] = queue
    
    def register_node(self, node_id: str, metadata: Dict[str, Any]):
        """Registers node metadata."""
        self.node_metadata[node_id] = metadata
    
    def get_source(self, source_id: str) -> SourceModel:
        """Retrieves a source by ID."""
        return self.sources.get(source_id)
    
    def get_queue(self, queue_id: str) -> QueueModel:
        """Retrieves a queue by ID."""
        return self.queues.get(queue_id)

# Global registry instance
registry = WorkflowRegistry()
```

### 3.3 Rate limiter module

**File:** `runtime/rate_limiter.py`

```python
import time
from typing import Optional
from agentflow_core.runtime.registry import registry

class RateLimiter:
    """Enforces rate limits based on queue configuration."""
    
    @staticmethod
    def check_rate_limit(queue_id: str):
        """
        Checks and enforces rate limit for a queue.
        Blocks if necessary to comply with bandwidth limits.
        """
        queue = registry.get_queue(queue_id)
        if not queue or not queue.bandwidth:
            return
        
        bw = queue.bandwidth
        now = time.time()
        key = f"{queue_id}_last"
        last_time = registry.last_usage.get(key, 0)
        
        # Check max_messages_per_second
        if bw.max_messages_per_second:
            min_interval = 1.0 / bw.max_messages_per_second
            elapsed = now - last_time
            
            if elapsed < min_interval:
                sleep_time = min_interval - elapsed
                time.sleep(sleep_time)
        
        # Update last usage time
        registry.last_usage[key] = time.time()
    
    @staticmethod
    def check_token_limit(queue_id: str, tokens: int) -> bool:
        """
        Checks if token usage is within limits.
        Returns True if allowed, False otherwise.
        """
        queue = registry.get_queue(queue_id)
        if not queue or not queue.bandwidth:
            return True
        
        bw = queue.bandwidth
        if not bw.max_tokens_per_minute:
            return True
        
        # TODO: Implement sliding window token counting
        return True

rate_limiter = RateLimiter()
```

### 3.4 Builder module

**File:** `runtime/builder.py`

```python
from langgraph.graph import StateGraph, END
from agentflow_core.api.models.workflow_model import WorkflowSpecModel
from agentflow_core.runtime.state import GraphState
from agentflow_core.runtime.registry import registry
from agentflow_core.nodes import (
    create_input_node,
    create_router_node,
    create_llm_node,
    create_image_node,
    create_db_node,
    create_aggregator_node
)

def build_graph_from_json(spec: WorkflowSpecModel) -> StateGraph:
    """
    Converts a WorkflowSpec into a compiled LangGraph.
    
    Steps:
    1. Clear and populate registry
    2. Create StateGraph
    3. Add nodes
    4. Set entry point
    5. Add edges
    6. Compile
    """
    # Clear registry
    registry.clear()
    
    # Register sources
    for source in spec.sources:
        registry.register_source(source)
    
    # Register queues
    for queue in spec.queues:
        registry.register_queue(queue)
    
    # Register node metadata
    for node in spec.nodes:
        registry.register_node(node.id, node.metadata or {})
    
    # Create graph
    graph = StateGraph(GraphState)
    
    # Add nodes
    node_factory = {
        'input': create_input_node,
        'router': create_router_node,
        'llm': create_llm_node,
        'image': create_image_node,
        'db': create_db_node,
        'aggregator': create_aggregator_node
    }
    
    for node in spec.nodes:
        if node.type not in node_factory:
            raise ValueError(f"Unknown node type: {node.type}")
        
        node_func = node_factory[node.type](node.id, node.metadata or {})
        graph.add_node(node.id, node_func)
    
    # Set entry point
    graph.set_entry_point(spec.start_node)
    
    # Add edges
    for edge in spec.edges:
        to_nodes = edge.to if isinstance(edge.to, list) else [edge.to]
        
        if len(to_nodes) == 1:
            graph.add_edge(edge.from_node, to_nodes[0])
        else:
            # Multiple destinations - add edges to all
            for to_node in to_nodes:
                graph.add_edge(edge.from_node, to_node)
    
    # Compile graph
    return graph.compile()
```

### 3.5 Executor module

**File:** `runtime/executor.py`

```python
import time
from typing import Dict, Any
from agentflow_core.api.models.workflow_model import WorkflowSpecModel
from agentflow_core.runtime.state import GraphState
from agentflow_core.runtime.builder import build_graph_from_json
from agentflow_core.runtime.validator import validate_workflow

def run_workflow(spec: WorkflowSpecModel, initial_state: Dict[str, Any]) -> GraphState:
    """
    Executes a workflow and returns the final state.
    
    Args:
        spec: Workflow specification
        initial_state: Initial state dictionary
    
    Returns:
        Final state after execution
    """
    # Validate workflow
    errors = validate_workflow(spec)
    if errors:
        raise ValueError(f"Workflow validation failed: {errors}")
    
    # Build graph
    graph = build_graph_from_json(spec)
    
    # Prepare initial state
    state = GraphState(**initial_state)
    state['metadata'] = state.get('metadata', {})
    state['metadata']['start_time'] = time.time()
    
    # Execute graph
    final_state = graph.invoke(state)
    
    # Add execution metrics
    final_state['metadata']['end_time'] = time.time()
    final_state['metadata']['execution_time'] = (
        final_state['metadata']['end_time'] - 
        final_state['metadata']['start_time']
    )
    
    return final_state
```

---

## 4. Node implementations

### 4.1 Base node interface

**File:** `nodes/base_node.py`

```python
from typing import Callable
from agentflow_core.runtime.state import GraphState

NodeCallable = Callable[[GraphState], GraphState]
```

### 4.2 Input node

**File:** `nodes/input_node.py`

```python
from agentflow_core.runtime.state import GraphState

def create_input_node(node_id: str, metadata: dict):
    """Creates an input node that passes state through unchanged."""
    
    def input_node(state: GraphState) -> GraphState:
        """Input node - entry point for user input."""
        return state
    
    return input_node
```

### 4.3 Router node

**File:** `nodes/router_node.py`

```python
from agentflow_core.runtime.state import GraphState

def create_router_node(node_id: str, metadata: dict):
    """Creates a router node that determines intent."""
    
    def router_node(state: GraphState) -> GraphState:
        """Router node - classifies user intent."""
        user_input = state.get('user_input', '')
        
        # Simple keyword-based routing
        # TODO: Replace with LLM-based classification
        if 'image' in user_input.lower() or 'picture' in user_input.lower():
            state['intent'] = 'image'
        elif 'data' in user_input.lower() or 'query' in user_input.lower():
            state['intent'] = 'database'
        else:
            state['intent'] = 'text'
        
        return state
    
    return router_node
```

### 4.4 LLM node

**File:** `nodes/llm_node.py`

```python
from agentflow_core.runtime.state import GraphState
from agentflow_core.runtime.registry import registry
from agentflow_core.sources.llm_openai import get_llm_client

def create_llm_node(node_id: str, metadata: dict):
    """Creates an LLM node that calls a language model."""
    
    def llm_node(state: GraphState) -> GraphState:
        """LLM node - generates text using language model."""
        # Get source configuration
        source_id = metadata.get('source')
        if not source_id:
            raise ValueError(f"LLM node '{node_id}' missing source")
        
        source = registry.get_source(source_id)
        if not source:
            raise ValueError(f"Source '{source_id}' not found")
        
        # Get LLM client
        llm_client = get_llm_client(source)
        
        # Prepare prompt
        user_input = state.get('user_input', '')
        prompt = metadata.get('prompt', user_input)
        
        # Call LLM
        response = llm_client.chat.completions.create(
            model=source.config.get('model_name', 'gpt-4'),
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": prompt}
            ]
        )
        
        # Store result
        state['text_result'] = response.choices[0].message.content
        state['tokens_used'] = state.get('tokens_used', 0) + response.usage.total_tokens
        
        return state
    
    return llm_node
```

### 4.5 Image node

**File:** `nodes/image_node.py`

```python
from agentflow_core.runtime.state import GraphState
from agentflow_core.runtime.registry import registry
from agentflow_core.sources.image_openai import get_image_client

def create_image_node(node_id: str, metadata: dict):
    """Creates an image generation node."""
    
    def image_node(state: GraphState) -> GraphState:
        """Image node - generates images using AI model."""
        # Get source configuration
        source_id = metadata.get('source')
        if not source_id:
            raise ValueError(f"Image node '{node_id}' missing source")
        
        source = registry.get_source(source_id)
        if not source:
            raise ValueError(f"Source '{source_id}' not found")
        
        # Get image client
        image_client = get_image_client(source)
        
        # Prepare prompt
        user_input = state.get('user_input', '')
        prompt = metadata.get('prompt', user_input)
        
        # Generate image
        response = image_client.images.generate(
            model=source.config.get('model_name', 'dall-e-3'),
            prompt=prompt,
            n=1,
            size="1024x1024"
        )
        
        # Store result
        state['image_result'] = {
            'url': response.data[0].url,
            'prompt': prompt
        }
        
        return state
    
    return image_node
```

### 4.6 Database node

**File:** `nodes/db_node.py`

```python
from agentflow_core.runtime.state import GraphState
from agentflow_core.runtime.registry import registry
from agentflow_core.sources.db_postgres import get_db_connection

def create_db_node(node_id: str, metadata: dict):
    """Creates a database query node."""
    
    def db_node(state: GraphState) -> GraphState:
        """DB node - executes database queries."""
        # Get source configuration
        source_id = metadata.get('source')
        if not source_id:
            raise ValueError(f"DB node '{node_id}' missing source")
        
        source = registry.get_source(source_id)
        if not source:
            raise ValueError(f"Source '{source_id}' not found")
        
        # Get database connection
        conn = get_db_connection(source)
        
        # Get query
        query = metadata.get('query', 'SELECT 1')
        
        # Execute query
        cursor = conn.cursor()
        cursor.execute(query)
        results = cursor.fetchall()
        cursor.close()
        
        # Store result
        state['db_result'] = [dict(row) for row in results]
        
        return state
    
    return db_node
```

### 4.7 Aggregator node

**File:** `nodes/aggregator_node.py`

```python
from agentflow_core.runtime.state import GraphState

def create_aggregator_node(node_id: str, metadata: dict):
    """Creates an aggregator node that combines results."""
    
    def aggregator_node(state: GraphState) -> GraphState:
        """Aggregator node - combines results into final output."""
        final_output = {}
        
        if state.get('text_result'):
            final_output['text'] = state['text_result']
        
        if state.get('image_result'):
            final_output['image'] = state['image_result']
        
        if state.get('db_result'):
            final_output['data'] = state['db_result']
        
        state['final_output'] = final_output
        
        return state
    
    return aggregator_node
```

---

## 5. Source adapters

### 5.1 OpenAI LLM adapter

**File:** `sources/llm_openai.py`

```python
import os
from openai import OpenAI
from agentflow_core.api.models.workflow_model import SourceModel

def get_llm_client(source: SourceModel) -> OpenAI:
    """
    Creates an OpenAI client for LLM calls.
    
    Args:
        source: Source configuration
    
    Returns:
        OpenAI client instance
    """
    api_key_env = source.config.get('api_key_env', 'OPENAI_API_KEY')
    api_key = os.getenv(api_key_env)
    
    if not api_key:
        raise ValueError(f"API key not found in environment variable '{api_key_env}'")
    
    return OpenAI(api_key=api_key)
```

### 5.2 OpenAI image adapter

**File:** `sources/image_openai.py`

```python
import os
from openai import OpenAI
from agentflow_core.api.models.workflow_model import SourceModel

def get_image_client(source: SourceModel) -> OpenAI:
    """
    Creates an OpenAI client for image generation.
    
    Args:
        source: Source configuration
    
    Returns:
        OpenAI client instance
    """
    api_key_env = source.config.get('api_key_env', 'OPENAI_API_KEY')
    api_key = os.getenv(api_key_env)
    
    if not api_key:
        raise ValueError(f"API key not found in environment variable '{api_key_env}'")
    
    return OpenAI(api_key=api_key)
```

### 5.3 PostgreSQL adapter

**File:** `sources/db_postgres.py`

```python
import os
import psycopg
from agentflow_core.api.models.workflow_model import SourceModel

def get_db_connection(source: SourceModel):
    """
    Creates a PostgreSQL database connection.
    
    Args:
        source: Source configuration
    
    Returns:
        Database connection
    """
    dsn_env = source.config.get('dsn_env', 'DATABASE_URL')
    dsn = os.getenv(dsn_env)
    
    if not dsn:
        raise ValueError(f"DSN not found in environment variable '{dsn_env}'")
    
    return psycopg.connect(dsn)
```

### 5.4 HTTP API adapter

**File:** `sources/api_http.py`

```python
import os
import httpx
from agentflow_core.api.models.workflow_model import SourceModel

def get_http_client(source: SourceModel) -> httpx.Client:
    """
    Creates an HTTP client for API calls.
    
    Args:
        source: Source configuration
    
    Returns:
        HTTP client instance
    """
    base_url = source.config.get('base_url')
    if not base_url:
        raise ValueError("HTTP source missing base_url")
    
    headers = {}
    auth_env = source.config.get('auth_env')
    if auth_env:
        auth_token = os.getenv(auth_env)
        if auth_token:
            headers['Authorization'] = f"Bearer {auth_token}"
    
    return httpx.Client(base_url=base_url, headers=headers)
```

---

## 6. API layer

### 6.1 FastAPI application

**File:** `api/main.py`

```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from agentflow_core.api.routes import workflows, sources, health

app = FastAPI(
    title="AgentFlow Core API",
    version="1.0.0",
    description="Multi-Agent Workflow Orchestration Engine"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(health.router, prefix="/health", tags=["health"])
app.include_router(workflows.router, prefix="/workflows", tags=["workflows"])
app.include_router(sources.router, prefix="/sources", tags=["sources"])

@app.get("/")
async def root():
    return {
        "service": "AgentFlow Core",
        "version": "1.0.0",
        "status": "running"
    }
```

### 6.2 Workflow routes

**File:** `api/routes/workflows.py`

```python
from fastapi import APIRouter, HTTPException
from agentflow_core.api.models.workflow_model import (
    WorkflowSpecModel,
    ExecuteRequest,
    ExecuteResponse,
    ValidationResponse
)
from agentflow_core.runtime.validator import validate_workflow
from agentflow_core.runtime.executor import run_workflow
import uuid

router = APIRouter()

@router.post("/validate", response_model=ValidationResponse)
async def validate_workflow_endpoint(spec: WorkflowSpecModel):
    """Validates a workflow specification."""
    errors = validate_workflow(spec)
    
    return ValidationResponse(
        valid=len(errors) == 0,
        errors=errors
    )

@router.post("/execute", response_model=ExecuteResponse)
async def execute_workflow_endpoint(request: ExecuteRequest):
    """Executes a workflow with initial state."""
    # Validate workflow
    errors = validate_workflow(request.workflow)
    if errors:
        raise HTTPException(status_code=400, detail={
            "message": "Workflow validation failed",
            "errors": [e.dict() for e in errors]
        })
    
    # Execute workflow
    try:
        final_state = run_workflow(request.workflow, request.initial_state)
        
        return ExecuteResponse(
            status="success",
            execution_id=str(uuid.uuid4()),
            final_state=dict(final_state),
            metrics={
                "execution_time": final_state.get('metadata', {}).get('execution_time', 0),
                "tokens_used": final_state.get('tokens_used', 0)
            }
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail={
            "message": "Workflow execution failed",
            "error": str(e)
        })
```

### 6.3 Source routes

**File:** `api/routes/sources.py`

```python
from fastapi import APIRouter, HTTPException
from typing import List
from agentflow_core.api.models.workflow_model import SourceModel

router = APIRouter()

# In-memory storage (replace with database in production)
sources_db = {}

@router.post("/", response_model=SourceModel)
async def create_source(source: SourceModel):
    """Creates a new source."""
    if source.id in sources_db:
        raise HTTPException(status_code=409, detail="Source already exists")
    
    sources_db[source.id] = source
    return source

@router.get("/", response_model=List[SourceModel])
async def list_sources():
    """Lists all sources."""
    return list(sources_db.values())

@router.get("/{source_id}", response_model=SourceModel)
async def get_source(source_id: str):
    """Retrieves a specific source."""
    if source_id not in sources_db:
        raise HTTPException(status_code=404, detail="Source not found")
    
    return sources_db[source_id]

@router.put("/{source_id}", response_model=SourceModel)
async def update_source(source_id: str, source: SourceModel):
    """Updates a source."""
    if source_id not in sources_db:
        raise HTTPException(status_code=404, detail="Source not found")
    
    sources_db[source_id] = source
    return source

@router.delete("/{source_id}")
async def delete_source(source_id: str):
    """Deletes a source."""
    if source_id not in sources_db:
        raise HTTPException(status_code=404, detail="Source not found")
    
    del sources_db[source_id]
    return {"status": "deleted"}
```

### 6.4 Health routes

**File:** `api/routes/health.py`

```python
from fastapi import APIRouter
import time

router = APIRouter()

start_time = time.time()

@router.get("/")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "ok",
        "version": "1.0.0",
        "uptime": time.time() - start_time
    }

@router.get("/ready")
async def readiness_check():
    """Readiness check for Kubernetes."""
    # Add checks for dependencies (DB, Redis, etc.)
    return {"status": "ready"}

@router.get("/live")
async def liveness_check():
    """Liveness check for Kubernetes."""
    return {"status": "alive"}
```

---

## 7. Frontend architecture

### 7.1 Technology stack

| Component | Technology | Version |
|-----------|------------|---------|
| Framework | Next.js | 16 |
| UI Library | React | 19 |
| Language | TypeScript | 5.0+ |
| Canvas | React Flow | 12 |
| State | Zustand | 4.4+ |
| Styling | TailwindCSS | 3.4+ |
| Components | ShadCN UI | Latest |
| Build Tool | Turbopack | Built-in |

### 7.2 Project structure

```
frontend/agentflow-studio/
├── app/
│   ├── layout.tsx                  # Root layout
│   ├── page.tsx                    # Dashboard
│   ├── designer/
│   │   └── page.tsx                # Workflow designer
│   └── api/
│       ├── workflows/
│       │   └── route.ts            # Proxy to backend
│       └── execute/
│           └── route.ts            # Execution proxy
├── components/
│   ├── WorkflowCanvas.tsx          # React Flow canvas
│   ├── NodePalette.tsx             # Node drag source
│   ├── PropertiesPanel.tsx         # Node/queue config
│   ├── QueueEditor.tsx             # Queue configuration
│   ├── SourceEditor.tsx            # Source management
│   └── JsonPreview.tsx             # JSON viewer
├── lib/
│   ├── types.ts                    # TypeScript types
│   ├── api.ts                      # Backend API client
│   ├── mappers.ts                  # Data transformations
│   └── useWorkflowStore.ts         # Zustand store
└── styles/
    └── globals.css                 # Global styles
```

---

## 8. Component specifications

### 8.1 Workflow store

**File:** `lib/useWorkflowStore.ts`

```typescript
'use client';

import { create } from 'zustand';

export interface WorkflowNode {
  id: string;
  type: string;
  position: { x: number; y: number };
  data: any;
}

export interface WorkflowEdge {
  id: string;
  source: string;
  target: string;
  label?: string;
}

export interface WorkflowQueue {
  id: string;
  from: string;
  to: string;
  bandwidth?: {
    max_messages_per_second?: number;
    max_requests_per_minute?: number;
    max_tokens_per_minute?: number;
  };
}

export interface WorkflowSource {
  id: string;
  kind: string;
  config: Record<string, any>;
}

interface WorkflowState {
  nodes: WorkflowNode[];
  edges: WorkflowEdge[];
  queues: WorkflowQueue[];
  sources: WorkflowSource[];
  startNode: string;
  
  setNodes: (nodes: WorkflowNode[]) => void;
  setEdges: (edges: WorkflowEdge[]) => void;
  setQueues: (queues: WorkflowQueue[]) => void;
  setSources: (sources: WorkflowSource[]) => void;
  setStartNode: (id: string) => void;
  
  addNode: (node: WorkflowNode) => void;
  removeNode: (id: string) => void;
  updateNode: (id: string, data: Partial<WorkflowNode>) => void;
  
  addEdge: (edge: WorkflowEdge) => void;
  removeEdge: (id: string) => void;
  
  addQueue: (queue: WorkflowQueue) => void;
  removeQueue: (id: string) => void;
  
  addSource: (source: WorkflowSource) => void;
  removeSource: (id: string) => void;
  
  generateSpec: () => any;
  clear: () => void;
}

export const useWorkflowStore = create<WorkflowState>((set, get) => ({
  nodes: [],
  edges: [],
  queues: [],
  sources: [],
  startNode: 'input',
  
  setNodes: (nodes) => set({ nodes }),
  setEdges: (edges) => set({ edges }),
  setQueues: (queues) => set({ queues }),
  setSources: (sources) => set({ sources }),
  setStartNode: (id) => set({ startNode: id }),
  
  addNode: (node) => set((state) => ({
    nodes: [...state.nodes, node]
  })),
  
  removeNode: (id) => set((state) => ({
    nodes: state.nodes.filter((n) => n.id !== id),
    edges: state.edges.filter((e) => e.source !== id && e.target !== id)
  })),
  
  updateNode: (id, data) => set((state) => ({
    nodes: state.nodes.map((n) => 
      n.id === id ? { ...n, ...data } : n
    )
  })),
  
  addEdge: (edge) => set((state) => ({
    edges: [...state.edges, edge]
  })),
  
  removeEdge: (id) => set((state) => ({
    edges: state.edges.filter((e) => e.id !== id)
  })),
  
  addQueue: (queue) => set((state) => ({
    queues: [...state.queues, queue]
  })),
  
  removeQueue: (id) => set((state) => ({
    queues: state.queues.filter((q) => q.id !== id)
  })),
  
  addSource: (source) => set((state) => ({
    sources: [...state.sources, source]
  })),
  
  removeSource: (id) => set((state) => ({
    sources: state.sources.filter((s) => s.id !== id)
  })),
  
  generateSpec: () => {
    const state = get();
    return {
      nodes: state.nodes.map((n) => ({
        id: n.id,
        type: n.type,
        metadata: n.data
      })),
      edges: state.edges.map((e) => ({
        from: e.source,
        to: e.target
      })),
      queues: state.queues,
      sources: state.sources,
      start_node: state.startNode
    };
  },
  
  clear: () => set({
    nodes: [],
    edges: [],
    queues: [],
    sources: [],
    startNode: 'input'
  })
}));
```

### 8.2 API client

**File:** `lib/api.ts`

```typescript
const CORE_URL = process.env.NEXT_PUBLIC_CORE_URL || 'http://localhost:8000';

export const api = {
  validateWorkflow: async (spec: any) => {
    const response = await fetch(`${CORE_URL}/workflows/validate`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(spec)
    });
    
    if (!response.ok) {
      throw new Error('Validation failed');
    }
    
    return response.json();
  },
  
  executeWorkflow: async (spec: any, initialState: any) => {
    const response = await fetch(`${CORE_URL}/workflows/execute`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        workflow: spec,
        initial_state: initialState
      })
    });
    
    if (!response.ok) {
      throw new Error('Execution failed');
    }
    
    return response.json();
  },
  
  listSources: async () => {
    const response = await fetch(`${CORE_URL}/sources`);
    
    if (!response.ok) {
      throw new Error('Failed to fetch sources');
    }
    
    return response.json();
  },
  
  createSource: async (source: any) => {
    const response = await fetch(`${CORE_URL}/sources`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(source)
    });
    
    if (!response.ok) {
      throw new Error('Failed to create source');
    }
    
    return response.json();
  }
};
```

---

## 9. State management

### 9.1 Zustand store architecture

```
┌─────────────────────────────────────────────────────────────┐
│                   Workflow Store (Zustand)                   │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  State:                                                     │
│  - nodes: WorkflowNode[]                                    │
│  - edges: WorkflowEdge[]                                    │
│  - queues: WorkflowQueue[]                                  │
│  - sources: WorkflowSource[]                                │
│  - startNode: string                                        │
│                                                             │
│  Actions:                                                   │
│  - addNode(), removeNode(), updateNode()                    │
│  - addEdge(), removeEdge()                                  │
│  - addQueue(), removeQueue()                                │
│  - addSource(), removeSource()                              │
│  - generateSpec()                                           │
│                                                             │
└─────────────────────────────────────────────────────────────┘
                        │
        ┌───────────────┼───────────────┐
        │               │               │
        ▼               ▼               ▼
┌──────────────┐ ┌──────────────┐ ┌──────────────┐
│   Canvas     │ │  Properties  │ │    JSON      │
│  Component   │ │    Panel     │ │   Preview    │
└──────────────┘ └──────────────┘ └──────────────┘
```

---

## 10. Error handling

### 10.1 Backend error handling

**File:** `utils/error_handler.py`

```python
from fastapi import Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError

class WorkflowError(Exception):
    """Base class for workflow-related errors."""
    def __init__(self, message: str, code: str):
        self.message = message
        self.code = code
        super().__init__(self.message)

class ValidationError(WorkflowError):
    """Workflow validation error."""
    pass

class ExecutionError(WorkflowError):
    """Workflow execution error."""
    pass

async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Handles Pydantic validation errors."""
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "detail": exc.errors(),
            "body": exc.body
        }
    )

async def workflow_exception_handler(request: Request, exc: WorkflowError):
    """Handles workflow-specific errors."""
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={
            "message": exc.message,
            "code": exc.code
        }
    )
```

### 10.2 Frontend error handling

```typescript
// lib/errors.ts

export class ApiError extends Error {
  constructor(
    message: string,
    public statusCode: number,
    public details?: any
  ) {
    super(message);
    this.name = 'ApiError';
  }
}

export async function handleApiResponse(response: Response) {
  if (!response.ok) {
    const error = await response.json().catch(() => ({}));
    throw new ApiError(
      error.message || 'Request failed',
      response.status,
      error
    );
  }
  return response.json();
}
```

---

## 11. Testing strategy

### 11.1 Backend testing

```python
# tests/test_validator.py

import pytest
from agentflow_core.api.models.workflow_model import WorkflowSpecModel
from agentflow_core.runtime.validator import validate_workflow

def test_validate_valid_workflow():
    """Tests validation of a valid workflow."""
    spec = WorkflowSpecModel(
        nodes=[
            {"id": "input", "type": "input"},
            {"id": "llm", "type": "llm", "metadata": {"source": "openai"}}
        ],
        edges=[
            {"from": "input", "to": "llm"}
        ],
        queues=[],
        sources=[
            {"id": "openai", "kind": "llm", "config": {"model_name": "gpt-4"}}
        ],
        start_node="input"
    )
    
    errors = validate_workflow(spec)
    assert len(errors) == 0

def test_validate_missing_start_node():
    """Tests validation with missing start node."""
    spec = WorkflowSpecModel(
        nodes=[{"id": "input", "type": "input"}],
        edges=[],
        queues=[],
        sources=[],
        start_node="nonexistent"
    )
    
    errors = validate_workflow(spec)
    assert len(errors) > 0
    assert any(e.code == "E005" for e in errors)
```

### 11.2 Frontend testing

```typescript
// __tests__/useWorkflowStore.test.ts

import { renderHook, act } from '@testing-library/react';
import { useWorkflowStore } from '@/lib/useWorkflowStore';

describe('useWorkflowStore', () => {
  it('should add a node', () => {
    const { result } = renderHook(() => useWorkflowStore());
    
    act(() => {
      result.current.addNode({
        id: 'test-node',
        type: 'llm',
        position: { x: 0, y: 0 },
        data: {}
      });
    });
    
    expect(result.current.nodes).toHaveLength(1);
    expect(result.current.nodes[0].id).toBe('test-node');
  });
  
  it('should generate workflow spec', () => {
    const { result } = renderHook(() => useWorkflowStore());
    
    act(() => {
      result.current.addNode({
        id: 'input',
        type: 'input',
        position: { x: 0, y: 0 },
        data: {}
      });
      
      result.current.addSource({
        id: 'openai',
        kind: 'llm',
        config: { model_name: 'gpt-4' }
      });
    });
    
    const spec = result.current.generateSpec();
    
    expect(spec.nodes).toHaveLength(1);
    expect(spec.sources).toHaveLength(1);
    expect(spec.start_node).toBe('input');
  });
});
```

---

**Document Approval**

| Role | Name | Date | Signature |
|------|------|------|-----------|
| Tech Lead | _______________ | _______________ | _______________ |
| Senior Backend Engineer | _______________ | _______________ | _______________ |
| Senior Frontend Engineer | _______________ | _______________ | _______________ |
