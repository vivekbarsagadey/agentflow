# AgentFlow Core – API Specification

Version: 0.1  
Service: AgentFlow Core (Backend)  
Tech: FastAPI (Python), LangGraph

---

## 1. Overview

AgentFlow Core exposes a REST API to:

- Validate workflow specifications (WorkflowSpec JSON)
- Execute workflows
- Manage workflows (save, list, retrieve, delete)
- Manage external sources (LLM, image, DB, API configs)
- Provide basic health and readiness endpoints

Base URL examples:

- Local development: `http://localhost:8000`
- Production (example): `https://core.agentflow.yourdomain.com`

All JSON responses use `application/json`.

---

## 2. Authentication (Pluggable)

> **Initial version** can be without auth (internal use).  
> For production, recommended:

- Header: `Authorization: Bearer <TOKEN>`

If enabled, all endpoints (except `/health`) should validate this token.

---

## 3. Workflow Endpoints

### 3.1 `POST /workflows/validate`

Validate a workflow specification without executing it.

**Description**

- Validates JSON schema, references (nodes/queues/sources), and ability to compile into a LangGraph graph.
- Does *not* persist the workflow (unless implemented separately).
- Used by AgentFlow Studio before saving or running.

**Request**

- Method: `POST`
- URL: `/workflows/validate`
- Headers:
  - `Content-Type: application/json`
- Body: `WorkflowSpec` JSON

**WorkflowSpec Skeleton**

```jsonc
{
  "nodes": [
    { "id": "user_input", "type": "input", "description": "Entry node" },
    { "id": "router", "type": "router" },
    { "id": "gpt4_agent", "type": "llm", "source": "openai_gpt4" }
  ],
  "queues": [
    {
      "id": "q_user_to_router",
      "from": "user_input",
      "to": "router",
      "bandwidth": {
        "max_messages_per_second": 10,
        "burst_size": 20
      }
    }
  ],
  "edges": [
    { "from": "user_input", "to": "router", "queue": "q_user_to_router" },
    { "from": "router", "to": "gpt4_agent", "condition": "intent == 'text'" }
  ],
  "sources": [
    {
      "id": "openai_gpt4",
      "kind": "llm",
      "provider": "openai",
      "model": "gpt-4o-mini",
      "api_key_env": "OPENAI_API_KEY"
    }
  ],
  "start_node": "user_input"
}
