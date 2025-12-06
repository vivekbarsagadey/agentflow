---
applyTo: '**'
---

# AgentFlow Project-Specific Rules

> **LLM Knowledge Assumption**: This guide assumes you already know Python, FastAPI, React, LangGraph, and common design patterns. It contains **ONLY AgentFlow-specific rules, conventions, and implementations** that differ from standard practices.

**Last Updated**: December 6, 2025  
**Stack**: FastAPI • Python 3.11+ • LangGraph • Next.js/TypeScript • React Flow

---

## Table of Contents

1. [Architecture Overview](#architecture-overview)
2. [Critical Policies](#critical-policies)
3. [Project Structure](#project-structure)
4. [Code Patterns](#code-patterns)
5. [Data Models](#data-models)
6. [Security & Compliance](#security--compliance)
7. [Quick Reference](#quick-reference)

---

## 1. Architecture Overview

### System Purpose

AgentFlow is a **JSON-driven workflow orchestration engine** that provides:

* **Visual workflow designer** (AgentFlow Studio - Next.js)
* **Multi-agent workflow execution** (via LangGraph runtime)
* **Configurable nodes** (LLM, Image, DB, Router, Aggregator)
* **Queue-based rate limiting** with bandwidth controls
* **REST API** for validation, execution, and management

### System Components

```
┌─────────────────────────────────────────────────────────────────┐
│                     AgentFlow Studio                            │
│                  (Next.js Visual Designer)                      │
│                                                                 │
│   Drag & Drop UI  ----> WorkflowSpec(JSON) ----> API Proxy     │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                     AgentFlow Core                              │
│                (FastAPI + Python + LangGraph)                   │
│                                                                 │
│   ┌───────────────┐     ┌───────────────────────────────┐      │
│   │  Validator    │ --> │  Runtime Graph Builder        │      │
│   └───────────────┘     └───────────────────────────────┘      │
│           │                         │                           │
│           ▼                         ▼                           │
│   ┌───────────────┐     ┌───────────────────────────────┐      │
│   │ Queue Manager │     │  Node Registry (LLM, DB, etc.)│      │
│   └───────────────┘     └───────────────────────────────┘      │
│           │                         │                           │
│           ▼                         ▼                           │
│   ┌─────────────────────────────────────────────────────┐      │
│   │        Executor (LangGraph runtime.invoke)          │      │
│   └─────────────────────────────────────────────────────┘      │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
                     Final State JSON Output
```

### Key Actors

* **Workflow Designer/Architect** – Technical user designing workflows visually
* **Backend Developer** – Extends node and source types in AgentFlow Core
* **Frontend Developer** – Enhances Studio UI, canvas behavior, and UX
* **DevOps/Platform Engineer** – Deploys and monitors AgentFlow Core and Studio
* **AgentFlow Core** – FastAPI + LangGraph runtime engine
* **AgentFlow Studio** – Next.js visual workflow designer

### Technology Stack

| Component | Technology |
|-----------|------------|
| Backend API | FastAPI (Python 3.11+) |
| Runtime Engine | LangGraph |
| Database | PostgreSQL (optional) |
| Queue/Rate Limiting | Redis |
| Frontend Studio | Next.js 16 + React 19 + TypeScript |
| Canvas Library | React Flow v12 |
| UI Components | ShadCN UI + TailwindCSS |
| State Management | Zustand |
| LLM Integration | OpenAI SDK |
| Image Generation | DALL·E / OpenAI |
| Database Queries | psycopg / SQLAlchemy |

---

## 2. Critical Policies

### ⚠️ Policy 1: Multi-Tenancy - Always Filter by tenant_id

**Every database query MUST filter by `tenant_id` for data isolation.**

```python
# ❌ FORBIDDEN - Security vulnerability (data leakage)
sessions = db.query(Session).all()

# ✅ REQUIRED - Tenant isolation
sessions = db.query(Session).filter(
    Session.tenant_id == current_tenant.id
).all()
```

### ⚠️ Policy 2: Soft Delete - NEVER Use Hard Delete

**Recordings and summaries must be recoverable for audit trails.**

```python
# ❌ FORBIDDEN - Will break audit trails
db.delete(session)

# ✅ REQUIRED - Soft delete
session.status = 'DELETED'
session.deleted_at = datetime.utcnow()
session.deleted_by = user_id
db.commit()
```

### ⚠️ Policy 3: Digital Signature Integrity

**Signed summaries MUST be tamper-proof.**

```python
# ✅ REQUIRED - Signature flow
1. Canonicalize JSON (sorted keys, no whitespace)
2. Compute SHA-256 hash
3. Sign with RSA private key (PKCS1v15)
4. Store signature + publicKeyId + documentHash
5. Never modify signed content
```

### ⚠️ Policy 4: Audit Fields on All Models

**Every model MUST have these fields:**

```python
class BaseModel:
    id: str                    # Primary key (e.g., sess_xxx, sum_xxx)
    created_at: datetime       # Auto-set on creation
    updated_at: datetime       # Auto-update on modification
    deleted_at: datetime       # Soft delete timestamp
    created_by: str           # User who created
    updated_by: str           # User who last updated
    deleted_by: str           # User who deleted
    status: str               # ACTIVE, DELETED, etc.
    tenant_id: str            # Multi-tenancy (REQUIRED)
```

### ⚠️ Policy 5: Use Functional Services Over Classes

**AgentFlow Philosophy**: Functional composition by default.

```python
# ✅ PREFERRED - Functional service
def create_workflow_service(db: Session, settings: Settings):
    def validate_workflow(spec: WorkflowSpecModel) -> List[Error]:
        errors = []
        node_ids = {n.id for n in spec.nodes}
        if spec.start_node not in node_ids:
            errors.append("Start node does not exist")
        return errors
    
    def execute_workflow(spec: WorkflowSpecModel, initial_state: GraphState) -> GraphState:
        graph = build_graph_from_json(spec)
        return graph.invoke(initial_state)
    
    return {
        "validate_workflow": validate_workflow,
        "execute_workflow": execute_workflow,
    }

# Usage
workflow_service = create_workflow_service(db, settings)
result = workflow_service["execute_workflow"](spec, initial_state)
```

### ⚠️ Policy 6: Schema Changes Require Synchronization

**When modifying SQLAlchemy models, update all layers:**

1. **SQLAlchemy Model** (`models/*.py`)
2. **Pydantic Schema** (`schemas/*.py`)
3. **Alembic Migration** (`migrations/versions/`)
4. **Service Layer** (`services/*.py`)
5. **API Routes** (`api/v1/*.py`)

```bash
# After model changes:
alembic revision --autogenerate -m "add_new_field"
alembic upgrade head
```

### ⚠️ Policy 7: Never Store Private Keys in Code

```python
# ❌ FORBIDDEN
PRIVATE_KEY = """-----BEGIN RSA PRIVATE KEY-----..."""

# ✅ REQUIRED - Load from environment/KMS
private_key = load_private_key_from_env("SIGNING_PRIVATE_KEY")
```

---

## 3. Project Structure

### Directory Layout

```
agentflow/
├── backend/
│   └── agentflow_core/
│       ├── __init__.py
│       ├── api/
│       │   ├── __init__.py
│       │   ├── main.py              # FastAPI entry point
│       │   ├── models/
│       │   │   └── workflow_model.py # Pydantic models
│       │   └── routes/
│       │       ├── workflows.py      # Validate, execute, save
│       │       ├── sources.py        # Manage sources
│       │       └── health.py         # Health checks
│       ├── runtime/
│       │   ├── builder.py            # WorkflowSpec → LangGraph
│       │   ├── executor.py           # Run workflows
│       │   ├── validator.py          # Schema + logic validation
│       │   ├── rate_limiter.py       # Queue bandwidth
│       │   ├── registry.py           # Node/source registries
│       │   └── state.py              # GraphState definitions
│       ├── nodes/
│       │   ├── base_node.py
│       │   ├── llm_node.py
│       │   ├── image_node.py
│       │   ├── db_node.py
│       │   ├── router_node.py
│       │   └── aggregator_node.py
│       ├── sources/
│       │   ├── llm_openai.py
│       │   ├── image_openai.py
│       │   ├── db_postgres.py
│       │   └── api_http.py
│       ├── schemas/
│       │   ├── workflow_schema.json
│       │   ├── node_schema.json
│       │   └── queue_schema.json
│       └── utils/
│           ├── logger.py
│           ├── error_handler.py
│           └── id_generator.py
│   ├── tests/
│   │   ├── test_api.py
│   │   ├── test_builder.py
│   │   ├── test_executor.py
│   │   └── test_validator.py
│   ├── requirements.txt
│   └── pyproject.toml
├── frontend/
│   └── agentflow-studio/
│       ├── app/
│       │   ├── layout.tsx
│       │   ├── page.tsx              # Dashboard
│       │   ├── designer/
│       │   │   └── page.tsx          # Workflow designer
│       │   ├── sources/
│       │   │   └── page.tsx          # Source manager
│       │   ├── settings/
│       │   │   └── page.tsx
│       │   └── api/
│       │       ├── workflows/
│       │       │   └── route.ts      # Proxy to backend
│       │       └── execute/
│       │           └── route.ts
│       ├── components/
│       │   ├── WorkflowCanvas.tsx
│       │   ├── NodePalette.tsx
│       │   ├── QueueEditor.tsx
│       │   ├── SourceEditor.tsx
│       │   ├── PropertiesPanel.tsx
│       │   └── JsonPreview.tsx
│       ├── lib/
│       │   ├── types.ts
│       │   ├── schema.ts
│       │   └── mappers.ts
│       ├── styles/
│       └── package.json
├── shared/
│   ├── examples/
│   │   ├── workflow_basic.json
│   │   └── workflow_extended.json
│   └── docs/
├── scripts/
│   ├── build_backend.sh
│   ├── start_backend.sh
│   ├── start_frontend.sh
│   └── deploy.sh
└── docs/
    ├── srs.md
    ├── hld.md
    ├── lld.md
    ├── API_Spec.md
    ├── BACKEND-SPEC.md
    ├── FRONTEND-SPEC.md
    └── WORKFLOW-SCHEMA.md
```

### File Naming Conventions

```
backend/agentflow_core/api/routes/workflows.py    # API routes (plural)
backend/agentflow_core/runtime/builder.py         # Runtime modules
backend/agentflow_core/nodes/llm_node.py          # Node implementations
backend/agentflow_core/sources/llm_openai.py      # Source adapters
frontend/agentflow-studio/components/WorkflowCanvas.tsx  # PascalCase components
frontend/agentflow-studio/lib/mappers.ts          # Utility modules
```

---

## 4. Code Patterns

### API Route Pattern

```python
# api/routes/workflows.py
from fastapi import APIRouter, Depends, HTTPException
from agentflow_core.api.models.workflow_model import WorkflowSpecModel, ExecuteRequest
from agentflow_core.runtime.validator import validate_workflow
from agentflow_core.runtime.executor import run_workflow

router = APIRouter(prefix="/workflows", tags=["workflows"])

@router.post("/validate")
async def validate_workflow_endpoint(spec: WorkflowSpecModel):
    """Validate a workflow specification."""
    errors = validate_workflow(spec)
    if errors:
        return {"valid": False, "errors": errors}
    return {"valid": True, "errors": []}

@router.post("/execute")
async def execute_workflow_endpoint(request: ExecuteRequest):
    """Execute a workflow with initial state."""
    # 1. Validate workflow
    errors = validate_workflow(request.workflow)
    if errors:
        raise HTTPException(status_code=400, detail=errors)
    
    # 2. Execute workflow
    result = run_workflow(request.workflow, request.initial_state)
    
    return {"status": "success", "final_state": result}
```

### Service Pattern

```python
# runtime/executor.py
from agentflow_core.runtime.builder import build_graph_from_json
from agentflow_core.runtime.state import GraphState
from agentflow_core.api.models.workflow_model import WorkflowSpecModel

def run_workflow(spec: WorkflowSpecModel, initial_state: GraphState) -> GraphState:
    """Execute a workflow and return final state."""
    
    # 1. Build LangGraph from JSON spec
    graph = build_graph_from_json(spec)
    
    # 2. Invoke the graph
    final_state = graph.invoke(initial_state)
    
    return final_state
```

### Pydantic Schema Pattern

```python
# api/models/workflow_model.py
from pydantic import BaseModel, Field
from typing import List, Optional, Any, Dict

class NodeModel(BaseModel):
    id: str
    type: str  # input, router, llm, image, db, aggregator
    metadata: Optional[Dict[str, Any]] = None

class EdgeModel(BaseModel):
    from_node: str = Field(..., alias="from")
    to: str | List[str]
    condition: Optional[str] = None

class QueueBandwidth(BaseModel):
    max_messages_per_second: Optional[int] = None
    max_requests_per_minute: Optional[int] = None
    max_tokens_per_minute: Optional[int] = None

class QueueModel(BaseModel):
    id: str
    from_node: str = Field(..., alias="from")
    to: str
    bandwidth: Optional[QueueBandwidth] = None

class SourceModel(BaseModel):
    id: str
    kind: str  # llm, image, db, api
    config: Dict[str, Any]

class WorkflowSpecModel(BaseModel):
    nodes: List[NodeModel]
    edges: List[EdgeModel]
    queues: List[QueueModel]
    sources: List[SourceModel]
    start_node: str
```

### GraphState Pattern

```python
# runtime/state.py
from typing import TypedDict, Any

class GraphState(TypedDict, total=False):
    user_input: str
    intent: str
    text_result: str
    image_result: Any
    db_result: Any
    final_output: Any
    tokens_used: int
    cost: float
    metadata: dict
```

---

## 5. Data Models

### Core Models

```python
# api/models/workflow_model.py
from pydantic import BaseModel, Field
from typing import List, Optional, Any, Dict

class NodeModel(BaseModel):
    """Represents a node in the workflow graph."""
    id: str
    type: str  # input, router, llm, image, db, aggregator
    metadata: Optional[Dict[str, Any]] = None

class EdgeModel(BaseModel):
    """Represents a connection between nodes."""
    from_node: str = Field(..., alias="from")
    to: str | List[str]
    condition: Optional[str] = None

class QueueBandwidth(BaseModel):
    """Bandwidth configuration for rate limiting."""
    max_messages_per_second: Optional[int] = None
    max_requests_per_minute: Optional[int] = None
    max_tokens_per_minute: Optional[int] = None

class QueueModel(BaseModel):
    """Represents a rate-limited queue between nodes."""
    id: str
    from_node: str = Field(..., alias="from")
    to: str
    bandwidth: Optional[QueueBandwidth] = None

class SourceModel(BaseModel):
    """External service configuration (LLM, DB, etc.)."""
    id: str
    kind: str  # llm, image, db, api
    config: Dict[str, Any]

class WorkflowSpecModel(BaseModel):
    """Complete workflow specification."""
    nodes: List[NodeModel]
    edges: List[EdgeModel]
    queues: List[QueueModel]
    sources: List[SourceModel]
    start_node: str
```

```python
# runtime/state.py
from typing import TypedDict, Any

class GraphState(TypedDict, total=False):
    """State passed between nodes during execution."""
    user_input: str
    intent: str
    text_result: str
    image_result: Any
    db_result: Any
    final_output: Any
    tokens_used: int
    cost: float
    metadata: dict
```

---

## 6. Security & Compliance

### Authentication

**API Key Authentication (Server-to-Server):**

```python
# core/security.py
from fastapi import Header, HTTPException

async def get_api_key(x_api_key: str = Header(...)):
    """Validate API key for workflow operations."""
    if not validate_api_key(x_api_key):
        raise HTTPException(status_code=401, detail="Invalid API key")
    return x_api_key
```

### Environment Variables

```python
# Load sensitive configuration from environment
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
DATABASE_URL = os.getenv("DATABASE_URL")
REDIS_URL = os.getenv("REDIS_URL")
```

### Error Handling

```python
# Common HTTP error responses
400 Bad Request   # Invalid workflow spec
401 Unauthorized  # Invalid API key
404 Not Found     # Workflow/source not found
422 Unprocessable # Validation errors
500 Internal      # Unexpected errors
```

---

## 7. Quick Reference

### Most Common Operations

| Task | Code |
|------|------|
| **Validate workflow** | `errors = validate_workflow(spec)` |
| **Build graph** | `graph = build_graph_from_json(spec)` |
| **Execute workflow** | `result = graph.invoke(initial_state)` |
| **Get node by type** | `node = create_node_callable(node_type, metadata)` |
| **Check rate limit** | `check_rate_limit(queue_id)` |

### ID Prefixes

| Entity | Prefix | Example |
|--------|--------|---------|
| Workflow | `wf_` | `wf_abc123` |
| Node | `node_` | `node_xyz789` |
| Queue | `queue_` | `queue_def456` |
| Source | `src_` | `src_ghi012` |

### Environment Variables

```bash
# Database (optional)
DATABASE_URL="postgresql://user:pass@localhost:5432/agentflow"

# AI Services
OPENAI_API_KEY="sk-..."
OPENAI_MODEL="gpt-4"

# Redis (for rate limiting)
REDIS_URL="redis://localhost:6379"

# Backend
AGENTFLOW_CORE_URL="http://localhost:8000"

# Frontend
NEXT_PUBLIC_CORE_URL="http://localhost:8000"
```

### Docker Commands

```bash
# Start development environment
docker-compose up -d

# View logs
docker-compose logs -f backend

# Run tests
docker-compose exec backend pytest

# Start frontend
cd frontend/agentflow-studio && npm run dev
```

---

## Summary

**Key Takeaways**:
1. ✅ JSON-driven workflow orchestration
2. ✅ LangGraph runtime for execution
3. ✅ Node types: input, router, llm, image, db, aggregator
4. ✅ Queue-based rate limiting with bandwidth controls
5. ✅ Use functional services over classes
6. ✅ Validate all inputs with Pydantic
7. ✅ React Flow for visual workflow design

**Questions?** See existing code in `/backend/agentflow_core`, `/frontend/agentflow-studio`, or `/docs` for real examples.

---

**Last Updated**: December 6, 2025  
**Maintained by**: AgentFlow Engineering Team
