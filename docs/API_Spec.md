**Fully detailed `API-SPEC.md` document** exactly like industry-standard API specifications:

* Every endpoint
* Request schema
* Response schema
* Error formats
* Auth notes
* Pagination where needed
* Example payloads
* Example success + failure responses
* Workflow validation + execution
* Sources management
* Queues management
* Workflow storage
* Health checks

Below is **your complete, production-ready API Spec MD file**.

---

# 📄 **API-SPEC.md — AgentFlow Core API Specification**

**Version:** 1.0
**Base URL:** `https://api.agentflow.ai` (placeholder)
**Format:** REST / JSON
**Status Codes:** Standard HTTP

---

# -------------------------------------------

# **1. Overview**

# -------------------------------------------

AgentFlow API enables:

✔ Uploading workflow JSON
✔ Validating workflow structure
✔ Constructing executable LangGraph runtime
✔ Executing workflows with dynamic state
✔ Managing sources (LLMs, DBs, APIs)
✔ Managing queues (bandwidth, routing constraints)
✔ Workflow versioning & storage

Authentication:

```
Authorization: Bearer <token>
Content-Type: application/json
```

---

# -------------------------------------------

# **2. Data Models**

# -------------------------------------------

These models appear in requests/responses.

---

## **2.1 Node Model**

```json
{
  "id": "string",
  "type": "input | router | llm | image | db | aggregator",
  "metadata": {
    "source": "string (source_id)",
    "config": {}
  }
}
```

---

## **2.2 Edge Model**

```json
{
  "from": "string (node_id)",
  "to": "string or array"
}
```

---

## **2.3 Queue Model**

```json
{
  "id": "string",
  "from": "string (node_id)",
  "to": "string (node_id)",
  "bandwidth": {
    "max_messages_per_second": 2,
    "max_requests_per_minute": 60,
    "tokens_per_minute": 20000
  },
  "subqueues": [
    {
      "id": "string",
      "weight": 0.5
    }
  ]
}
```

---

## **2.4 Source Model**

```json
{
  "id": "llm-openai",
  "kind": "llm | image | db | api",
  "config": {
    "model_name": "gpt-4.1",
    "api_key": "string",
    "url": "optional"
  }
}
```

---

## **2.5 WorkflowSpec Model**

```json
{
  "nodes": [],
  "edges": [],
  "queues": [],
  "sources": [],
  "start_node": "input"
}
```

---

## **2.6 Execution State**

```json
{
  "user_input": "string",
  "text_result": "optional string",
  "image_result": "optional base64",
  "db_result": "optional array",
  "final_output": {},
  "metadata": {}
}
```

---

# -------------------------------------------

# **3. Endpoints**

# -------------------------------------------

There are 5 major API groups:

### 1. **Workflow Management**

### 2. **Execution**

### 3. **Sources**

### 4. **Queues**

### 5. **System / Health**

---

# ===========================================

# **3.1 WORKFLOW VALIDATION**

# ===========================================

# ✅ **POST /workflows/validate**

Validates a workflow without executing it.

### **Request Body**

```json
{
  "workflow": { ... WorkflowSpec }
}
```

### **Success Response**

```json
{
  "status": "ok",
  "errors": [],
  "warnings": []
}
```

### **Validation Errors**

```json
{
  "status": "error",
  "errors": [
    "Start node does not exist",
    "Node id 'llm-text' missing source",
    "Queue Q1 refers to missing node input-text"
  ]
}
```

---

# ===========================================

# **3.2 WORKFLOW EXECUTION**

# ===========================================

# ✅ **POST /workflows/execute**

Runs the workflow with an initial state.

### **Request Body**

```json
{
  "workflow": { ... WorkflowSpec },
  "initial_state": {
    "user_input": "Write a poem about clouds"
  }
}
```

### **Success Response**

```json
{
  "status": "ok",
  "execution_id": "exec_12345",
  "final_state": {
    "text_result": "Here is your poem...",
    "image_result": null,
    "db_result": null,
    "final_output": {
      "text": "Here is your poem..."
    }
  },
  "metrics": {
    "execution_time_ms": 130,
    "tokens_used": 120,
    "nodes_executed": ["input", "router", "llm-text", "aggregator"]
  }
}
```

---

### **Execution Error Response**

```json
{
  "status": "error",
  "message": "Node execution failed",
  "node_id": "llm-text",
  "details": "OpenAI API key invalid"
}
```

---

# ===========================================

# **3.3 WORKFLOW STORAGE**

# ===========================================

# ➕ **POST /workflows**

Store workflow in DB.

```json
{
  "name": "My Workflow",
  "workflow": { ... WorkflowSpec }
}
```

Response:

```json
{
  "status": "ok",
  "workflow_id": "wf_001",
  "version": 1
}
```

---

# 📄 **GET /workflows/{id}**

Retrieves workflow spec.

---

# 📝 **PUT /workflows/{id}**

Updates workflow.

---

# 🗑 **DELETE /workflows/{id}**

Deletes workflow.

---

# ===========================================

# **3.4 SOURCES**

# ===========================================

# ➕ **POST /sources**

```json
{
  "id": "llm-openai",
  "kind": "llm",
  "config": {
    "model_name": "gpt-4.1",
    "api_key": "sk-xxxxx"
  }
}
```

Response:

```json
{ "status": "ok" }
```

---

# 📄 **GET /sources**

Lists all configured sources.

---

# 📝 **PUT /sources/{id}**

Updates a source.

---

# 🗑 **DELETE /sources/{id}**

Deletes source.

---

# ===========================================

# **3.5 QUEUES**

# ===========================================

# ➕ **POST /queues**

```json
{
  "id": "q1",
  "from": "llm-text",
  "to": "image-gen",
  "bandwidth": {
    "max_messages_per_second": 1,
    "tokens_per_minute": 20000
  },
  "subqueues": []
}
```

---

# 📄 **GET /queues**

Lists all queues.

---

# ===========================================

# **3.6 SYSTEM / HEALTH**

# ===========================================

# GET /health

```json
{
  "status": "ok",
  "uptime": 10293,
  "version": "1.0",
  "timestamp": "2025-02-27T12:30Z"
}
```

---

# -------------------------------------------

# **4. Error Format (Global Standard)**

# -------------------------------------------

All errors follow this structure:

```json
{
  "status": "error",
  "message": "Human-readable error",
  "details": "Optional detailed info or stack trace"
}
```

---

# -------------------------------------------

# **5. Security**

# -------------------------------------------

* JWT or API Key required
* Workflow execution also checks for:

  * Rate limits
  * Overlapping requests
  * Token budgets

---

# -------------------------------------------

# **6. Examples**

# -------------------------------------------

### **Example: Full Workflow Validate + Execute Flow**

1. Designer exports JSON
2. Frontend calls:

```
POST /workflows/validate
```

If valid → “ok”

3. User tests it:

```
POST /workflows/execute
{
  "workflow": {...},
  "initial_state": {"user_input": "hello"}
}
```

Backend:

* Builds LangGraph
* Runs nodes
* Returns final_state

---

# -------------------------------------------

# ✅ Your API-SPEC.md is READY

# -------------------------------------------

If you want, I can also generate:

### 🔥 **BACKEND-SPEC.md**

### 🔥 **FRONTEND-SPEC.md**

### 🔥 **WORKFLOW-SCHEMA.md (JSON schema validator)**

### 🔥 **OpenAPI 3.1 YAML version of this API**

### 🔥 **Postman Collection file**

Tell me which one you want next.
