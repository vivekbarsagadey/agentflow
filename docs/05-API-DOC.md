# API Documentation

# AgentFlow Core API v1.0

**Version:** 1.0.0  
**Base URL:** `http://localhost:8000` (Development)  
**Base URL:** `https://api.agentflow.io` (Production)  
**Date:** December 7, 2025

---

## Table of Contents

1. [Overview](#1-overview)
2. [Authentication](#2-authentication)
3. [Workflow endpoints](#3-workflow-endpoints)
4. [Source endpoints](#4-source-endpoints)
5. [Health endpoints](#5-health-endpoints)
6. [Data models](#6-data-models)
7. [Error codes](#7-error-codes)
8. [Rate limiting](#8-rate-limiting)
9. [Examples](#9-examples)

---

## 1. Overview

### 1.1 Introduction

The AgentFlow Core API provides RESTful endpoints for:

- **Workflow validation** - Validate workflow specifications before execution
- **Workflow execution** - Execute workflows with initial state
- **Source management** - Create, read, update, and delete sources
- **Health checks** - Monitor service health and readiness

### 1.2 API conventions

| Convention | Description |
|------------|-------------|
| **Protocol** | HTTPS (production), HTTP (development) |
| **Format** | JSON (Content-Type: application/json) |
| **Encoding** | UTF-8 |
| **HTTP Methods** | GET, POST, PUT, DELETE |
| **Status Codes** | Standard HTTP status codes |
| **Timestamps** | ISO 8601 format (UTC) |
| **IDs** | UUID v4 or prefixed strings (e.g., `wf_`, `src_`) |

### 1.3 Base URLs

| Environment | Base URL |
|-------------|----------|
| Development | `http://localhost:8000` |
| Staging | `https://staging-api.agentflow.io` |
| Production | `https://api.agentflow.io` |

---

## 2. Authentication

### 2.1 API key authentication

**Header:**
```
X-API-Key: your_api_key_here
```

**Example:**
```bash
curl -X POST https://api.agentflow.io/workflows/validate \
  -H "X-API-Key: sk_live_abc123xyz..." \
  -H "Content-Type: application/json" \
  -d @workflow_spec.json
```

### 2.2 Authentication errors

| Status Code | Error | Description |
|-------------|-------|-------------|
| `401` | Unauthorized | Missing or invalid API key |
| `403` | Forbidden | Insufficient permissions |

---

## 3. Workflow endpoints

### 3.1 Validate workflow

Validates a workflow specification without executing it.

**Endpoint:** `POST /workflows/validate`

**Request body:**
```json
{
  "nodes": [
    {
      "id": "input",
      "type": "input",
      "metadata": null
    },
    {
      "id": "router",
      "type": "router",
      "metadata": null
    },
    {
      "id": "llm",
      "type": "llm",
      "metadata": {
        "source": "openai",
        "prompt": "Respond to: {user_input}"
      }
    }
  ],
  "edges": [
    {
      "from": "input",
      "to": "router"
    },
    {
      "from": "router",
      "to": "llm"
    }
  ],
  "queues": [
    {
      "id": "queue_router_llm",
      "from": "router",
      "to": "llm",
      "bandwidth": {
        "max_messages_per_second": 10,
        "max_tokens_per_minute": 50000
      }
    }
  ],
  "sources": [
    {
      "id": "openai",
      "kind": "llm",
      "config": {
        "model_name": "gpt-4",
        "api_key_env": "OPENAI_API_KEY"
      }
    }
  ],
  "start_node": "input"
}
```

**Response (200 OK):**
```json
{
  "valid": true,
  "errors": [],
  "warnings": []
}
```

**Response (400 Bad Request):**
```json
{
  "valid": false,
  "errors": [
    {
      "code": "E005",
      "message": "Start node 'nonexistent' does not exist",
      "field": "start_node",
      "node_id": null
    }
  ],
  "warnings": []
}
```

---

### 3.2 Execute workflow

Executes a validated workflow with initial state.

**Endpoint:** `POST /workflows/execute`

**Request body:**
```json
{
  "workflow": {
    "nodes": [...],
    "edges": [...],
    "queues": [...],
    "sources": [...],
    "start_node": "input"
  },
  "initial_state": {
    "user_input": "Tell me about quantum computing"
  }
}
```

**Response (200 OK):**
```json
{
  "status": "success",
  "execution_id": "exec_550e8400-e29b-41d4-a716-446655440000",
  "final_state": {
    "user_input": "Tell me about quantum computing",
    "intent": "text",
    "text_result": "Quantum computing is...",
    "tokens_used": 150,
    "metadata": {
      "start_time": 1701234567.890,
      "end_time": 1701234570.123,
      "execution_time": 2.233
    }
  },
  "metrics": {
    "execution_time": 2.233,
    "tokens_used": 150
  }
}
```

**Response (400 Bad Request):**
```json
{
  "message": "Workflow validation failed",
  "errors": [
    {
      "code": "E006",
      "message": "Edge references non-existent destination node 'llm2'",
      "field": "edges",
      "node_id": null
    }
  ]
}
```

**Response (500 Internal Server Error):**
```json
{
  "message": "Workflow execution failed",
  "error": "OpenAI API error: Rate limit exceeded"
}
```

---

### 3.3 Save workflow (future)

Saves a workflow specification for reuse.

**Endpoint:** `POST /workflows`

**Request body:**
```json
{
  "name": "Customer Support Workflow",
  "description": "Routes customer inquiries to appropriate handlers",
  "spec": {
    "nodes": [...],
    "edges": [...],
    "queues": [...],
    "sources": [...],
    "start_node": "input"
  }
}
```

**Response (201 Created):**
```json
{
  "id": "wf_550e8400-e29b-41d4-a716-446655440000",
  "name": "Customer Support Workflow",
  "description": "Routes customer inquiries to appropriate handlers",
  "created_at": "2025-12-07T10:30:00Z",
  "updated_at": "2025-12-07T10:30:00Z",
  "spec": {...}
}
```

---

### 3.4 List workflows (future)

Retrieves all saved workflows.

**Endpoint:** `GET /workflows`

**Query parameters:**
- `limit` (integer, optional): Maximum number of results (default: 50, max: 100)
- `offset` (integer, optional): Pagination offset (default: 0)
- `search` (string, optional): Search by name or description

**Example:**
```
GET /workflows?limit=20&offset=0&search=support
```

**Response (200 OK):**
```json
{
  "total": 42,
  "limit": 20,
  "offset": 0,
  "workflows": [
    {
      "id": "wf_550e8400-e29b-41d4-a716-446655440000",
      "name": "Customer Support Workflow",
      "description": "Routes customer inquiries to appropriate handlers",
      "created_at": "2025-12-07T10:30:00Z",
      "updated_at": "2025-12-07T10:30:00Z"
    },
    ...
  ]
}
```

---

### 3.5 Get workflow (future)

Retrieves a specific workflow by ID.

**Endpoint:** `GET /workflows/{workflow_id}`

**Response (200 OK):**
```json
{
  "id": "wf_550e8400-e29b-41d4-a716-446655440000",
  "name": "Customer Support Workflow",
  "description": "Routes customer inquiries to appropriate handlers",
  "created_at": "2025-12-07T10:30:00Z",
  "updated_at": "2025-12-07T10:30:00Z",
  "spec": {
    "nodes": [...],
    "edges": [...],
    "queues": [...],
    "sources": [...],
    "start_node": "input"
  }
}
```

**Response (404 Not Found):**
```json
{
  "detail": "Workflow not found"
}
```

---

### 3.6 Update workflow (future)

Updates an existing workflow.

**Endpoint:** `PUT /workflows/{workflow_id}`

**Request body:**
```json
{
  "name": "Updated Workflow Name",
  "description": "Updated description",
  "spec": {...}
}
```

**Response (200 OK):**
```json
{
  "id": "wf_550e8400-e29b-41d4-a716-446655440000",
  "name": "Updated Workflow Name",
  "description": "Updated description",
  "created_at": "2025-12-07T10:30:00Z",
  "updated_at": "2025-12-07T11:45:00Z",
  "spec": {...}
}
```

---

### 3.7 Delete workflow (future)

Deletes a workflow.

**Endpoint:** `DELETE /workflows/{workflow_id}`

**Response (200 OK):**
```json
{
  "status": "deleted",
  "id": "wf_550e8400-e29b-41d4-a716-446655440000"
}
```

---

## 4. Source endpoints

### 4.1 Create source

Creates a new source configuration.

**Endpoint:** `POST /sources`

**Request body (LLM source):**
```json
{
  "id": "openai-gpt4",
  "kind": "llm",
  "config": {
    "model_name": "gpt-4",
    "api_key_env": "OPENAI_API_KEY",
    "temperature": 0.7,
    "max_tokens": 2000
  }
}
```

**Request body (Image source):**
```json
{
  "id": "dalle3",
  "kind": "image",
  "config": {
    "model_name": "dall-e-3",
    "api_key_env": "OPENAI_API_KEY",
    "size": "1024x1024",
    "quality": "standard"
  }
}
```

**Request body (Database source):**
```json
{
  "id": "postgres-main",
  "kind": "db",
  "config": {
    "dsn_env": "DATABASE_URL",
    "pool_size": 10,
    "timeout": 30
  }
}
```

**Request body (API source):**
```json
{
  "id": "external-api",
  "kind": "api",
  "config": {
    "base_url": "https://api.example.com",
    "auth_env": "API_AUTH_TOKEN",
    "timeout": 30
  }
}
```

**Response (201 Created):**
```json
{
  "id": "openai-gpt4",
  "kind": "llm",
  "config": {
    "model_name": "gpt-4",
    "api_key_env": "OPENAI_API_KEY",
    "temperature": 0.7,
    "max_tokens": 2000
  }
}
```

**Response (409 Conflict):**
```json
{
  "detail": "Source already exists"
}
```

---

### 4.2 List sources

Retrieves all sources.

**Endpoint:** `GET /sources`

**Response (200 OK):**
```json
[
  {
    "id": "openai-gpt4",
    "kind": "llm",
    "config": {
      "model_name": "gpt-4",
      "api_key_env": "OPENAI_API_KEY"
    }
  },
  {
    "id": "dalle3",
    "kind": "image",
    "config": {
      "model_name": "dall-e-3",
      "api_key_env": "OPENAI_API_KEY"
    }
  },
  {
    "id": "postgres-main",
    "kind": "db",
    "config": {
      "dsn_env": "DATABASE_URL"
    }
  }
]
```

---

### 4.3 Get source

Retrieves a specific source by ID.

**Endpoint:** `GET /sources/{source_id}`

**Response (200 OK):**
```json
{
  "id": "openai-gpt4",
  "kind": "llm",
  "config": {
    "model_name": "gpt-4",
    "api_key_env": "OPENAI_API_KEY",
    "temperature": 0.7,
    "max_tokens": 2000
  }
}
```

**Response (404 Not Found):**
```json
{
  "detail": "Source not found"
}
```

---

### 4.4 Update source

Updates an existing source.

**Endpoint:** `PUT /sources/{source_id}`

**Request body:**
```json
{
  "id": "openai-gpt4",
  "kind": "llm",
  "config": {
    "model_name": "gpt-4-turbo",
    "api_key_env": "OPENAI_API_KEY",
    "temperature": 0.8,
    "max_tokens": 4000
  }
}
```

**Response (200 OK):**
```json
{
  "id": "openai-gpt4",
  "kind": "llm",
  "config": {
    "model_name": "gpt-4-turbo",
    "api_key_env": "OPENAI_API_KEY",
    "temperature": 0.8,
    "max_tokens": 4000
  }
}
```

---

### 4.5 Delete source

Deletes a source.

**Endpoint:** `DELETE /sources/{source_id}`

**Response (200 OK):**
```json
{
  "status": "deleted"
}
```

**Response (404 Not Found):**
```json
{
  "detail": "Source not found"
}
```

---

## 5. Health endpoints

### 5.1 Health check

Basic health check endpoint.

**Endpoint:** `GET /health`

**Response (200 OK):**
```json
{
  "status": "ok",
  "version": "1.0.0",
  "uptime": 3600.5
}
```

---

### 5.2 Readiness check

Kubernetes readiness probe.

**Endpoint:** `GET /health/ready`

**Response (200 OK):**
```json
{
  "status": "ready"
}
```

**Response (503 Service Unavailable):**
```json
{
  "status": "not_ready",
  "checks": {
    "database": false,
    "redis": true
  }
}
```

---

### 5.3 Liveness check

Kubernetes liveness probe.

**Endpoint:** `GET /health/live`

**Response (200 OK):**
```json
{
  "status": "alive"
}
```

---

## 6. Data models

### 6.1 NodeModel

```json
{
  "id": "string",
  "type": "input | router | llm | image | db | aggregator",
  "metadata": {
    "source": "string (optional)",
    "prompt": "string (optional)",
    "query": "string (optional)",
    "...": "additional fields"
  }
}
```

---

### 6.2 EdgeModel

```json
{
  "from": "string",
  "to": "string | string[]",
  "condition": "string (optional)"
}
```

---

### 6.3 QueueModel

```json
{
  "id": "string",
  "from": "string",
  "to": "string",
  "bandwidth": {
    "max_messages_per_second": "integer (optional)",
    "max_requests_per_minute": "integer (optional)",
    "max_tokens_per_minute": "integer (optional)",
    "burst_size": "integer (optional)"
  },
  "sub_queues": [
    {
      "id": "string",
      "weight": "number (0.0-1.0)"
    }
  ]
}
```

---

### 6.4 SourceModel

```json
{
  "id": "string",
  "kind": "llm | image | db | api",
  "config": {
    "model_name": "string (for llm, image)",
    "api_key_env": "string (for llm, image, api)",
    "dsn_env": "string (for db)",
    "base_url": "string (for api)",
    "...": "additional kind-specific fields"
  }
}
```

---

### 6.5 WorkflowSpecModel

```json
{
  "nodes": ["NodeModel[]"],
  "edges": ["EdgeModel[]"],
  "queues": ["QueueModel[]"],
  "sources": ["SourceModel[]"],
  "start_node": "string"
}
```

---

### 6.6 GraphState

```json
{
  "user_input": "string",
  "intent": "string (optional)",
  "text_result": "string (optional)",
  "image_result": "any (optional)",
  "db_result": "any (optional)",
  "final_output": "any (optional)",
  "tokens_used": "integer (optional)",
  "cost": "number (optional)",
  "execution_time": "number (optional)",
  "metadata": "object (optional)",
  "errors": "array (optional)"
}
```

---

## 7. Error codes

### 7.1 Validation error codes

| Code | Description |
|------|-------------|
| `E001` | Invalid JSON schema |
| `E002` | Missing required field |
| `E003` | Invalid field value |
| `E004` | Invalid node type |
| `E005` | Start node does not exist |
| `E006` | Edge references non-existent node |
| `E007` | Queue references non-existent node |
| `E008` | Node references non-existent source |
| `E009` | Duplicate node IDs |
| `E010` | Duplicate source IDs |
| `E011` | Duplicate queue IDs |
| `E012` | Circular dependency detected |
| `E013` | Unreachable nodes detected |
| `E014` | Node requires source configuration |

---

### 7.2 HTTP status codes

| Status Code | Description | Usage |
|-------------|-------------|-------|
| `200` | OK | Successful GET, PUT, DELETE |
| `201` | Created | Successful POST |
| `400` | Bad Request | Invalid request body or validation error |
| `401` | Unauthorized | Missing or invalid API key |
| `403` | Forbidden | Insufficient permissions |
| `404` | Not Found | Resource not found |
| `409` | Conflict | Resource already exists |
| `422` | Unprocessable Entity | Pydantic validation error |
| `429` | Too Many Requests | Rate limit exceeded |
| `500` | Internal Server Error | Server error |
| `503` | Service Unavailable | Service temporarily unavailable |

---

## 8. Rate limiting

### 8.1 Rate limit headers

**Response headers:**
```
X-RateLimit-Limit: 1000
X-RateLimit-Remaining: 999
X-RateLimit-Reset: 1701234567
```

### 8.2 Rate limit exceeded

**Response (429 Too Many Requests):**
```json
{
  "error": "Rate limit exceeded",
  "limit": 1000,
  "remaining": 0,
  "reset_at": "2025-12-07T12:00:00Z"
}
```

---

## 9. Examples

### 9.1 Simple text workflow

**Request:**
```bash
curl -X POST http://localhost:8000/workflows/execute \
  -H "Content-Type: application/json" \
  -d '{
    "workflow": {
      "nodes": [
        {"id": "input", "type": "input"},
        {"id": "llm", "type": "llm", "metadata": {"source": "openai"}}
      ],
      "edges": [
        {"from": "input", "to": "llm"}
      ],
      "queues": [],
      "sources": [
        {
          "id": "openai",
          "kind": "llm",
          "config": {"model_name": "gpt-4", "api_key_env": "OPENAI_API_KEY"}
        }
      ],
      "start_node": "input"
    },
    "initial_state": {
      "user_input": "What is the capital of France?"
    }
  }'
```

**Response:**
```json
{
  "status": "success",
  "execution_id": "exec_123",
  "final_state": {
    "user_input": "What is the capital of France?",
    "text_result": "The capital of France is Paris.",
    "tokens_used": 25,
    "metadata": {
      "execution_time": 1.2
    }
  },
  "metrics": {
    "execution_time": 1.2,
    "tokens_used": 25
  }
}
```

---

### 9.2 Multi-node workflow with router

**Request:**
```bash
curl -X POST http://localhost:8000/workflows/execute \
  -H "Content-Type: application/json" \
  -d '{
    "workflow": {
      "nodes": [
        {"id": "input", "type": "input"},
        {"id": "router", "type": "router"},
        {"id": "llm", "type": "llm", "metadata": {"source": "openai"}},
        {"id": "image", "type": "image", "metadata": {"source": "dalle"}},
        {"id": "aggregator", "type": "aggregator"}
      ],
      "edges": [
        {"from": "input", "to": "router"},
        {"from": "router", "to": "llm"},
        {"from": "router", "to": "image"},
        {"from": "llm", "to": "aggregator"},
        {"from": "image", "to": "aggregator"}
      ],
      "queues": [],
      "sources": [
        {"id": "openai", "kind": "llm", "config": {"model_name": "gpt-4"}},
        {"id": "dalle", "kind": "image", "config": {"model_name": "dall-e-3"}}
      ],
      "start_node": "input"
    },
    "initial_state": {
      "user_input": "Create an image of a sunset"
    }
  }'
```

**Response:**
```json
{
  "status": "success",
  "execution_id": "exec_456",
  "final_state": {
    "user_input": "Create an image of a sunset",
    "intent": "image",
    "image_result": {
      "url": "https://oaidalleapiprodscus.blob.core.windows.net/...",
      "prompt": "Create an image of a sunset"
    },
    "final_output": {
      "image": {
        "url": "https://oaidalleapiprodscus.blob.core.windows.net/...",
        "prompt": "Create an image of a sunset"
      }
    },
    "metadata": {
      "execution_time": 8.5
    }
  },
  "metrics": {
    "execution_time": 8.5,
    "tokens_used": 0
  }
}
```

---

### 9.3 Workflow with rate limiting

**Request:**
```bash
curl -X POST http://localhost:8000/workflows/execute \
  -H "Content-Type: application/json" \
  -d '{
    "workflow": {
      "nodes": [
        {"id": "input", "type": "input"},
        {"id": "llm", "type": "llm", "metadata": {"source": "openai"}}
      ],
      "edges": [
        {"from": "input", "to": "llm"}
      ],
      "queues": [
        {
          "id": "queue_input_llm",
          "from": "input",
          "to": "llm",
          "bandwidth": {
            "max_messages_per_second": 5,
            "max_tokens_per_minute": 10000
          }
        }
      ],
      "sources": [
        {"id": "openai", "kind": "llm", "config": {"model_name": "gpt-4"}}
      ],
      "start_node": "input"
    },
    "initial_state": {
      "user_input": "Explain quantum entanglement"
    }
  }'
```

**Response:**
```json
{
  "status": "success",
  "execution_id": "exec_789",
  "final_state": {
    "user_input": "Explain quantum entanglement",
    "text_result": "Quantum entanglement is...",
    "tokens_used": 250,
    "metadata": {
      "execution_time": 2.1,
      "rate_limit_delay": 0.2
    }
  },
  "metrics": {
    "execution_time": 2.1,
    "tokens_used": 250
  }
}
```

---

### 9.4 Database query workflow

**Request:**
```bash
curl -X POST http://localhost:8000/workflows/execute \
  -H "Content-Type: application/json" \
  -d '{
    "workflow": {
      "nodes": [
        {"id": "input", "type": "input"},
        {
          "id": "db",
          "type": "db",
          "metadata": {
            "source": "postgres",
            "query": "SELECT * FROM users WHERE id = 1"
          }
        }
      ],
      "edges": [
        {"from": "input", "to": "db"}
      ],
      "queues": [],
      "sources": [
        {
          "id": "postgres",
          "kind": "db",
          "config": {"dsn_env": "DATABASE_URL"}
        }
      ],
      "start_node": "input"
    },
    "initial_state": {
      "user_input": "Fetch user data"
    }
  }'
```

**Response:**
```json
{
  "status": "success",
  "execution_id": "exec_101",
  "final_state": {
    "user_input": "Fetch user data",
    "db_result": [
      {
        "id": 1,
        "name": "John Doe",
        "email": "john@example.com"
      }
    ],
    "metadata": {
      "execution_time": 0.5
    }
  },
  "metrics": {
    "execution_time": 0.5,
    "tokens_used": 0
  }
}
```

---

**Document Approval**

| Role | Name | Date | Signature |
|------|------|------|-----------|
| API Lead | _______________ | _______________ | _______________ |
| Backend Engineer | _______________ | _______________ | _______________ |
| QA Engineer | _______________ | _______________ | _______________ |
