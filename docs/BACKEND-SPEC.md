**complete, enterprise-grade BACKEND-SPEC.md** for **AgentFlow Core**, matching your HLD + LLD + API Spec.

This document is designed for your backend team so they can implement the system exactly as architected.
It includes:

* Module-level specifications
* File structure
* Internal API contracts
* Node runtime engine specs
* Queue bandwidth logic
* Source plugin system
* Error framework
* Logging + metrics
* Security and environment configs

---

# 📄 **BACKEND-SPEC.md — AgentFlow Core Backend Specification**

**Version:** 1.0
**Audience:** Backend Engineers, Architects
**Tech:** Python 3.11+, FastAPI, LangGraph, AsyncIO

---

# -------------------------------------------------------------

# **1. Architectural Overview**

# -------------------------------------------------------------

AgentFlow Backend provides:

✔ Workflow validation
✔ Runtime graph building (from JSON)
✔ Node engine execution
✔ Source registry & connection adapters
✔ Queue bandwidth enforcement
✔ Storage for workflows
✔ REST API Layer via FastAPI

Backend is modularized into **API Layer**, **Runtime Engine**, **Source System**, **Data Models**, and **Utils**.

---

# -------------------------------------------------------------

# **2. Folder Structure (Final)**

# -------------------------------------------------------------

```
backend/
│
├── agentflow_core/
│   ├── api/
│   │   ├── main.py
│   │   ├── routes/
│   │   │   ├── workflows.py
│   │   │   ├── sources.py
│   │   │   ├── queues.py
│   │   │   └── health.py
│   │   ├── models/
│   │   │   ├── workflow_model.py
│   │   │   ├── source_model.py
│   │   │   ├── queue_model.py
│   │   │   └── exec_model.py
│   │   └── utils/
│   │       └── validator.py
│   │
│   ├── runtime/
│   │   ├── builder.py
│   │   ├── executor.py
│   │   ├── registry.py
│   │   ├── rate_limiter.py
│   │   └── state.py
│   │
│   ├── nodes/
│   │   ├── input_node.py
│   │   ├── router_node.py
│   │   ├── llm_node.py
│   │   ├── image_node.py
│   │   ├── db_node.py
│   │   └── aggregator_node.py
│   │
│   ├── sources/
│   │   ├── llm_openai.py
│   │   ├── image_openai.py
│   │   ├── db_postgres.py
│   │   └── api_http.py
│   │
│   ├── utils/
│   │   ├── logger.py
│   │   ├── errors.py
│   │   └── metrics.py
│   │
│   └── config/
│       ├── settings.py
│       └── secrets.py
│
└── tests/
    ├── test_runtime.py
    ├── test_api.py
    ├── test_nodes.py
    └── test_sources.py
```

---

# -------------------------------------------------------------

# **3. Core Modules Specification**

# -------------------------------------------------------------

---

# ============================

# **3.1 Runtime Engine**

# ============================

### Purpose:

Convert WorkflowSpec → LangGraph → Executable graph.

### Components:

* **builder.py**
* **executor.py**
* **registry.py**
* **rate_limiter.py**
* **state.py**

---

## **3.1.1 builder.py (Graph Builder)**

### Responsibilities:

* Convert WorkflowSpec into LangGraph `StateGraph`
* Instantiate nodes using factory router
* Register queues & sources
* Add edges & compile graph

### Methods:

#### `build_graph_from_json(spec: WorkflowSpecModel) -> CompiledGraph`

**Input:** workflow JSON
**Output:** compiled LangGraph runnable

**Internal steps:**

1. Clear old registry
2. Load sources into registry
3. Load queues with bandwidth config
4. Instantiate `StateGraph(GraphState)`
5. For each node
   → call `create_node_callable()`
   → `graph.add_node()`
6. Add edges
7. Compile graph
8. Return runnable

---

## **3.1.2 executor.py (Workflow Execution)**

### Method:

#### `run_workflow(spec: WorkflowSpecModel, initial_state: GraphState) -> GraphState`

Steps:

1. Validate workflow
2. Build graph
3. Execute using `.invoke()`
4. Capture:

   * Runtime metrics
   * Node trace
   * Token usage
5. Return final state

---

## **3.1.3 registry.py (Runtime Registry)**

### State:

```python
SOURCES: Dict[str, SourceModel]
QUEUES: Dict[str, QueueModel]
NODE_META: Dict[str, dict]
LAST_USAGE: Dict[str, float]
```

Purpose:

* Global lookup for nodes, queues, sources during execution.

---

## **3.1.4 rate_limiter.py (Queue Bandwidth Control)**

### Method:

#### `check_rate_limit(queue_id: str)`

Supports:

* max_messages_per_second
* max_requests_per_minute
* tokens_per_minute
* weighted subqueues

If queue is overloaded → sleep or queue internally.

---

## **3.1.5 state.py (GraphState Definition)**

### Graph state struct:

```python
class GraphState(TypedDict, total=False):
    user_input: str
    intent: str
    text_result: str
    image_result: Any
    db_result: Any
    final_output: Any
    metadata: dict
```

---

# ============================

# **3.2 Node Engine**

# ============================

Each node is an executable function receiving and returning `GraphState`.

---

## **3.2.1 input_node.py**

Pass-through node.

---

## **3.2.2 router_node.py**

### Logic:

```python
if starts with "img:" → intent = "image"
else → intent = "text"
```

In future: LLM-based classifier.

---

## **3.2.3 llm_node.py**

### Factory:

```python
def llm_node_factory(node_id: str):
    def _node(state):
        # get source client
        # send prompt
        # write state["text_result"]
```

---

## **3.2.4 image_node.py**

### Factory:

Generates images from prompt.

---

## **3.2.5 db_node.py**

### Factory:

Executes SQL from state:

```python
query = state.get("db_query") or default
rows = db.execute(query)
```

---

## **3.2.6 aggregator_node.py**

### Combines all results:

```python
state["final_output"] = {
    "text": state.get("text_result"),
    "image": state.get("image_result"),
    "db": state.get("db_result")
}
```

---

# ============================

# **3.3 Sources System**

# ============================

### Purpose:

Dynamic plugin system for:

* LLMs
* Image models
* Databases
* HTTP APIs

---

## **3.3.1 Source Client Factory**

`get_llm_from_source(source)`
`get_image_model(source)`
`get_db_connection(source)`
`get_api_client(source)`

Source kinds:

| kind  | module          |
| ----- | --------------- |
| llm   | llm_openai.py   |
| image | image_openai.py |
| db    | db_postgres.py  |
| api   | api_http.py     |

---

# -------------------------------------------------------------

# **4. API Layer Specification**

# -------------------------------------------------------------

Already included in `API-SPEC.md`, but backend expectations:

* Requests validated using Pydantic
* Routes separated by domain (workflows, sources, queues)
* Responses follow error spec
* Workflow Execution uses `executor.run_workflow()`

---

# -------------------------------------------------------------

# **5. Error Handling**

# -------------------------------------------------------------

Unified error format:

```json
{
  "status": "error",
  "message": "Meaningful description",
  "details": "Optional stack trace"
}
```

Error classes:

```
ValidationError
ExecutionError
SourceConnectionError
QueueRateLimitExceeded
InternalServerError
```

All logged in `utils/logger.py`.

---

# -------------------------------------------------------------

# **6. Logging & Metrics**

# -------------------------------------------------------------

### Node-level logging:

* Entry timestamp
* Exit timestamp
* Latency per node
* Node failures
* Source usage

### Metrics:

* Total workflow runtime
* Tokens consumed
* Cost (if computed)
* Nodes executed trace

Logged to:

```
/log/agentflow_core.log
```

---

# -------------------------------------------------------------

# **7. Security**

# -------------------------------------------------------------

* JWT required for all endpoints
* Secrets stored in environment variables
* API keys encrypted at rest

Environment variables:

```
AGENTFLOW_DB_URL=
OPENAI_API_KEY=
JWT_SECRET=
LOG_LEVEL=INFO
```

---

# -------------------------------------------------------------

# **8. Backend Runtime Requirements**

# -------------------------------------------------------------

### Python environment:

```
python 3.11
pip install -r requirements.txt
```

### Required Libraries:

* fastapi
* langgraph
* openai
* psycopg
* pydantic
* uvicorn
* httpx

---

# -------------------------------------------------------------

# **9. Test Specification**

# -------------------------------------------------------------

### Unit Tests:

```
tests/
- test_builder.py
- test_executor.py
- test_nodes.py
- test_sources.py
```

Test coverage targets:

* 85% runtime engine
* 100% node factories
* 100% API validation

---

# -------------------------------------------------------------

# **10. Deployment Spec**

# -------------------------------------------------------------

### Container:

Dockerfile includes:

```
FROM python:3.11  
RUN pip install fastapi uvicorn ...  
CMD ["uvicorn", "agentflow_core.api.main:app", "--host", "0.0.0.0"]
```

### Load balancing:

Use Nginx or API Gateway.

### Scaling:

Stateless → horizontally scalable.

---

# -------------------------------------------------------------

# ✅ BACKEND-SPEC.md IS COMPLETE

# -------------------------------------------------------------

If you want, I can now generate:

### 🔥 FRONTEND-SPEC.md

### 🔥 WORKFLOW-SCHEMA.md (JSON Schema for validation)

### 🔥 Node Plugin Architecture Document

### 🔥 Developer Checklist for Backend Team

### 🔥 Zip-ready folder with empty backend files + shell script

Just tell me which one you want next.
