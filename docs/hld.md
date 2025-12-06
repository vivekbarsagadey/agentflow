
# 🟦 **AgentFlow – High-Level Design (HLD)**

**Version:** 1.0
**Prepared for:** System Architects, Backend Engineers, Frontend Engineers
**Tech Stack:** Python (FastAPI + LangGraph), Next.js Studio Designer, JSON workflow specs

---

# **1. System Overview**

**AgentFlow** is a **JSON-driven workflow orchestration engine** that converts declarative workflow specifications into **executable multi-agent graphs**.

It has two major components:

---

## **1.1 AgentFlow Core (Backend)**

Built using **Python, FastAPI, and LangGraph**.
Core functionalities:

* Parse and validate a `WorkflowSpec` (JSON)
* Build a LangGraph runtime graph dynamically
* Configure:

  * Nodes (LLM, Image, DB, Router, Aggregator)
  * Edges (with conditions)
  * Queues (with bandwidth / rate limits)
  * Sources (OpenAI, DBs, APIs)
* Execute workflows and return structured final state
* Provide REST endpoints for validate / execute / save / retrieve workflows

---

## **1.2 AgentFlow Studio (Frontend Designer)**

A visual workflow builder built with **Next.js (App Router)**.

Studio enables users to:

* Add nodes visually (drag & drop)
* Connect nodes to form workflows
* Configure sources (LLMs, DBs, APIs)
* Set queue bandwidth limits
* Preview JSON spec in real-time
* Validate workflow (via backend)
* Execute workflow with test inputs

---

# **2. High-Level Architecture Diagram**

```
+---------------------------------------------------------------+
|                         AgentFlow Studio                      |
|                     (Next.js Visual Designer)                 |
|                                                               |
|   Drag & Drop UI  ----> WorkflowSpec(JSON) ----> API Proxy    |
|                                                               |
+-------------------------------|-------------------------------+
                                |
                                v
+-------------------------------|-------------------------------+
|                         AgentFlow Core                        |
|                    (FastAPI + Python + LangGraph)             |
|                                                               |
|   +-------------------+     +------------------------------+  |
|   | Validator Module  | --> | Runtime Graph Builder        |--|
|   +-------------------+     +------------------------------+  |
|            |                           |                     |
|            v                           v                     |
|   +-------------------+     +------------------------------+  |
|   | Queue Manager     |     | Node Registry (LLM, DB, etc.)|  |
|   +-------------------+     +------------------------------+  |
|            |                           |                     |
|            v                           v                     |
|   +--------------------------------------------------------+ |
|   | Executor (LangGraph runtime.invoke)                    | |
|   +--------------------------------------------------------+ |
|                                                               |
+-------------------------------|-------------------------------+
                                |
                                |
                                v
                       Final State JSON Output
```

---

# **3. Core Concepts**

---

## **3.1 WorkflowSpec (JSON Blueprint)**

The entire system is defined by a single JSON structure containing:

* **Nodes**
* **Edges**
* **Queues (with bandwidth limits)**
* **Sources (LLM, API, DB)**
* **Start Node**

AgentFlow Core uses this JSON to dynamically build the execution graph.

---

## **3.2 Nodes**

Supported built-in node types:

| Node Type      | Purpose                                        |
| -------------- | ---------------------------------------------- |
| `input`        | Entry point, accepts user input                |
| `router`       | Determines routing conditions via LLM or rules |
| `llm`          | Text generation / reasoning                    |
| `image`        | DALL·E or other model-based image generation   |
| `db`           | Runs SQL queries                               |
| `api` (future) | External API calls                             |
| `aggregator`   | Combines values into a final output            |

Nodes are converted into **LangGraph functions** at runtime.

---

## **3.3 Edges**

Edges define connections between nodes.
They support:

* Unconditional edges
* Conditional edges (`condition: intent == 'image'`)
* Parallel edges (list of nodes)

---

## **3.4 Queues**

Queues act as **rate-limited message channels**.

Supports:

* `max_messages_per_second`
* `max_requests_per_minute`
* `max_tokens_per_minute`
* `sub_queues` with weighted distribution

Each edge maps to a queue (optional).

---

## **3.5 Sources**

Reusable external integrations:

* OpenAI LLM (`model`, `api_key_env`)
* DALL·E image generator
* Postgres DB (`dsn_env`)
* REST API endpoints
* IoT devices (future)

---

# **4. High-Level Module Design**

---

## **4.1 Backend Modules (AgentFlow Core)**

| Module                      | Description                                    |
| --------------------------- | ---------------------------------------------- |
| **runtime/builder.py**      | Converts WorkflowSpec → LangGraph graph        |
| **runtime/validator.py**    | Schema + logical validation                    |
| **runtime/executor.py**     | Invokes compiled graph and returns final state |
| **runtime/registry.py**     | Stores active sources, queues, node metadata   |
| **runtime/rate_limiter.py** | Enforces bandwidth and queue rules             |
| **nodes/**                  | Contains implementations of each node type     |
| **sources/**                | OpenAI, DB, image, HTTP connectors             |
| **api/routes/**             | FastAPI endpoints for validate, execute, save  |

---

## **4.2 Frontend Modules (AgentFlow Studio)**

| Module                 | Description                         |
| ---------------------- | ----------------------------------- |
| **WorkflowCanvas.tsx** | Graph canvas for nodes/edges        |
| **NodePalette.tsx**    | Drag-and-drop node tools            |
| **QueueEditor.tsx**    | Bandwidth/subqueue configuration UI |
| **SourceEditor.tsx**   | CRUD for sources                    |
| **JsonPreview.tsx**    | Real-time JSON preview              |
| **Proxy API routes**   | Connect Studio → Core backend       |

---

# **5. Workflow Execution Overview**

---

### **5.1 Studio → Core Interaction**

1. User creates workflow visually
2. JSON Spec is generated
3. User clicks **Validate**
4. Studio sends JSON → `/workflows/validate`
5. Backend returns success or detailed errors

---

### **5.2 Execution Pipeline**

1. Studio sends:

```json
{
  "workflow": { ... },
  "initial_state": { "user_input": "Hello" }
}
```

2. Backend validates JSON
3. Backend builds runtime graph
4. Backend executes graph step-by-step
5. Queue manager enforces rate limits
6. Node callables execute LLMs, DBs, APIs
7. Aggregator builds final output
8. Backend returns:

```json
{
  "status": "ok",
  "final_state": { ... }
}
```

---

# **6. Deployment Architecture**

---

### **6.1 Recommended Deployment**

```
+----------------------+     +-------------------------+
| AgentFlow Studio     | --> | AgentFlow Core (FastAPI)|
| Next.js Static Build |     | Containerized API       |
+----------------------+     +-------------------------+
                                     |
                                     v
                            External Services (LLM, DB, APIs)
```

---

### **6.2 Docker Deployment**

You may use:

* `agentflow-core:latest`
* `agentflow-studio:latest`

---

## **7. Security Considerations**

* API Key handling via environment variables only
* Zero keys stored on frontend
* Role-based auth (future)
* AES-encrypted workflow storage (optional)
* CORS restricted to Studio domain
* Optional JWT authentication layer

---

# **8. Future Roadmap**

| Feature               | Description                          |
| --------------------- | ------------------------------------ |
| Workflow versioning   | Save multiple versions of workflows  |
| Real-time graph trace | Visual replay of workflow run        |
| Logs Dashboard        | Token usage, latency, cost per node  |
| Node Marketplace      | Custom node plugins                  |
| Python SDK            | `client.execute(workflow_id, input)` |

---

# ✅ **This is your complete High-Level Design (HLD)**

It’s ready for inclusion in your documentation folder.

---

If you want, I can now generate:

### ✔ **LLD (Low-Level Design)**

### ✔ **API Spec MD (done)**

### ✔ **Frontend App Spec MD (done)**

### ✔ **Architecture Diagram in PNG (ASCII or image)**

### ✔ **PDF export of all docs**

### ✔ **AgentFlow branding & color theme**

