```chatagent
# AgentFlow Agent Context

> **For AI Agents**: This file contains AgentFlow-specific context that all agents should be aware of. Modern LLMs already know Python, FastAPI, React, LangGraph, and TypeScript fundamentals - this document focuses ONLY on what makes AgentFlow unique.

## Project Identity

**AgentFlow**: JSON-Driven Workflow Orchestration Engine + Visual Designer  
**Stack**: FastAPI (Python 3.11+) • LangGraph • Next.js 16 • React Flow • TypeScript  
**Primary Instruction File**: `.github/instructions/agentflow-rules.instructions.md`

---

## Critical AgentFlow-Specific Patterns

### 1. JSON-First Workflow Specification

**All workflows are defined as JSON WorkflowSpec:**

```json
{
  "nodes": [...],
  "edges": [...],
  "queues": [...],
  "sources": [...],
  "start_node": "input"
}
```

**Hierarchy:**
```
WorkflowSpec
  ├── Nodes (input, router, llm, image, db, aggregator)
  ├── Edges (connections with optional conditions)
  ├── Queues (rate limiting + bandwidth)
  └── Sources (LLM, Image, DB, API configs)
```

### 2. Node Types

| Node Type | Purpose |
|-----------|---------|
| `input` | Entry point, accepts user input |
| `router` | Determines routing via LLM or rules |
| `llm` | Text generation / reasoning |
| `image` | DALL·E or other image generation |
| `db` | Runs SQL queries |
| `aggregator` | Combines results into final output |

### 3. LangGraph Runtime

**Workflows are converted to LangGraph graphs:**

```python
# runtime/builder.py
def build_graph_from_json(spec: WorkflowSpecModel) -> CompiledGraph:
    graph = StateGraph(GraphState)
    
    # Add nodes
    for node in spec.nodes:
        callable_fn = create_node_callable(node)
        graph.add_node(node.id, callable_fn)
    
    # Add edges
    for edge in spec.edges:
        if edge.condition:
            graph.add_conditional_edges(edge.from_node, ...)
        else:
            graph.add_edge(edge.from_node, edge.to)
    
    # Set entry point
    graph.set_entry_point(spec.start_node)
    
    return graph.compile()
```

### 4. GraphState Pattern

**State passed between nodes:**

```python
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

### 5. Queue Bandwidth Configuration

**Rate limiting for node-to-node communication:**

```json
{
  "id": "queue_llm",
  "from": "router",
  "to": "llm",
  "bandwidth": {
    "max_messages_per_second": 2,
    "max_requests_per_minute": 60,
    "max_tokens_per_minute": 20000
  }
}
```

### 6. Source Configuration

**Reusable external service configs:**

```json
{
  "id": "llm-openai",
  "kind": "llm",
  "config": {
    "model_name": "gpt-4",
    "api_key_env": "OPENAI_API_KEY"
  }
}
```

---

## System Architecture

### Main Components

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

### Directory Structure

```
backend/agentflow_core/
├── api/             # FastAPI routes
│   ├── routes/      # /workflows, /sources, /health
│   └── models/      # Pydantic models
├── runtime/         # LangGraph runtime engine
│   ├── builder.py   # WorkflowSpec → LangGraph
│   ├── executor.py  # Run workflows
│   ├── validator.py # Schema + logic validation
│   └── state.py     # GraphState definitions
├── nodes/           # Node type implementations
├── sources/         # External service adapters
└── utils/           # Logger, error handler

frontend/agentflow-studio/
├── app/             # Next.js App Router
│   ├── designer/    # Workflow designer page
│   ├── sources/     # Source manager
│   └── api/         # API route proxies
├── components/      # React Flow canvas, panels
└── lib/             # Types, schema, mappers
```

---

## Key Workflows

### Workflow Validation Flow
1. User creates workflow in Studio
2. Frontend generates WorkflowSpec JSON
3. POST to `/workflows/validate`
4. Backend validates schema + logic
5. Return errors or success

### Workflow Execution Flow
1. POST to `/workflows/execute` with WorkflowSpec + initial_state
2. Backend validates workflow
3. Build LangGraph from JSON
4. Execute via `graph.invoke(initial_state)`
5. Return final_state

### Visual Designer Flow
1. Drag nodes from NodePalette
2. Connect nodes on WorkflowCanvas
3. Configure sources in SourceEditor
4. Set queue bandwidth in QueueEditor
5. Preview JSON in JsonPreview
6. Validate and execute

---

## ID Prefixes

| Entity | Prefix | Example |
|--------|--------|---------|
| Workflow | `wf_` | `wf_abc123` |
| Node | `node_` | `node_xyz789` |
| Queue | `queue_` | `queue_def456` |
| Source | `src_` | `src_ghi012` |

---

## API Endpoints

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/workflows/validate` | POST | Validate workflow spec |
| `/workflows/execute` | POST | Execute workflow |
| `/sources` | GET/POST | List/create sources |
| `/health` | GET | Health check |

---

## Reference Documentation

- `.github/instructions/agentflow-rules.instructions.md` - Project rules & patterns
- `/docs/srs.md` - Software Requirements Specification
- `/docs/hld.md` - High-Level Design
- `/docs/lld.md` - Low-Level Design
- `/docs/API_Spec.md` - API Specification
- `/docs/BACKEND-SPEC.md` - Backend Specification
- `/docs/FRONTEND-SPEC.md` - Frontend Specification
- `/docs/WORKFLOW-SCHEMA.md` - JSON Schema documentation
```
