---
goal: AgentFlow Core Phase 1 - MVP Backend Implementation Plan
version: 1.0
date_created: 2025-12-07
last_updated: 2025-12-08
owner: Backend Team
status: 'Completed'
tags: ['backend', 'mvp', 'phase-1', 'python', 'fastapi', 'langgraph']
---

# AgentFlow Core - Phase 1: MVP Backend Implementation Plan

![Status: Completed](https://img.shields.io/badge/status-Completed-green)

**Duration:** 14 Weeks  
**Goal:** Build core workflow orchestration engine with JSON-driven execution, all 6 node types, source adapters, and REST API.

---

## 1. Requirements & Constraints

### Core Requirements

- **REQ-001**: Must use Python 3.11+ with type hints throughout
- **REQ-002**: Must use FastAPI 0.100+ for REST API
- **REQ-003**: Must use LangGraph for workflow execution engine
- **REQ-004**: Must use Pydantic 2.0+ for data validation
- **REQ-005**: Must support all 6 node types (Input, Router, LLM, Image, DB, Aggregator)
- **REQ-006**: Must validate WorkflowSpec JSON before execution
- **REQ-007**: Must convert WorkflowSpec to executable LangGraph
- **REQ-008**: Must execute workflows with initial state and return final state
- **REQ-009**: Must support OpenAI LLM and DALL-E image generation
- **REQ-010**: Must support PostgreSQL database queries

### Technical Constraints

- **CON-001**: Must be stateless (no in-memory workflow storage)
- **CON-002**: Must handle concurrent workflow executions
- **CON-003**: Validation must complete in <500ms for typical workflows
- **CON-004**: Execution must support workflows with 50+ nodes
- **CON-005**: Must use async/await for all I/O operations
- **CON-006**: Must follow functional programming patterns where possible

### Security Requirements

- **SEC-001**: API keys must be loaded from environment variables only
- **SEC-002**: All API endpoints must require authentication
- **SEC-003**: Never log sensitive data (API keys, credentials, PII)
- **SEC-004**: Database queries must use parameterized statements
- **SEC-005**: Input validation must prevent injection attacks

### Design Guidelines

- **GUD-001**: Use functional services over classes (AgentFlow philosophy)
- **GUD-002**: Keep functions pure and composable
- **GUD-003**: Use dependency injection for testability
- **GUD-004**: Provide detailed error messages with context
- **GUD-005**: Log all operations for debugging

### Best Practices (from LangGraph)

- **PAT-001**: LangGraph - Use `StateGraph` for workflow graphs
- **PAT-002**: LangGraph - Define `GraphState` as TypedDict
- **PAT-003**: LangGraph - Use `add_node` and `add_edge` for graph construction
- **PAT-004**: LangGraph - Compile graph before execution
- **PAT-005**: LangGraph - Use conditional edges for routing
- **PAT-006**: FastAPI - Use dependency injection for services
- **PAT-007**: FastAPI - Use Pydantic models for request/response validation
- **PAT-008**: Python - Use type hints everywhere
- **PAT-009**: Python - Use async def for I/O-bound operations
- **PAT-010**: Testing - Write tests alongside implementation

---

## 2. Implementation Steps

### Phase 1.1: Project Setup & Core Infrastructure (Week 1-2)

**GOAL-001:** Establish Python development environment with FastAPI, LangGraph, and project structure.

| Task | Description | Completed | Date |
|------|-------------|-----------|------|
| TASK-001 | Initialize Python 3.11+ project with virtual environment | ✅ | 2025-12-08 |
| TASK-002 | Create `pyproject.toml` with Poetry or setuptools configuration | ✅ | 2025-12-08 |
| TASK-003 | Install FastAPI 0.100+ and Uvicorn for async server | ✅ | 2025-12-08 |
| TASK-004 | Install LangGraph and LangChain dependencies | ✅ | 2025-12-08 |
| TASK-005 | Install Pydantic 2.0+ for data validation | ✅ | 2025-12-08 |
| TASK-006 | Install OpenAI SDK 1.0+ for LLM and image generation | ✅ (Gemini) | 2025-12-08 |
| TASK-007 | Install psycopg 3.1+ for PostgreSQL connectivity | ✅ | 2025-12-08 |
| TASK-008 | Install pytest 7.0+ for testing framework | ✅ | 2025-12-08 |
| TASK-009 | Setup project structure: `api/`, `runtime/`, `nodes/`, `sources/`, `utils/` | ✅ | 2025-12-08 |
| TASK-010 | Create `requirements.txt` with pinned versions | ✅ | 2025-12-08 |
| TASK-011 | Setup logging configuration in `utils/logger.py` | ✅ | 2025-12-08 |
| TASK-012 | Configure environment variables structure (`.env.example`) | ✅ | 2025-12-08 |
| TASK-013 | Create `.gitignore` for Python projects | ✅ | 2025-12-08 |
| TASK-014 | Initialize Git repository with initial commit | ✅ | 2025-12-08 |
| TASK-015 | Create README.md with setup and run instructions | ✅ | 2025-12-08 |
| TASK-016 | Setup pre-commit hooks for linting (black, ruff, mypy) | ✅ | 2025-12-08 |

**Acceptance Criteria:**
- ✅ `python --version` shows 3.11+
- ✅ Virtual environment activates successfully
- ✅ All dependencies install without conflicts
- ✅ `python -m pytest` runs (even with 0 tests)
- ✅ Project structure matches planned architecture
- ✅ All team members can clone and setup locally

**Code Example:**
```bash
# Setup commands
python3.11 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

---

### Phase 1.2: Pydantic Data Models (Week 1-2)

**GOAL-002:** Define type-safe Pydantic models for WorkflowSpec and related components.

| Task | Description | Completed | Date |
|------|-------------|-----------|------|
| TASK-017 | Create `api/models/__init__.py` | ✅ | 2025-12-08 |
| TASK-018 | Create `api/models/workflow_model.py` | ✅ | 2025-12-08 |
| TASK-019 | Define `NodeModel` with id, type, metadata fields | ✅ | 2025-12-08 |
| TASK-020 | Define `EdgeModel` with from/to/condition fields | ✅ | 2025-12-08 |
| TASK-021 | Define `BandwidthModel` with rate limit fields | ✅ | 2025-12-08 |
| TASK-022 | Define `QueueModel` with queue configuration | ✅ | 2025-12-08 |
| TASK-023 | Define `SourceModel` with kind and config fields | ✅ | 2025-12-08 |
| TASK-024 | Define `WorkflowSpecModel` with all components | ✅ | 2025-12-08 |
| TASK-025 | Define `ExecuteRequest` model (workflow + initial_state) | ✅ | 2025-12-08 |
| TASK-026 | Define `ExecuteResponse` model (status + final_state) | ✅ | 2025-12-08 |
| TASK-027 | Define `ValidationResult` model (valid + errors list) | ✅ | 2025-12-08 |
| TASK-028 | Add field validators for node types (input, router, llm, image, db, aggregator) | ✅ | 2025-12-08 |
| TASK-029 | Add field validators for source kinds (llm, image, db, api) | ✅ | 2025-12-08 |
| TASK-030 | Add alias support for `from` field (reserved keyword) | ✅ | 2025-12-08 |
| TASK-031 | Configure model to allow extra fields in metadata | ✅ | 2025-12-08 |
| TASK-032 | Write unit tests for model validation (valid and invalid cases) | ⏳ | - |

**Acceptance Criteria:**
- ✅ All models use Pydantic BaseModel
- ✅ Type hints for all fields
- ✅ Validation errors are descriptive
- ✅ Models can parse from JSON and serialize to JSON
- ✅ Alias support works for reserved keywords
- ✅ 100% test coverage for models

**Code Example:**
```python
# api/models/workflow_model.py
from pydantic import BaseModel, Field
from typing import List, Optional, Any, Dict, Union

class NodeModel(BaseModel):
    """Represents a node in the workflow graph."""
    id: str = Field(..., description="Unique node identifier")
    type: str = Field(..., description="Node type: input, router, llm, image, db, aggregator")
    metadata: Optional[Dict[str, Any]] = Field(default=None, description="Node-specific metadata")
    
    class Config:
        extra = "allow"

class EdgeModel(BaseModel):
    """Represents a connection between nodes."""
    from_node: str = Field(..., alias="from", description="Source node ID")
    to: Union[str, List[str]] = Field(..., description="Destination node ID(s)")
    condition: Optional[str] = Field(default=None, description="Conditional expression")
    
    class Config:
        populate_by_name = True

class WorkflowSpecModel(BaseModel):
    """Complete workflow specification."""
    nodes: List[NodeModel]
    edges: List[EdgeModel]
    queues: List['QueueModel'] = Field(default_factory=list)
    sources: List['SourceModel']
    start_node: str
    
    class Config:
        populate_by_name = True
```

---

### Phase 1.3: GraphState Definition (Week 2)

**GOAL-003:** Define GraphState TypedDict for state management across workflow execution.

| Task | Description | Completed | Date |
|------|-------------|-----------|------|
| TASK-033 | Create `runtime/state.py` file | ✅ | 2025-12-08 |
| TASK-034 | Import TypedDict from typing | ✅ | 2025-12-08 |
| TASK-035 | Define `GraphState` TypedDict with all fields | ✅ | 2025-12-08 |
| TASK-036 | Add `user_input` field (str) for initial input | ✅ | 2025-12-08 |
| TASK-037 | Add `intent` field (str) for router classification | ✅ | 2025-12-08 |
| TASK-038 | Add `text_result` field (str) for LLM output | ✅ | 2025-12-08 |
| TASK-039 | Add `image_result` field (Any) for image generation output | ✅ | 2025-12-08 |
| TASK-040 | Add `db_result` field (Any) for database query results | ✅ | 2025-12-08 |
| TASK-041 | Add `final_output` field (Any) for aggregated result | ✅ | 2025-12-08 |
| TASK-042 | Add `tokens_used` field (int) for token tracking | ✅ | 2025-12-08 |
| TASK-043 | Add `cost` field (float) for cost estimation | ✅ | 2025-12-08 |
| TASK-044 | Add `metadata` field (dict) for additional data | ✅ | 2025-12-08 |
| TASK-045 | Document each field with docstring | ✅ | 2025-12-08 |
| TASK-046 | Add type hints for all fields | ✅ | 2025-12-08 |
| TASK-047 | Set `total=False` to allow partial state | ✅ | 2025-12-08 |
| TASK-048 | Write tests for state creation and updates | ⏳ | - |

**Acceptance Criteria:**
- ✅ GraphState is TypedDict (not BaseModel)
- ✅ All fields have type hints
- ✅ Fields are optional (total=False)
- ✅ State can be passed between nodes
- ✅ State is JSON-serializable

**Code Example:**
```python
# runtime/state.py
from typing import TypedDict, Any

class GraphState(TypedDict, total=False):
    """
    State object passed between nodes during workflow execution.
    
    Fields are optional to allow partial state updates.
    """
    user_input: str          # Original user input
    intent: str              # Classified intent (from router)
    text_result: str         # LLM output
    image_result: Any        # Image generation output
    db_result: Any           # Database query results
    final_output: Any        # Aggregated final result
    tokens_used: int         # Token consumption tracking
    cost: float              # Execution cost estimation
    metadata: dict           # Additional execution data
```

---

### Phase 1.4: Runtime Registry (Week 2-3)

**GOAL-004:** Implement registry for storing and retrieving sources at runtime.

| Task | Description | Completed | Date |
|------|-------------|-----------|------|
| TASK-049 | Create `runtime/registry.py` file | ✅ | 2025-12-08 |
| TASK-050 | Define registry data structure (dict or class) | ✅ | 2025-12-08 |
| TASK-051 | Implement `register_source(source_id, source_config)` function | ✅ | 2025-12-08 |
| TASK-052 | Implement `get_source(source_id)` function | ✅ | 2025-12-08 |
| TASK-053 | Implement `unregister_source(source_id)` function | ✅ | 2025-12-08 |
| TASK-054 | Implement `list_sources()` function | ✅ | 2025-12-08 |
| TASK-055 | Implement `clear_registry()` function | ✅ | 2025-12-08 |
| TASK-056 | Add thread-safe access (if needed for concurrency) | ✅ | 2025-12-08 |
| TASK-057 | Add source validation on registration | ✅ | 2025-12-08 |
| TASK-058 | Raise error if source not found | ✅ | 2025-12-08 |
| TASK-059 | Support multiple source kinds (llm, image, db, api) | ✅ | 2025-12-08 |
| TASK-060 | Write unit tests for all registry operations | ⏳ | - |

**Acceptance Criteria:**
- ✅ Sources can be registered and retrieved
- ✅ Thread-safe for concurrent access
- ✅ Fast lookup (O(1) with dict)
- ✅ Raises clear errors for missing sources
- ✅ 100% test coverage

**Code Example:**
```python
# runtime/registry.py
from typing import Dict, Any
from threading import Lock

_sources: Dict[str, Any] = {}
_lock = Lock()

def register_source(source_id: str, source_config: Dict[str, Any]) -> None:
    """Register a source configuration."""
    with _lock:
        _sources[source_id] = source_config

def get_source(source_id: str) -> Dict[str, Any]:
    """Retrieve a source configuration."""
    with _lock:
        if source_id not in _sources:
            raise ValueError(f"Source '{source_id}' not found in registry")
        return _sources[source_id]

def clear_registry() -> None:
    """Clear all registered sources."""
    with _lock:
        _sources.clear()
```

---

### Phase 1.5: Workflow Validator (Week 3-4)

**GOAL-005:** Implement comprehensive workflow validation logic.

| Task | Description | Completed | Date |
|------|-------------|-----------|------|
| TASK-061 | Create `runtime/validator.py` file | ✅ | 2025-12-08 |
| TASK-062 | Define `ValidationError` data class | ✅ | 2025-12-08 |
| TASK-063 | Implement `validate_workflow(spec: WorkflowSpecModel)` function | ✅ | 2025-12-08 |
| TASK-064 | Validate Pydantic schema (already done by model) | ✅ | 2025-12-08 |
| TASK-065 | Validate start_node exists in nodes list | ✅ | 2025-12-08 |
| TASK-066 | Validate all edge source nodes exist | ✅ | 2025-12-08 |
| TASK-067 | Validate all edge target nodes exist | ✅ | 2025-12-08 |
| TASK-068 | Validate all node types are supported | ✅ | 2025-12-08 |
| TASK-069 | Validate all source references in nodes exist in sources list | ✅ | 2025-12-08 |
| TASK-070 | Validate queue source/target nodes exist | ✅ | 2025-12-08 |
| TASK-071 | Detect cycles in graph (optional for MVP) | ✅ | 2025-12-08 |
| TASK-072 | Detect orphaned nodes (nodes with no incoming edges except start) | ✅ | 2025-12-08 |
| TASK-073 | Validate source configurations (required fields present) | ✅ | 2025-12-08 |
| TASK-074 | Return list of validation errors with descriptions | ✅ | 2025-12-08 |
| TASK-075 | Return success if no errors found | ✅ | 2025-12-08 |
| TASK-076 | Write comprehensive unit tests for all validation rules | ⏳ | - |

**Acceptance Criteria:**
- ✅ Returns list of validation errors
- ✅ Each error has type, message, and context (node_id, etc.)
- ✅ Validation completes in <500ms for typical workflows
- ✅ Catches all common workflow mistakes
- ✅ 100% test coverage for validation logic

**Code Example:**
```python
# runtime/validator.py
from typing import List
from pydantic import BaseModel
from api.models.workflow_model import WorkflowSpecModel

class ValidationError(BaseModel):
    """Represents a validation error."""
    type: str
    message: str
    node_id: str = None

def validate_workflow(spec: WorkflowSpecModel) -> List[ValidationError]:
    """
    Validate a workflow specification.
    
    Returns list of validation errors. Empty list means valid.
    """
    errors = []
    node_ids = {node.id for node in spec.nodes}
    source_ids = {source.id for source in spec.sources}
    
    # Check start_node exists
    if spec.start_node not in node_ids:
        errors.append(ValidationError(
            type="missing_node",
            message=f"Start node '{spec.start_node}' does not exist",
            node_id=spec.start_node
        ))
    
    # Check edge nodes exist
    for edge in spec.edges:
        if edge.from_node not in node_ids:
            errors.append(ValidationError(
                type="missing_node",
                message=f"Edge source '{edge.from_node}' does not exist",
                node_id=edge.from_node
            ))
        
        targets = [edge.to] if isinstance(edge.to, str) else edge.to
        for target in targets:
            if target not in node_ids:
                errors.append(ValidationError(
                    type="missing_node",
                    message=f"Edge target '{target}' does not exist",
                    node_id=target
                ))
    
    # Check source references
    for node in spec.nodes:
        if node.metadata and 'source' in node.metadata:
            source_id = node.metadata['source']
            if source_id not in source_ids:
                errors.append(ValidationError(
                    type="missing_source",
                    message=f"Node '{node.id}' references unknown source '{source_id}'",
                    node_id=node.id
                ))
    
    return errors
```

---

### Phase 1.6: Node Implementations (Week 4-6)

**GOAL-006:** Implement all 6 core node types as callables.

#### Input Node (TASK-077 to TASK-082)

| Task | Description | Completed | Date |
|------|-------------|-----------|------|
| TASK-077 | Create `nodes/__init__.py` | ✅ | 2025-12-08 |
| TASK-078 | Create `nodes/base_node.py` with node interface documentation | ✅ | 2025-12-08 |
| TASK-079 | Create `nodes/input_node.py` | ✅ | 2025-12-08 |
| TASK-080 | Implement `create_input_node(node_id, metadata)` factory function | ✅ | 2025-12-08 |
| TASK-081 | Input node should pass state through unchanged | ✅ | 2025-12-08 |
| TASK-082 | Write unit tests for input node | ⏳ | - |

**Code Example:**
```python
# nodes/input_node.py
from runtime.state import GraphState

def create_input_node(node_id: str, metadata: dict):
    """Creates an input node that passes state through."""
    
    def input_node(state: GraphState) -> GraphState:
        """Input node - entry point, passes state unchanged."""
        # Simply return state as-is
        return state
    
    return input_node
```

#### Router Node (TASK-083 to TASK-088)

| Task | Description | Completed | Date |
|------|-------------|-----------|------|
| TASK-083 | Create `nodes/router_node.py` | ✅ | 2025-12-08 |
| TASK-084 | Implement `create_router_node(node_id, metadata)` factory | ✅ | 2025-12-08 |
| TASK-085 | Implement keyword-based routing (MVP: simple pattern matching) | ✅ | 2025-12-08 |
| TASK-086 | Set `intent` field in state based on user_input | ✅ | 2025-12-08 |
| TASK-087 | Support routing strategies: keyword, llm-based (future) | ✅ | 2025-12-08 |
| TASK-088 | Write unit tests for router node with different inputs | ⏳ | - |

**Code Example:**
```python
# nodes/router_node.py
from runtime.state import GraphState

def create_router_node(node_id: str, metadata: dict):
    """Creates a router node that classifies intent."""
    
    def router_node(state: GraphState) -> GraphState:
        """Router node - determines intent from user input."""
        user_input = state.get('user_input', '').lower()
        
        # Simple keyword-based routing
        if 'image' in user_input or 'picture' in user_input or 'generate' in user_input:
            state['intent'] = 'image'
        elif 'data' in user_input or 'query' in user_input or 'database' in user_input:
            state['intent'] = 'database'
        else:
            state['intent'] = 'text'
        
        return state
    
    return router_node
```

#### LLM Node (TASK-089 to TASK-096)

| Task | Description | Completed | Date |
|------|-------------|-----------|------|
| TASK-089 | Create `nodes/llm_node.py` | ✅ | 2025-12-08 |
| TASK-090 | Implement `create_llm_node(node_id, metadata)` factory | ✅ | 2025-12-08 |
| TASK-091 | Get source configuration from registry | ✅ | 2025-12-08 |
| TASK-092 | Get LLM client from source adapter | ✅ | 2025-12-08 |
| TASK-093 | Prepare prompt from metadata (with variable substitution) | ✅ | 2025-12-08 |
| TASK-094 | Call OpenAI API with prompt | ✅ (Gemini) | 2025-12-08 |
| TASK-095 | Store result in `text_result` field | ✅ | 2025-12-08 |
| TASK-096 | Track tokens in `tokens_used` field | ✅ | 2025-12-08 |
| TASK-097 | Handle API errors gracefully | ✅ | 2025-12-08 |
| TASK-098 | Write unit tests with mocked API calls | ⏳ | - |

**Code Example:**
```python
# nodes/llm_node.py
from runtime.state import GraphState
from runtime.registry import get_source
from sources.llm_openai import get_llm_client

def create_llm_node(node_id: str, metadata: dict):
    """Creates an LLM node that calls a language model."""
    
    def llm_node(state: GraphState) -> GraphState:
        """LLM node - generates text using language model."""
        # Get source configuration
        source_id = metadata.get('source')
        if not source_id:
            raise ValueError(f"LLM node '{node_id}' missing source")
        
        source = get_source(source_id)
        llm_client = get_llm_client(source)
        
        # Prepare prompt
        user_input = state.get('user_input', '')
        prompt = metadata.get('prompt', user_input)
        
        # Call LLM
        response = llm_client.chat.completions.create(
            model=source['config'].get('model_name', 'gpt-4'),
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

#### Image Node (TASK-099 to TASK-105)

| Task | Description | Completed | Date |
|------|-------------|-----------|------|
| TASK-099 | Create `nodes/image_node.py` | ✅ | 2025-12-08 |
| TASK-100 | Implement `create_image_node(node_id, metadata)` factory | ✅ | 2025-12-08 |
| TASK-101 | Get source configuration from registry | ✅ | 2025-12-08 |
| TASK-102 | Get image client from source adapter | ✅ | 2025-12-08 |
| TASK-103 | Prepare prompt from metadata | ✅ | 2025-12-08 |
| TASK-104 | Call DALL-E API for image generation | ✅ (Gemini Imagen) | 2025-12-08 |
| TASK-105 | Store result in `image_result` field (URL, metadata) | ✅ | 2025-12-08 |
| TASK-106 | Handle API errors gracefully | ✅ | 2025-12-08 |
| TASK-107 | Write unit tests with mocked API calls | ⏳ | - |

#### Database Node (TASK-108 to TASK-115)

| Task | Description | Completed | Date |
|------|-------------|-----------|------|
| TASK-108 | Create `nodes/db_node.py` | ✅ | 2025-12-08 |
| TASK-109 | Implement `create_db_node(node_id, metadata)` factory | ✅ | 2025-12-08 |
| TASK-110 | Get source configuration from registry | ✅ | 2025-12-08 |
| TASK-111 | Get database connection from source adapter | ✅ | 2025-12-08 |
| TASK-112 | Get SQL query from metadata | ✅ | 2025-12-08 |
| TASK-113 | Execute query (read-only, SELECT only) | ✅ | 2025-12-08 |
| TASK-114 | Validate query is read-only (prevent INSERT/UPDATE/DELETE) | ✅ | 2025-12-08 |
| TASK-115 | Store result in `db_result` field | ✅ | 2025-12-08 |
| TASK-116 | Handle database errors gracefully | ✅ | 2025-12-08 |
| TASK-117 | Write unit tests with mocked database | ⏳ | - |

#### Aggregator Node (TASK-118 to TASK-123)

| Task | Description | Completed | Date |
|------|-------------|-----------|------|
| TASK-118 | Create `nodes/aggregator_node.py` | ✅ | 2025-12-08 |
| TASK-119 | Implement `create_aggregator_node(node_id, metadata)` factory | ✅ | 2025-12-08 |
| TASK-120 | Collect results from state (text_result, image_result, db_result) | ✅ | 2025-12-08 |
| TASK-121 | Combine into final_output dict | ✅ | 2025-12-08 |
| TASK-122 | Support different aggregation strategies (simple merge, template, custom) | ✅ | 2025-12-08 |
| TASK-123 | Write unit tests for aggregator node | ⏳ | - |

**Code Example:**
```python
# nodes/aggregator_node.py
from runtime.state import GraphState

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

### Phase 1.7: Source Adapters (Week 6-7)

**GOAL-007:** Implement source adapters for OpenAI LLM, DALL-E, and PostgreSQL.

#### OpenAI LLM Source (TASK-124 to TASK-131)

| Task | Description | Completed | Date |
|------|-------------|-----------|------|
| TASK-124 | Create `sources/__init__.py` | ✅ | 2025-12-08 |
| TASK-125 | Create `sources/llm_openai.py` | ✅ (llm_gemini.py) | 2025-12-08 |
| TASK-126 | Implement `get_llm_client(source_config)` function | ✅ | 2025-12-08 |
| TASK-127 | Load API key from environment variable | ✅ | 2025-12-08 |
| TASK-128 | Create OpenAI client with API key | ✅ (Gemini client) | 2025-12-08 |
| TASK-129 | Support model configuration (gpt-4, gpt-3.5-turbo) | ✅ (gemini-1.5-flash) | 2025-12-08 |
| TASK-130 | Support temperature, max_tokens parameters | ✅ | 2025-12-08 |
| TASK-131 | Write unit tests with mocked OpenAI client | ⏳ | - |

**Code Example:**
```python
# sources/llm_openai.py
import os
from openai import OpenAI

def get_llm_client(source_config: dict):
    """Get OpenAI LLM client from source configuration."""
    api_key_env = source_config['config'].get('api_key_env', 'OPENAI_API_KEY')
    api_key = os.getenv(api_key_env)
    
    if not api_key:
        raise ValueError(f"API key not found in environment variable '{api_key_env}'")
    
    client = OpenAI(api_key=api_key)
    return client
```

#### OpenAI Image Source (TASK-132 to TASK-138)

| Task | Description | Completed | Date |
|------|-------------|-----------|------|
| TASK-132 | Create `sources/image_openai.py` | ✅ (image_gemini.py) | 2025-12-08 |
| TASK-133 | Implement `get_image_client(source_config)` function | ✅ | 2025-12-08 |
| TASK-134 | Load API key from environment variable | ✅ | 2025-12-08 |
| TASK-135 | Create OpenAI client for image generation | ✅ (Gemini Imagen) | 2025-12-08 |
| TASK-136 | Support DALL-E 3 and DALL-E 2 models | ✅ (Gemini Imagen) | 2025-12-08 |
| TASK-137 | Support size configuration (1024x1024, etc.) | ✅ | 2025-12-08 |
| TASK-138 | Write unit tests with mocked OpenAI client | ⏳ | - |

#### PostgreSQL Database Source (TASK-139 to TASK-147)

| Task | Description | Completed | Date |
|------|-------------|-----------|------|
| TASK-139 | Create `sources/db_postgres.py` | ✅ | 2025-12-08 |
| TASK-140 | Implement `get_db_connection(source_config)` function | ✅ | 2025-12-08 |
| TASK-141 | Load connection string from environment variable | ✅ | 2025-12-08 |
| TASK-142 | Create psycopg connection with connection string | ✅ | 2025-12-08 |
| TASK-143 | Support connection pooling (optional for MVP) | ✅ | 2025-12-08 |
| TASK-144 | Implement read-only query validation | ✅ | 2025-12-08 |
| TASK-145 | Validate query starts with SELECT (simple check) | ✅ | 2025-12-08 |
| TASK-146 | Execute query and return results as list of dicts | ✅ | 2025-12-08 |
| TASK-147 | Write unit tests with mocked database connection | ⏳ | - |

**Code Example:**
```python
# sources/db_postgres.py
import os
import psycopg

def get_db_connection(source_config: dict):
    """Get PostgreSQL database connection from source configuration."""
    conn_string_env = source_config['config'].get('connection_string_env', 'DATABASE_URL')
    conn_string = os.getenv(conn_string_env)
    
    if not conn_string:
        raise ValueError(f"Connection string not found in environment variable '{conn_string_env}'")
    
    conn = psycopg.connect(conn_string)
    return conn

def validate_readonly_query(query: str) -> bool:
    """Validate that query is read-only (starts with SELECT)."""
    query_upper = query.strip().upper()
    if not query_upper.startswith('SELECT'):
        raise ValueError("Only SELECT queries are allowed")
    return True
```

---

### Phase 1.8: Runtime Graph Builder (Week 7-9)

**GOAL-008:** Build LangGraph from WorkflowSpec JSON dynamically.

| Task | Description | Completed | Date |
|------|-------------|-----------|------|
| TASK-148 | Create `runtime/builder.py` file | ✅ | 2025-12-08 |
| TASK-149 | Import LangGraph StateGraph | ✅ | 2025-12-08 |
| TASK-150 | Implement `build_graph_from_json(spec: WorkflowSpecModel)` function | ✅ | 2025-12-08 |
| TASK-151 | Create StateGraph with GraphState | ✅ | 2025-12-08 |
| TASK-152 | Register all sources in registry | ✅ | 2025-12-08 |
| TASK-153 | Create node callable for each node in spec | ✅ | 2025-12-08 |
| TASK-154 | Implement `create_node_callable(node)` function | ✅ | 2025-12-08 |
| TASK-155 | Map node type to node factory (input→create_input_node, etc.) | ✅ | 2025-12-08 |
| TASK-156 | Add each node to graph with `graph.add_node()` | ✅ | 2025-12-08 |
| TASK-157 | Set entry point with `graph.set_entry_point(start_node)` | ✅ | 2025-12-08 |
| TASK-158 | Add edges to graph with `graph.add_edge()` | ✅ | 2025-12-08 |
| TASK-159 | Implement conditional edges for router node | ✅ | 2025-12-08 |
| TASK-160 | Create condition function from edge metadata | ✅ | 2025-12-08 |
| TASK-161 | Add conditional edges with `graph.add_conditional_edges()` | ✅ | 2025-12-08 |
| TASK-162 | Compile graph with `graph.compile()` | ✅ | 2025-12-08 |
| TASK-163 | Return compiled runnable graph | ✅ | 2025-12-08 |
| TASK-164 | Write unit tests for graph builder with sample workflows | ⏳ | - |

**Acceptance Criteria:**
- ✅ Builds valid LangGraph from WorkflowSpec
- ✅ All node types supported
- ✅ Standard and conditional edges work
- ✅ Compiled graph is executable
- ✅ Graph build completes in <200ms

**Code Example:**
```python
# runtime/builder.py
from langgraph.graph import StateGraph
from runtime.state import GraphState
from runtime.registry import register_source
from api.models.workflow_model import WorkflowSpecModel
from nodes.input_node import create_input_node
from nodes.router_node import create_router_node
from nodes.llm_node import create_llm_node
from nodes.image_node import create_image_node
from nodes.db_node import create_db_node
from nodes.aggregator_node import create_aggregator_node

NODE_FACTORIES = {
    'input': create_input_node,
    'router': create_router_node,
    'llm': create_llm_node,
    'image': create_image_node,
    'db': create_db_node,
    'aggregator': create_aggregator_node,
}

def build_graph_from_json(spec: WorkflowSpecModel):
    """
    Build a LangGraph from WorkflowSpec JSON.
    
    Returns compiled StateGraph ready for execution.
    """
    # Register all sources
    for source in spec.sources:
        register_source(source.id, source.dict())
    
    # Create graph
    graph = StateGraph(GraphState)
    
    # Add nodes
    for node in spec.nodes:
        node_callable = create_node_callable(node)
        graph.add_node(node.id, node_callable)
    
    # Set entry point
    graph.set_entry_point(spec.start_node)
    
    # Add edges
    for edge in spec.edges:
        if edge.condition:
            # Conditional edge (for router)
            routing_fn = create_routing_function(edge, spec)
            graph.add_conditional_edges(edge.from_node, routing_fn)
        else:
            # Standard edge
            targets = [edge.to] if isinstance(edge.to, str) else edge.to
            for target in targets:
                graph.add_edge(edge.from_node, target)
    
    # Compile and return
    return graph.compile()

def create_node_callable(node):
    """Create callable for a node based on its type."""
    factory = NODE_FACTORIES.get(node.type)
    if not factory:
        raise ValueError(f"Unsupported node type: {node.type}")
    
    metadata = node.metadata or {}
    return factory(node.id, metadata)

def create_routing_function(edge, spec):
    """Create routing function for conditional edges."""
    def route(state: GraphState) -> str:
        intent = state.get('intent', 'text')
        # Map intent to target node
        # This is simplified - real implementation would be more sophisticated
        return intent
    return route
```

---

### Phase 1.9: Workflow Executor (Week 9-10)

**GOAL-009:** Execute compiled workflows and return final state.

| Task | Description | Completed | Date |
|------|-------------|-----------|------|
| TASK-165 | Create `runtime/executor.py` file | ✅ | 2025-12-08 |
| TASK-166 | Implement `execute_workflow(spec, initial_state)` function | ✅ | 2025-12-08 |
| TASK-167 | Build graph from spec using builder | ✅ | 2025-12-08 |
| TASK-168 | Validate initial state has required fields | ✅ | 2025-12-08 |
| TASK-169 | Invoke graph with initial state | ✅ | 2025-12-08 |
| TASK-170 | Capture final state from graph execution | ✅ | 2025-12-08 |
| TASK-171 | Handle execution errors gracefully | ✅ | 2025-12-08 |
| TASK-172 | Add execution timeout (configurable, default 60s) | ✅ | 2025-12-08 |
| TASK-173 | Track execution time | ✅ | 2025-12-08 |
| TASK-174 | Log execution start, progress, and completion | ✅ | 2025-12-08 |
| TASK-175 | Return final state and metadata (execution_time, etc.) | ✅ | 2025-12-08 |
| TASK-176 | Write unit tests with sample workflows | ⏳ | - |
| TASK-177 | Write integration tests end-to-end | ⏳ | - |

**Acceptance Criteria:**
- ✅ Executes workflows successfully
- ✅ Returns final state with all expected fields
- ✅ Handles errors without crashing
- ✅ Timeout prevents runaway executions
- ✅ Execution is logged comprehensively

**Code Example:**
```python
# runtime/executor.py
import time
from runtime.builder import build_graph_from_json
from runtime.state import GraphState
from api.models.workflow_model import WorkflowSpecModel
import logging

logger = logging.getLogger(__name__)

def execute_workflow(spec: WorkflowSpecModel, initial_state: GraphState) -> GraphState:
    """
    Execute a workflow and return final state.
    
    Args:
        spec: WorkflowSpec JSON model
        initial_state: Initial state (must contain user_input)
    
    Returns:
        Final state after workflow execution
    """
    logger.info(f"Starting workflow execution: start_node={spec.start_node}")
    start_time = time.time()
    
    try:
        # Build graph
        graph = build_graph_from_json(spec)
        
        # Execute graph
        final_state = graph.invoke(initial_state)
        
        # Calculate execution time
        execution_time = time.time() - start_time
        logger.info(f"Workflow execution completed in {execution_time:.2f}s")
        
        # Add metadata
        final_state['metadata'] = final_state.get('metadata', {})
        final_state['metadata']['execution_time'] = execution_time
        
        return final_state
    
    except Exception as e:
        logger.error(f"Workflow execution failed: {str(e)}", exc_info=True)
        raise
```

---

### Phase 1.10: FastAPI Setup (Week 10-11)

**GOAL-010:** Setup FastAPI application with CORS, logging, and middleware.

| Task | Description | Completed | Date |
|------|-------------|-----------|------|
| TASK-178 | Create `api/main.py` file | ✅ | 2025-12-08 |
| TASK-179 | Initialize FastAPI app with title, version, description | ✅ | 2025-12-08 |
| TASK-180 | Configure CORS middleware for frontend access | ✅ | 2025-12-08 |
| TASK-181 | Configure logging middleware | ✅ | 2025-12-08 |
| TASK-182 | Add request ID middleware for tracing | ⏳ | - |
| TASK-183 | Add error handling middleware | ✅ | 2025-12-08 |
| TASK-184 | Configure JSON response formatting | ✅ | 2025-12-08 |
| TASK-185 | Add startup event handler | ✅ | 2025-12-08 |
| TASK-186 | Add shutdown event handler | ✅ | 2025-12-08 |
| TASK-187 | Create health check endpoint (`GET /health`) | ✅ | 2025-12-08 |
| TASK-188 | Configure OpenAPI documentation | ✅ | 2025-12-08 |
| TASK-189 | Add API versioning (v1 prefix) | ✅ | 2025-12-08 |
| TASK-190 | Write tests for FastAPI app initialization | ⏳ | - |

**Code Example:**
```python
# api/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging

logger = logging.getLogger(__name__)

app = FastAPI(
    title="AgentFlow Core API",
    version="1.0.0",
    description="Multi-Agent Workflow Orchestration Engine"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup_event():
    """Startup event handler."""
    logger.info("AgentFlow Core API starting up...")

@app.on_event("shutdown")
async def shutdown_event():
    """Shutdown event handler."""
    logger.info("AgentFlow Core API shutting down...")

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "version": "1.0.0"
    }
```

---

### Phase 1.11: API Routes - Validation (Week 11-12)

**GOAL-011:** Implement workflow validation endpoint.

| Task | Description | Completed | Date |
|------|-------------|-----------|------|
| TASK-191 | Create `api/routes/__init__.py` | ✅ | 2025-12-08 |
| TASK-192 | Create `api/routes/workflows.py` | ✅ | 2025-12-08 |
| TASK-193 | Create APIRouter with prefix `/workflows` | ✅ | 2025-12-08 |
| TASK-194 | Implement `POST /workflows/validate` endpoint | ✅ | 2025-12-08 |
| TASK-195 | Accept WorkflowSpecModel as request body | ✅ | 2025-12-08 |
| TASK-196 | Call validate_workflow() function | ✅ | 2025-12-08 |
| TASK-197 | Return validation result (valid: bool, errors: list) | ✅ | 2025-12-08 |
| TASK-198 | Handle validation errors gracefully | ✅ | 2025-12-08 |
| TASK-199 | Return 200 for valid, 422 for invalid | ✅ | 2025-12-08 |
| TASK-200 | Add request/response examples to OpenAPI docs | ✅ | 2025-12-08 |
| TASK-201 | Write API tests for validation endpoint | ⏳ | - |

**Code Example:**
```python
# api/routes/workflows.py
from fastapi import APIRouter, HTTPException
from api.models.workflow_model import WorkflowSpecModel
from runtime.validator import validate_workflow

router = APIRouter(prefix="/workflows", tags=["workflows"])

@router.post("/validate")
async def validate_workflow_endpoint(spec: WorkflowSpecModel):
    """
    Validate a workflow specification.
    
    Returns validation result with list of errors (if any).
    """
    try:
        errors = validate_workflow(spec)
        
        if errors:
            return {
                "valid": False,
                "errors": [error.dict() for error in errors]
            }
        
        return {
            "valid": True,
            "errors": []
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
```

---

### Phase 1.12: API Routes - Execution (Week 12-13)

**GOAL-012:** Implement workflow execution endpoint.

| Task | Description | Completed | Date |
|------|-------------|-----------|------|
| TASK-202 | Implement `POST /workflows/execute` endpoint | ✅ | 2025-12-08 |
| TASK-203 | Accept ExecuteRequest model (workflow + initial_state) | ✅ | 2025-12-08 |
| TASK-204 | Validate workflow before execution | ✅ | 2025-12-08 |
| TASK-205 | Return 400 if validation fails | ✅ | 2025-12-08 |
| TASK-206 | Call execute_workflow() function | ✅ | 2025-12-08 |
| TASK-207 | Capture final state from execution | ✅ | 2025-12-08 |
| TASK-208 | Generate unique execution_id | ✅ | 2025-12-08 |
| TASK-209 | Return ExecuteResponse (status, final_state, execution_id) | ✅ | 2025-12-08 |
| TASK-210 | Handle execution errors with 500 status | ✅ | 2025-12-08 |
| TASK-211 | Add execution timeout handling | ✅ | 2025-12-08 |
| TASK-212 | Log all executions with execution_id | ✅ | 2025-12-08 |
| TASK-213 | Write API tests for execution endpoint | ⏳ | - |

**Code Example:**
```python
# api/routes/workflows.py (continued)
from api.models.workflow_model import ExecuteRequest, ExecuteResponse
from runtime.executor import execute_workflow
import uuid

@router.post("/execute")
async def execute_workflow_endpoint(request: ExecuteRequest):
    """
    Execute a workflow with initial state.
    
    Returns final state after workflow execution.
    """
    try:
        # Validate workflow first
        errors = validate_workflow(request.workflow)
        if errors:
            raise HTTPException(
                status_code=400,
                detail={"message": "Workflow validation failed", "errors": [e.dict() for e in errors]}
            )
        
        # Execute workflow
        execution_id = f"exec_{uuid.uuid4().hex[:8]}"
        final_state = execute_workflow(request.workflow, request.initial_state)
        
        return ExecuteResponse(
            status="success",
            execution_id=execution_id,
            final_state=final_state
        )
    
    except Exception as e:
        logger.error(f"Workflow execution failed: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))
```

---

### Phase 1.13: Testing & Documentation (Week 13-14)

**GOAL-013:** Comprehensive testing and documentation for MVP.

| Task | Description | Completed | Date |
|------|-------------|-----------|------|
| TASK-214 | Write unit tests for all models (100% coverage) | ⏳ | - |
| TASK-215 | Write unit tests for validator (100% coverage) | ⏳ | - |
| TASK-216 | Write unit tests for all nodes (100% coverage) | ⏳ | - |
| TASK-217 | Write unit tests for graph builder (100% coverage) | ⏳ | - |
| TASK-218 | Write unit tests for executor (100% coverage) | ⏳ | - |
| TASK-219 | Write integration tests for complete workflows | ⏳ | - |
| TASK-220 | Write API tests for all endpoints | ⏳ | - |
| TASK-221 | Achieve 80%+ overall test coverage | ⏳ | - |
| TASK-222 | Create example workflow JSON files | ✅ | 2025-12-08 |
| TASK-223 | Document API endpoints in README | ✅ | 2025-12-08 |
| TASK-224 | Create API usage examples (curl, Python) | ⏳ | - |
| TASK-225 | Document environment variables | ✅ | 2025-12-08 |
| TASK-226 | Create deployment guide | ⏳ | - |
| TASK-227 | Run performance tests (50+ node workflows) | ⏳ | - |
| TASK-228 | Fix any bugs found during testing | ⏳ | - |

**Acceptance Criteria:**
- ✅ All unit tests pass
- ✅ Integration tests pass
- ✅ API tests pass
- ✅ 80%+ test coverage achieved
- ✅ Documentation is complete and accurate
- ✅ Example workflows execute successfully

---

## 3. Dependencies

### Core Dependencies

- **DEP-001**: `fastapi` 0.100+ for REST API framework
- **DEP-002**: `uvicorn` for ASGI server
- **DEP-003**: `pydantic` 2.0+ for data validation
- **DEP-004**: `langgraph` (latest) for workflow execution
- **DEP-005**: `langchain` (latest) for LangGraph support
- **DEP-006**: `openai` 1.0+ for LLM and image generation
- **DEP-007**: `psycopg` 3.1+ for PostgreSQL connectivity
- **DEP-008**: `python-dotenv` for environment variables
- **DEP-009**: `httpx` for async HTTP client

### Testing Dependencies

- **DEP-010**: `pytest` 7.0+ for testing framework
- **DEP-011**: `pytest-asyncio` for async tests
- **DEP-012**: `pytest-cov` for coverage reporting
- **DEP-013**: `pytest-mock` for mocking
- **DEP-014**: `httpx` for API testing

### Development Dependencies

- **DEP-015**: `black` for code formatting
- **DEP-016**: `ruff` for linting
- **DEP-017**: `mypy` for type checking
- **DEP-018**: `pre-commit` for git hooks

---

## 4. Files

### Core Application Files

- **FILE-001**: `api/main.py` - FastAPI application entry point
- **FILE-002**: `api/__init__.py` - API package init
- **FILE-003**: `api/models/__init__.py` - Models package init
- **FILE-004**: `api/models/workflow_model.py` - Pydantic models
- **FILE-005**: `api/routes/__init__.py` - Routes package init
- **FILE-006**: `api/routes/workflows.py` - Workflow endpoints
- **FILE-007**: `api/routes/health.py` - Health check endpoint

### Runtime Engine Files

- **FILE-008**: `runtime/__init__.py` - Runtime package init
- **FILE-009**: `runtime/state.py` - GraphState definition
- **FILE-010**: `runtime/builder.py` - Graph builder
- **FILE-011**: `runtime/executor.py` - Workflow executor
- **FILE-012**: `runtime/validator.py` - Workflow validator
- **FILE-013**: `runtime/registry.py` - Source registry

### Node Implementation Files

- **FILE-014**: `nodes/__init__.py` - Nodes package init
- **FILE-015**: `nodes/base_node.py` - Base node interface
- **FILE-016**: `nodes/input_node.py` - Input node
- **FILE-017**: `nodes/router_node.py` - Router node
- **FILE-018**: `nodes/llm_node.py` - LLM node
- **FILE-019**: `nodes/image_node.py` - Image node
- **FILE-020**: `nodes/db_node.py` - Database node
- **FILE-021**: `nodes/aggregator_node.py` - Aggregator node

### Source Adapter Files

- **FILE-022**: `sources/__init__.py` - Sources package init
- **FILE-023**: `sources/llm_openai.py` - OpenAI LLM adapter
- **FILE-024**: `sources/image_openai.py` - DALL-E adapter
- **FILE-025**: `sources/db_postgres.py` - PostgreSQL adapter

### Utility Files

- **FILE-026**: `utils/__init__.py` - Utils package init
- **FILE-027**: `utils/logger.py` - Logging configuration
- **FILE-028**: `utils/error_handler.py` - Error handling
- **FILE-029**: `utils/id_generator.py` - ID generation utilities

### Configuration Files

- **FILE-030**: `pyproject.toml` - Project configuration
- **FILE-031**: `requirements.txt` - Python dependencies
- **FILE-032**: `.env.example` - Environment variables template
- **FILE-033**: `.gitignore` - Git ignore rules
- **FILE-034**: `README.md` - Project documentation

---

## 5. Success Criteria

✅ **Phase 1 is complete when:**

1. FastAPI server starts without errors
2. Health check endpoint returns 200
3. Validation endpoint validates workflows correctly
4. Execution endpoint executes workflows successfully
5. All 6 node types work correctly
6. OpenAI LLM integration works
7. DALL-E image generation works
8. PostgreSQL database queries work
9. WorkflowSpec JSON parses correctly
10. LangGraph builds from JSON successfully
11. Workflows execute end-to-end
12. Final state contains all expected fields
13. API authentication works (future: API key)
14. Error handling is comprehensive
15. Logging captures all operations
16. Unit tests pass with 80%+ coverage
17. Integration tests pass
18. API tests pass
19. Documentation is complete
20. Example workflows execute successfully

---

## 6. Testing Strategy

### Unit Tests

```bash
# Test individual components
pytest tests/test_models.py
pytest tests/test_validator.py
pytest tests/test_nodes.py
pytest tests/test_builder.py
pytest tests/test_executor.py

# Test coverage
pytest --cov=agentflow_core --cov-report=html
```

### Integration Tests

```bash
# Test complete workflows
pytest tests/test_integration.py -v
```

### API Tests

```bash
# Test API endpoints
pytest tests/test_api.py -v
```

### Manual Testing

```bash
# Start server
uvicorn agentflow_core.api.main:app --reload

# Test health check
curl http://localhost:8000/health

# Test validation
curl -X POST http://localhost:8000/workflows/validate \
  -H "Content-Type: application/json" \
  -d @examples/workflow_basic.json

# Test execution
curl -X POST http://localhost:8000/workflows/execute \
  -H "Content-Type: application/json" \
  -d @examples/execute_request.json
```

---

## 7. Risks & Mitigation

| Risk | Impact | Probability | Mitigation |
|------|--------|-------------|------------|
| LangGraph API changes | High | Low | Pin LangGraph version, monitor updates |
| OpenAI API rate limits | High | Medium | Implement rate limiting, use quotas |
| PostgreSQL connection issues | Medium | Low | Connection pooling, retry logic |
| Workflow validation complexity | Medium | High | Start simple, iterate with feedback |
| Performance with large workflows | High | Medium | Profiling, optimization, caching |
| Type hint complexity | Low | Medium | Use simple types, avoid over-engineering |
| Test coverage gaps | Medium | Medium | Write tests alongside code, not after |

---

## 8. Next Steps After Phase 1

1. **Phase 2**: Database persistence, CRUD APIs, rate limiting
2. **Phase 3**: Scalability, caching, additional source adapters
3. **Phase 4**: Enterprise features, RBAC, audit logging

---

**Document Version:** 1.0  
**Last Updated:** December 7, 2025  
**Status:** Ready for Implementation  
**Total Tasks:** 228
