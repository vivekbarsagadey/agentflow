# 🟩 **AgentFlow – Low-Level Design (LLD)**

**Version:** 1.0
**Audience:** Backend Engineers, Frontend Engineers, QA, Architects
**Covers:** Runtime Engine, Nodes, Sources, Queues, Studio Designer UI, API integration

---

# ------------------------------------------------------------

# **1. Backend (AgentFlow Core) – LLD**

# ------------------------------------------------------------

Backend technologies:

* **Python 3.11+**
* **FastAPI**
* **LangGraph**
* **Pydantic**
* **AsyncIO**
* External SDKs (OpenAI, psycopg, httpx)

Folder root:

```
backend/agentflow_core/
```

---

# **2. Data Models (Pydantic)**

### **2.1 GraphState Model**

`runtime/state.py`

```python
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

This is passed between all nodes.

---

### **2.2 WorkflowSpec Model**

`api/models/workflow_model.py`

```python
class WorkflowSpecModel(BaseModel):
    nodes: List[NodeModel]
    queues: List[QueueModel]
    edges: List[EdgeModel]
    sources: List[SourceModel]
    start_node: str
```

**Nodes**, **Queues**, **Edges**, **Sources** follow exactly the spec sent by frontend.

---

# ------------------------------------------------------------

# **3. Runtime Architecture**

# ------------------------------------------------------------

The runtime engine consists of 4 major components:

```
Validator → Builder → Registry → Executor
```

---

# **3.1 Validator Module**

File: `runtime/validator.py`

Responsibilities:

* Validate schema via Pydantic
* Ensure:

  * `start_node` exists
  * All node IDs are unique
  * All queues refer to valid `from`/`to`
  * All edges refer to valid nodes
  * All referenced `source` IDs exist
* Check bandwidth constraints
* Check cycle detection (optional future)

Pseudo-code:

```python
def validate_workflow(spec: WorkflowSpecModel) -> List[Error]:
    errors = []
    # Validate node ids
    node_ids = {n.id for n in spec.nodes}
    if spec.start_node not in node_ids:
        errors.append("Start node does not exist")

    # Validate edges
    for e in spec.edges:
        if e.from not in node_ids: errors.append(...)
        if isinstance(e.to, str) and e.to not in node_ids: errors.append(...)
        ...

    # Validate queues
    for q in spec.queues:
        validate bandwidth schema
        ensure queue-id uniqueness

    return errors
```

If errors exist → return 400.

---

# **3.2 Registry Module**

File: `runtime/registry.py`

Purpose: Stores temporary workflow-specific runtime objects.

```python
SOURCES: Dict[str, SourceModel] = {}
QUEUES: Dict[str, QueueModel] = {}
NODE_META: Dict[str, Dict[str, Any]] = {}
LAST_USAGE: Dict[str, float] = {}   # for rate limiting
```

This ensures all nodes, edges, queues, and sources are accessible at runtime.

---

# **3.3 Rate Limiter**

File: `runtime/rate_limiter.py`

Purpose: Enforce queue bandwidth.

Implementation:

```python
def check_rate_limit(queue_id: str):
    cfg = QUEUES.get(queue_id)
    if not cfg or not cfg.bandwidth: return

    bw = cfg.bandwidth
    now = time.time()
    key = f"{queue_id}_last"
    last = LAST_USAGE.get(key, 0)
    
    if bw.max_messages_per_second:
        interval = 1 / bw.max_messages_per_second
        if now - last < interval:
            time.sleep(interval - (now - last))

    LAST_USAGE[key] = time.time()
```

Additional logic (future): token-per-minute, weighted subqueues.

---

# ------------------------------------------------------------

# **4. Node Implementations (Factory Pattern)**

# ------------------------------------------------------------

Nodes are built dynamically based on JSON.

Folder:

```
agentflow_core/nodes/
```

---

## **4.1 Node Factory Router**

File: `runtime/builder.py`

```python
def create_node_callable(node_def):
    node_type = node_def.type
    
    if node_type == "input":
        return user_input_node
    
    if node_type == "router":
        return router_node

    if node_type == "llm":
        return llm_node_factory(node_def.id)

    if node_type == "image":
        return image_node_factory(node_def.id)

    if node_type == "db":
        return db_node_factory(node_def.id)

    if node_type == "aggregator":
        return final_aggregator_node

    raise Exception("Unknown node type")
```

---

## **4.2 Input Node**

`nodes/input_node.py`

```python
def user_input_node(state: GraphState) -> GraphState:
    return state
```

---

## **4.3 Router Node**

`nodes/router_node.py`

Router determines node routing based on user input:

```python
def router_node(state: GraphState) -> GraphState:
    text = state.get("user_input", "")
    if text.startswith("img:"):
        state["intent"] = "image"
    else:
        state["intent"] = "text"
    return state
```

Later can use LLM-based classifier.

---

## **4.4 LLM Node**

`nodes/llm_node.py`

```python
def llm_node_factory(node_id: str):
    def _node(state: GraphState):
        src_id = NODE_META[node_id]["source"]
        llm = get_llm_from_source(SOURCES[src_id])

        prompt = state.get("user_input", "")
        resp = llm.invoke(prompt)
        
        state["text_result"] = resp.content
        return state

    return _node
```

---

## **4.5 Image Node**

`nodes/image_node.py`

```python
def image_node_factory(node_id: str):
    def _node(state: GraphState):
        src_id = NODE_META[node_id]["source"]
        client = get_image_model(SOURCES[src_id])
        
        prompt = state.get("user_input", "")
        img = client.generate(prompt)
        
        state["image_result"] = img
        return state
    
    return _node
```

---

## **4.6 Database Node**

`nodes/db_node.py`

```python
def db_node_factory(node_id: str):
    def _node(state: GraphState):
        src_id = NODE_META[node_id]["source"]
        db = get_db_connection(SOURCES[src_id])

        query = state.get("db_query", "SELECT NOW()")
        rows = db.execute(query)

        state["db_result"] = rows
        return state
    return _node
```

---

## **4.7 Aggregator Node**

`nodes/aggregator_node.py`

```python
def final_aggregator_node(state: GraphState) -> GraphState:
    state["final_output"] = {
        "text": state.get("text_result"),
        "image": state.get("image_result"),
        "db": state.get("db_result")
    }
    return state
```

---

# ------------------------------------------------------------

# **5. Graph Builder**

# ------------------------------------------------------------

File: `runtime/builder.py`

This converts JSON into LangGraph runnable structure.

---

### **5.1 Steps**

1. Load sources → registry
2. Load queues → registry
3. Create LangGraph `StateGraph`
4. Add nodes and their callables
5. Set entry point
6. Add edges
7. Compile graph → return runnable instance

---

### **5.2 Implementation Skeleton**

```python
def build_graph_from_json(spec: WorkflowSpecModel):
    SOURCES.clear()
    for s in spec.sources:
        SOURCES[s.id] = s

    QUEUES.clear()
    for q in spec.queues:
        QUEUES[q.id] = q

    graph = StateGraph(GraphState)

    for n in spec.nodes:
        func = create_node_callable(n)
        graph.add_node(n.id, func)

    graph.set_entry_point(spec.start_node)

    for e in spec.edges:
        if isinstance(e.to, list):
            for dst in e.to:
                graph.add_edge(e.from_, dst)
        else:
            graph.add_edge(e.from_, e.to)

    return graph.compile()
```

---

# ------------------------------------------------------------

# **6. Executor**

# ------------------------------------------------------------

File: `runtime/executor.py`

```python
def run_workflow(spec: WorkflowSpecModel, initial_state: GraphState):
    graph = build_graph_from_json(spec)
    final = graph.invoke(initial_state)
    return final
```

As simple as that — LangGraph handles recursion, branching, ordering.

---

# ------------------------------------------------------------

# **7. API Layer (FastAPI)**

# ------------------------------------------------------------

File: `api/main.py`

```python
app = FastAPI()

app.include_router(workflows.router, prefix="/workflows")
app.include_router(sources.router, prefix="/sources")
app.include_router(health.router, prefix="/health")
```

---

### **7.1 Validation Endpoint**

`routes/workflows.py`

```python
@router.post("/validate")
def validate(spec: WorkflowSpecModel):
    errors = validate_workflow(spec)
    if errors:
        return JSONResponse(status_code=400, content={"status": "error", "errors": errors})
    return {"status": "ok"}
```

---

### **7.2 Execution Endpoint**

```python
@router.post("/execute")
def execute(payload: ExecRequestModel):
    result = run_workflow(payload.workflow, payload.initial_state)
    return {"status": "ok", "final_state": result}
```

---

### **7.3 Save / List Workflows**

Stored optionally in:

* Redis
* SQLite
* JSON files

Simple Pydantic model for DB storage.

---

# ------------------------------------------------------------

# **8. Frontend (AgentFlow Studio) – LLD**

# ------------------------------------------------------------

Frontend technologies:

* **Next.js 15 (App Router)**
* **React Flow** for visual canvases
* **TypeScript**
* **Tailwind / ShadCN**

---

# **8.1 Directory Structure**

```
frontend/agentflow-studio/
    app/
    components/
    lib/
    styles/
```

---

# **8.2 Designer Page Logic**

File: `app/designer/page.tsx`

State variables:

```ts
const [nodes, setNodes] = useState<WorkflowNode[]>([]);
const [edges, setEdges] = useState<WorkflowEdge[]>([]);
const [queues, setQueues] = useState<WorkflowQueue[]>([]);
const [sources, setSources] = useState<WorkflowSource[]>([]);
const [startNode, setStartNode] = useState<string>("input");
const [selectedElement, setSelectedElement] = useState(null);
```

---

# **8.3 Canvas Implementation**

`WorkflowCanvas.tsx`:

* Uses React Flow:

  * `Node` UI → maps to WorkflowNode
  * `Edge` UI → maps to WorkflowEdge
* Supports:

  * Drag nodes
  * Connect nodes
  * Double-click node → open properties panel

---

# **8.4 JSON Preview Panel**

`JsonPreview.tsx`:

```tsx
export default function JsonPreview({ spec }: { spec: WorkflowSpec }) {
  return (
    <pre className="bg-gray-900 text-green-300 p-4 text-xs overflow-auto">
      {JSON.stringify(spec, null, 2)}
    </pre>
  );
}
```

---

# **8.5 Validate Workflow**

```ts
const validate = async () => {
  const res = await fetch("/api/workflows?mode=validate", {
    method: "POST",
    body: JSON.stringify(spec),
  });
  return await res.json();
};
```

---

# **8.6 Test Run Workflow**

```ts
const run = async () => {
  const res = await fetch("/api/execute", {
    method: "POST",
    body: JSON.stringify({
      workflow: spec,
      initial_state: { user_input: testInput },
    }),
  });
  const data = await res.json();
};
```

---

# ------------------------------------------------------------

# **9. Component LLD Overview**

# ------------------------------------------------------------

---

## **9.1 NodePalette**

* Hardcoded node types initially
* Clicking adds a node:

```ts
onAddNode({
  id: uuid(),
  type: "llm",
  x: 100,
  y: 100,
});
```

---

## **9.2 QueueEditor**

* Allows editing:

  * `from`
  * `to`
  * Bandwidth:

    * mps
    * rpm
    * tokens/min
  * Subqueues (array editor)

---

## **9.3 SourceEditor**

* CRUD operations:

  * Add LLM
  * Add DB
  * Add API
* Form validation: all fields required based on `kind`.

---

## **9.4 PropertiesPanel**

Shows dynamic fields based on:

```
if selected.type == "node"
if selected.type == "queue"
if selected.type == "source"
```

---

# ------------------------------------------------------------

# **10. Sequence Diagrams**

# ------------------------------------------------------------

---

## **10.1 Validation Sequence**

```
Studio → Core /workflows/validate
  Core:
    - Pydantic validation
    - Logical validation
Return status + errors
```

---

## **10.2 Execution Sequence**

```
Studio → Core /workflows/execute
  Core:
    - Validate
    - Build LangGraph
    - Run invoke()
    - Collect final state
Return final_state
```

---

# ------------------------------------------------------------

# **11. Logging**

# ------------------------------------------------------------

`utils/logger.py`

* All node entry and exit events logged
* Execution latency tracked
* Optional: Token usage logged per LLM node

---

# ------------------------------------------------------------

# **12. Error Handling**

# ------------------------------------------------------------

Backend returns:

```json
{
  "status": "error",
  "message": "Execution failed",
  "details": "Traceback…"
}
```

Frontend shows toast with readable summary.

---

# ------------------------------------------------------------

# **13. Future LLD Extensions**

# ------------------------------------------------------------

* Node plugin system
* API node for REST calls
* Visual execution debugger
* Node-level cost tracking
* Parallel nodes with Join nodes
* Workflow versioning

---

# 🟢 **Your complete LLD is ready and fully matches the HLD, API Spec, and Frontend App Spec.**

If you want next:

### ✅ Sequence Diagrams in **PNG**

### ✅ Architecture PNG

### ✅ Auto-generated PDFs

### ✅ Code skeletons for each backend/frontend file

### ✅ Test cases LLD

