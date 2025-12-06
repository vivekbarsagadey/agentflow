# High-Level Design (HLD)

# AgentFlow — Multi-Agent Workflow Orchestration Platform

**Version:** 1.0  
**Date:** December 7, 2025  
**Status:** Approved  
**Audience:** System Architects, Backend Engineers, Frontend Engineers, Tech Leads

---

## Table of Contents

1. [System overview](#1-system-overview)
2. [Architecture diagram](#2-architecture-diagram)
3. [Core concepts](#3-core-concepts)
4. [Component design](#4-component-design)
5. [Data flow](#5-data-flow)
6. [Integration architecture](#6-integration-architecture)
7. [Deployment architecture](#7-deployment-architecture)
8. [Security architecture](#8-security-architecture)
9. [Scalability and performance](#9-scalability-and-performance)
10. [Technology decisions](#10-technology-decisions)
11. [Future roadmap](#11-future-roadmap)

---

## 1. System overview

### 1.1 Purpose

**AgentFlow** is a **JSON-driven workflow orchestration engine** that converts declarative workflow specifications into **executable multi-agent graphs**. The system enables technical users to design, validate, and execute complex workflows involving AI agents, databases, APIs, and other external services.

### 1.2 System components

AgentFlow consists of two major components:

#### 1.2.1 AgentFlow Core (Backend)

Built using **Python, FastAPI, and LangGraph**.

Core functionalities:

- Parse and validate a `WorkflowSpec` (JSON)
- Build a LangGraph runtime graph dynamically
- Configure nodes (LLM, Image, DB, Router, Aggregator)
- Configure edges (with conditions)
- Configure queues (with bandwidth / rate limits)
- Configure sources (OpenAI, DBs, APIs)
- Execute workflows and return structured final state
- Provide REST endpoints for validate / execute / save / retrieve workflows

#### 1.2.2 AgentFlow Studio (Frontend Designer)

A visual workflow builder built with **Next.js (App Router)**.

Studio enables users to:

- Add nodes visually (drag & drop)
- Connect nodes to form workflows
- Configure sources (LLMs, DBs, APIs)
- Set queue bandwidth limits
- Preview JSON spec in real-time
- Validate workflow (via backend)
- Execute workflow with test inputs

### 1.3 Design principles

| Principle | Description |
|-----------|-------------|
| **JSON-First** | All workflows are defined, stored, and exchanged as JSON specifications |
| **Declarative** | Users declare what they want, not how to execute it |
| **Modular** | Components are loosely coupled and independently deployable |
| **Extensible** | New node types and sources can be added without core changes |
| **Secure** | Secrets never stored in code or logs; tenant isolation enforced |
| **Observable** | Comprehensive logging and metrics for all operations |

---

## 2. Architecture diagram

### 2.1 High-level system architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              External Users                                  │
│                    (Designers, Engineers, Operators)                         │
└─────────────────────────────────────────────────────────────────────────────┘
                                      │
                                      │ HTTPS
                                      ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                          Load Balancer / CDN                                 │
│                         (nginx / Cloudflare)                                 │
└─────────────────────────────────────────────────────────────────────────────┘
                                      │
                    ┌─────────────────┴─────────────────┐
                    │                                   │
                    ▼                                   ▼
┌───────────────────────────────────┐   ┌───────────────────────────────────┐
│        AgentFlow Studio           │   │        AgentFlow Core             │
│      (Next.js 16 Frontend)        │   │      (FastAPI Backend)            │
│                                   │   │                                   │
│  ┌─────────────────────────────┐ │   │  ┌─────────────────────────────┐  │
│  │    React Flow Canvas       │  │   │  │      REST API Layer         │  │
│  │    (Workflow Designer)      │  │   │  │   /workflows, /sources      │  │
│  └─────────────────────────────┘ │   │  └─────────────────────────────┘  │
│  ┌─────────────────────────────┐ │   │  ┌─────────────────────────────┐  │
│  │    Zustand State Store     │  │   │  │      Validator Module       │  │
│  │    (Workflow State)         │  │   │  │   (Schema + Logic)          │  │
│  └─────────────────────────────┘ │   │  └─────────────────────────────┘  │
│  ┌─────────────────────────────┐ │   │  ┌─────────────────────────────┐  │
│  │    API Client Layer        │  │   │  │      Runtime Engine         │  │
│  │    (Backend Integration)    │  │   │  │   (LangGraph Builder)       │  │
│  └─────────────────────────────┘ │   │  └─────────────────────────────┘  │
│                                   │   │  ┌─────────────────────────────┐  │
│                                   │   │  │      Node Registry          │  │
│                                   │   │  │   (LLM, DB, Image, etc.)    │  │
│                                   │   │  └─────────────────────────────┘  │
│                                   │   │  ┌─────────────────────────────┐  │
│                                   │   │  │      Queue Manager          │  │
│                                   │   │  │   (Rate Limiting)           │  │
│                                   │   │  └─────────────────────────────┘  │
└───────────────────────────────────┘   └───────────────────────────────────┘
                    │                                   │
                    │                                   │
                    └─────────────────┬─────────────────┘
                                      │
                    ┌─────────────────┴─────────────────┐
                    │                                   │
                    ▼                                   ▼
┌───────────────────────────────────┐   ┌───────────────────────────────────┐
│           PostgreSQL              │   │             Redis                 │
│     (Workflow Storage)            │   │    (Rate Limiting / Cache)        │
└───────────────────────────────────┘   └───────────────────────────────────┘
                                      │
                                      │
                                      ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                          External Services                                   │
│                                                                             │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐       │
│  │   OpenAI    │  │  DALL-E     │  │  PostgreSQL │  │  HTTP APIs  │       │
│  │   (LLM)     │  │  (Image)    │  │  (Data)     │  │  (Custom)   │       │
│  └─────────────┘  └─────────────┘  └─────────────┘  └─────────────┘       │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 2.2 Component interaction diagram

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                          AgentFlow Core Internal                             │
└─────────────────────────────────────────────────────────────────────────────┘

    ┌───────────────┐
    │ API Request   │
    │ (WorkflowSpec)│
    └───────┬───────┘
            │
            ▼
    ┌───────────────┐       ┌───────────────┐
    │   Validator   │ ────▶ │   Registry    │
    │   Module      │       │   (Sources,   │
    │               │       │    Queues)    │
    └───────┬───────┘       └───────────────┘
            │                       │
            │ Valid                 │
            ▼                       ▼
    ┌───────────────┐       ┌───────────────┐
    │    Builder    │ ◀──── │ Node Factory  │
    │   (LangGraph) │       │ (LLM, DB...)  │
    └───────┬───────┘       └───────────────┘
            │
            │ Compiled Graph
            ▼
    ┌───────────────┐       ┌───────────────┐
    │   Executor    │ ◀──── │ Rate Limiter  │
    │   (invoke)    │       │ (Queue Mgmt)  │
    └───────┬───────┘       └───────────────┘
            │
            │ Final State
            ▼
    ┌───────────────┐
    │ API Response  │
    │ (Final State) │
    └───────────────┘
```

---

## 3. Core concepts

### 3.1 WorkflowSpec (JSON blueprint)

The entire system is defined by a single JSON structure containing:

- **Nodes** — Computation units
- **Edges** — Connections between nodes
- **Queues** — Rate-limited channels with bandwidth controls
- **Sources** — External service configurations (LLM, API, DB)
- **Start Node** — Entry point for execution

AgentFlow Core uses this JSON to dynamically build the execution graph.

### 3.2 Nodes

Supported built-in node types:

| Node Type | Purpose | Requires Source |
|-----------|---------|-----------------|
| `input` | Entry point, accepts user input | No |
| `router` | Determines routing conditions via LLM or rules | Optional |
| `llm` | Text generation / reasoning | Yes |
| `image` | DALL·E or other model-based image generation | Yes |
| `db` | Runs SQL queries | Yes |
| `aggregator` | Combines values into a final output | No |
| `api` (future) | External API calls | Yes |

Nodes are converted into **LangGraph functions** at runtime.

### 3.3 Edges

Edges define connections between nodes.

Edge types:

| Type | Description | Example |
|------|-------------|---------|
| **Unconditional** | Always follows this path | `input` → `router` |
| **Conditional** | Follows based on condition | `router` → `llm` if `intent == 'text'` |
| **Parallel** | Connects to multiple nodes | `router` → `[llm, image]` |

### 3.4 Queues

Queues act as **rate-limited message channels** between nodes.

Bandwidth configuration options:

| Option | Description |
|--------|-------------|
| `max_messages_per_second` | Maximum messages per second |
| `max_requests_per_minute` | Maximum requests per rolling minute |
| `max_tokens_per_minute` | Maximum tokens (for LLM) per minute |
| `burst_size` | Allowed burst above normal rate |
| `sub_queues` | Weighted distribution across sub-queues |

### 3.5 Sources

Reusable external integrations:

| Source Kind | Configuration | Purpose |
|-------------|---------------|---------|
| `llm` | model, api_key_env | Language model calls |
| `image` | model, api_key_env | Image generation |
| `db` | driver, dsn_env | Database queries |
| `api` | base_url, auth_env | HTTP API calls |

### 3.6 GraphState

The state object passed between nodes during execution:

```python
class GraphState(TypedDict, total=False):
    user_input: str        # Original user input
    intent: str            # Classified intent
    text_result: str       # LLM output
    image_result: Any      # Image generation output
    db_result: Any         # Database query result
    final_output: Any      # Aggregated final result
    tokens_used: int       # Token consumption
    cost: float            # Execution cost
    metadata: dict         # Additional execution data
```

---

## 4. Component design

### 4.1 Backend modules (AgentFlow Core)

| Module | File Path | Description |
|--------|-----------|-------------|
| **API Layer** | `api/main.py` | FastAPI application entry point |
| **Workflow Routes** | `api/routes/workflows.py` | Validate, execute, CRUD endpoints |
| **Source Routes** | `api/routes/sources.py` | Source management endpoints |
| **Health Routes** | `api/routes/health.py` | Health check endpoints |
| **Validator** | `runtime/validator.py` | Schema + logical validation |
| **Builder** | `runtime/builder.py` | Converts WorkflowSpec → LangGraph |
| **Executor** | `runtime/executor.py` | Invokes compiled graph |
| **Registry** | `runtime/registry.py` | Stores sources, queues, node metadata |
| **Rate Limiter** | `runtime/rate_limiter.py` | Enforces bandwidth and queue rules |
| **State** | `runtime/state.py` | GraphState definition |
| **Node Implementations** | `nodes/*.py` | LLM, Image, DB, Router, Aggregator |
| **Source Adapters** | `sources/*.py` | OpenAI, Postgres, HTTP connectors |
| **Utilities** | `utils/*.py` | Logging, error handling, ID generation |

### 4.2 Frontend modules (AgentFlow Studio)

| Module | File Path | Description |
|--------|-----------|-------------|
| **Designer Page** | `app/designer/page.tsx` | Main workflow designer page |
| **Workflow Canvas** | `components/WorkflowCanvas.tsx` | React Flow canvas for nodes/edges |
| **Node Palette** | `components/NodePalette.tsx` | Drag-and-drop node tools |
| **Properties Panel** | `components/PropertiesPanel.tsx` | Node/queue/source configuration |
| **Queue Editor** | `components/QueueEditor.tsx` | Bandwidth/subqueue configuration |
| **Source Editor** | `components/SourceEditor.tsx` | CRUD for sources |
| **JSON Preview** | `components/JsonPreview.tsx` | Real-time JSON preview |
| **Workflow Store** | `lib/useWorkflowStore.ts` | Zustand state management |
| **API Client** | `lib/api.ts` | Backend API integration |
| **Type Definitions** | `lib/types.ts` | TypeScript type definitions |
| **API Routes** | `app/api/*.ts` | Proxy routes to backend |

### 4.3 Module dependency diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                        API Layer                                 │
│                   (routes/workflows.py)                          │
└─────────────────────────────────────────────────────────────────┘
            │                   │                   │
            ▼                   ▼                   ▼
┌───────────────────┐ ┌───────────────────┐ ┌───────────────────┐
│    Validator      │ │     Builder       │ │    Executor       │
│  (validator.py)   │ │   (builder.py)    │ │  (executor.py)    │
└───────────────────┘ └───────────────────┘ └───────────────────┘
            │                   │                   │
            └───────────┬───────┴───────────┬───────┘
                        ▼                   ▼
            ┌───────────────────┐ ┌───────────────────┐
            │     Registry      │ │   Rate Limiter    │
            │   (registry.py)   │ │ (rate_limiter.py) │
            └───────────────────┘ └───────────────────┘
                        │
            ┌───────────┴───────────┐
            ▼                       ▼
┌───────────────────┐     ┌───────────────────┐
│      Nodes        │     │     Sources       │
│   (nodes/*.py)    │     │  (sources/*.py)   │
└───────────────────┘     └───────────────────┘
```

---

## 5. Data flow

### 5.1 Workflow creation flow

```
┌──────────┐    ┌──────────┐    ┌──────────┐    ┌──────────┐
│  User    │───▶│  Studio  │───▶│  Core    │───▶│   DB     │
│  Action  │    │  Canvas  │    │  API     │    │ Storage  │
└──────────┘    └──────────┘    └──────────┘    └──────────┘
     │               │               │               │
     │ Drag node     │               │               │
     ├──────────────▶│               │               │
     │               │ Update state  │               │
     │               ├──────────────▶│               │
     │               │               │               │
     │ Click Save    │               │               │
     ├──────────────▶│               │               │
     │               │ POST /workflows│              │
     │               ├──────────────▶│               │
     │               │               │ Save workflow │
     │               │               ├──────────────▶│
     │               │               │               │
     │               │  Success      │               │
     │               │◀──────────────┤               │
     │  Confirmed    │               │               │
     │◀──────────────┤               │               │
```

### 5.2 Workflow validation flow

```
┌──────────┐    ┌──────────┐    ┌──────────┐    ┌──────────┐
│  Studio  │───▶│   Core   │───▶│ Validator│───▶│ Response │
│  Client  │    │   API    │    │  Module  │    │          │
└──────────┘    └──────────┘    └──────────┘    └──────────┘
     │               │               │               │
     │ POST /validate│               │               │
     ├──────────────▶│               │               │
     │               │ Parse JSON    │               │
     │               ├──────────────▶│               │
     │               │               │ Schema check  │
     │               │               ├──────────────▶│
     │               │               │               │
     │               │               │ Ref check     │
     │               │               ├──────────────▶│
     │               │               │               │
     │               │ Errors/OK     │               │
     │               │◀──────────────┤               │
     │  Response     │               │               │
     │◀──────────────┤               │               │
```

### 5.3 Workflow execution flow

```
┌──────────┐    ┌──────────┐    ┌──────────┐    ┌──────────┐    ┌──────────┐
│  Studio  │───▶│   Core   │───▶│ Builder  │───▶│ Executor │───▶│ External │
│  Client  │    │   API    │    │          │    │          │    │ Services │
└──────────┘    └──────────┘    └──────────┘    └──────────┘    └──────────┘
     │               │               │               │               │
     │ POST /execute │               │               │               │
     │ + initial_state               │               │               │
     ├──────────────▶│               │               │               │
     │               │ Validate      │               │               │
     │               ├──────────────▶│               │               │
     │               │               │               │               │
     │               │ Build graph   │               │               │
     │               ├──────────────▶│               │               │
     │               │               │               │               │
     │               │   Compiled    │               │               │
     │               │   Graph       │               │               │
     │               │◀──────────────┤               │               │
     │               │               │               │               │
     │               │ Execute       │               │               │
     │               ├──────────────────────────────▶│               │
     │               │               │               │               │
     │               │               │               │ LLM Call      │
     │               │               │               ├──────────────▶│
     │               │               │               │               │
     │               │               │               │ Response      │
     │               │               │               │◀──────────────┤
     │               │               │               │               │
     │               │   Final State │               │               │
     │               │◀──────────────────────────────┤               │
     │  Response     │               │               │               │
     │◀──────────────┤               │               │               │
```

### 5.4 Node execution sequence

```
input_node ──▶ router_node ──┬──▶ llm_node ──────┐
                             │                   │
                             └──▶ image_node ────┼──▶ aggregator_node ──▶ END
                                                 │
                                                 └───────────────────────────
```

---

## 6. Integration architecture

### 6.1 LLM integration

```
┌─────────────────────────────────────────────────────────────────┐
│                         LLM Node                                 │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                      Source Adapter                              │
│                    (llm_openai.py)                               │
│                                                                  │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │  - Load API key from environment                        │   │
│  │  - Configure model parameters                           │   │
│  │  - Handle rate limiting                                 │   │
│  │  - Parse response                                       │   │
│  └─────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                     OpenAI API                                   │
│                  (api.openai.com)                                │
└─────────────────────────────────────────────────────────────────┘
```

### 6.2 Database integration

```
┌─────────────────────────────────────────────────────────────────┐
│                          DB Node                                 │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                      Source Adapter                              │
│                    (db_postgres.py)                              │
│                                                                  │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │  - Load DSN from environment                            │   │
│  │  - Connection pooling                                   │   │
│  │  - Execute query                                        │   │
│  │  - Return results                                       │   │
│  └─────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                      PostgreSQL                                  │
│                  (Customer Database)                             │
└─────────────────────────────────────────────────────────────────┘
```

### 6.3 API integration patterns

| Pattern | Description | Use Case |
|---------|-------------|----------|
| **Synchronous** | Wait for response before continuing | LLM calls, DB queries |
| **Retry with Backoff** | Retry on transient failures | API rate limits |
| **Circuit Breaker** | Stop calling failing services | External API outages |
| **Timeout** | Limit wait time for responses | All external calls |

---

## 7. Deployment architecture

### 7.1 Recommended deployment

```
┌─────────────────────────────────────────────────────────────────┐
│                         Internet                                 │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                    Load Balancer (nginx)                         │
│                    - SSL termination                             │
│                    - Rate limiting                               │
└─────────────────────────────────────────────────────────────────┘
                              │
              ┌───────────────┴───────────────┐
              │                               │
              ▼                               ▼
┌─────────────────────────────┐ ┌─────────────────────────────┐
│    AgentFlow Studio         │ │     AgentFlow Core          │
│    (Static/CDN)             │ │     (Container Cluster)     │
│                             │ │                             │
│  - Next.js static export    │ │  - FastAPI containers       │
│  - CDN distribution         │ │  - Horizontal scaling       │
│  - Edge caching             │ │  - Health checks            │
└─────────────────────────────┘ └─────────────────────────────┘
                                              │
                              ┌───────────────┴───────────────┐
                              │                               │
                              ▼                               ▼
                ┌─────────────────────────────┐ ┌─────────────────────────────┐
                │       PostgreSQL            │ │          Redis              │
                │   - Primary + Replica       │ │   - Cluster mode            │
                │   - Automated backups       │ │   - Persistence             │
                └─────────────────────────────┘ └─────────────────────────────┘
```

### 7.2 Container architecture

```yaml
# docker-compose.yml structure
services:
  studio:
    image: agentflow-studio:latest
    ports: ["3000:3000"]
    
  core:
    image: agentflow-core:latest
    ports: ["8000:8000"]
    environment:
      - DATABASE_URL
      - REDIS_URL
      - OPENAI_API_KEY
    depends_on:
      - postgres
      - redis
      
  postgres:
    image: postgres:14
    volumes: ["pgdata:/var/lib/postgresql/data"]
    
  redis:
    image: redis:7
    volumes: ["redisdata:/data"]
```

### 7.3 Kubernetes deployment

| Resource | Replicas | Resources |
|----------|----------|-----------|
| Core API Pods | 3-10 | 512Mi-2Gi RAM, 0.5-2 CPU |
| Studio Pods | 2-5 | 256Mi-512Mi RAM, 0.25-0.5 CPU |
| PostgreSQL | 1 Primary + 2 Replicas | 4Gi RAM, 2 CPU |
| Redis | 3 (Cluster) | 1Gi RAM, 0.5 CPU |

---

## 8. Security architecture

### 8.1 Security layers

```
┌─────────────────────────────────────────────────────────────────┐
│                      Network Security                            │
│  - TLS 1.3 encryption                                           │
│  - WAF protection                                               │
│  - DDoS mitigation                                              │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                   Application Security                           │
│  - JWT authentication                                           │
│  - Role-based access control                                    │
│  - Input validation                                             │
│  - SQL injection prevention                                     │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                       Data Security                              │
│  - Encryption at rest (AES-256)                                 │
│  - Multi-tenant isolation                                       │
│  - Secret management (env vars)                                 │
│  - Audit logging                                                │
└─────────────────────────────────────────────────────────────────┘
```

### 8.2 Authentication flow

```
┌──────────┐    ┌──────────┐    ┌──────────┐    ┌──────────┐
│  Client  │───▶│  Auth    │───▶│   Core   │───▶│ Protected│
│          │    │  Server  │    │   API    │    │ Resource │
└──────────┘    └──────────┘    └──────────┘    └──────────┘
     │               │               │               │
     │ Login         │               │               │
     ├──────────────▶│               │               │
     │               │ Validate      │               │
     │               ├──────────────▶│               │
     │  JWT Token    │               │               │
     │◀──────────────┤               │               │
     │               │               │               │
     │ Request + JWT │               │               │
     ├──────────────────────────────▶│               │
     │               │               │ Verify JWT   │
     │               │               ├──────────────▶│
     │               │               │               │
     │   Response    │               │               │
     │◀──────────────────────────────┤               │
```

### 8.3 Security considerations

| Area | Measures |
|------|----------|
| **API Key Management** | Environment variables only, never in code or logs |
| **CORS** | Restricted to Studio domain |
| **Rate Limiting** | Per-IP and per-user limits |
| **Input Validation** | Pydantic models, JSON schema validation |
| **SQL Injection** | Parameterized queries, ORM usage |
| **Multi-tenancy** | tenant_id filtering on all queries |
| **Audit Trail** | All operations logged with user context |
| **Secrets** | HashiCorp Vault integration (optional) |

---

## 9. Scalability and performance

### 9.1 Scaling strategy

| Component | Scaling Type | Trigger |
|-----------|--------------|---------|
| Core API | Horizontal | CPU > 70%, Response time > 200ms |
| Studio | Horizontal/CDN | Request count |
| PostgreSQL | Vertical + Read Replicas | Connection count, Query time |
| Redis | Cluster | Memory usage, Operations/sec |

### 9.2 Performance optimizations

| Area | Optimization |
|------|--------------|
| **API Response** | Response caching, connection pooling |
| **Workflow Compilation** | Compiled graph caching |
| **Database** | Query optimization, indexing, connection pooling |
| **Frontend** | Code splitting, lazy loading, CDN |
| **LLM Calls** | Request batching, response streaming |

### 9.3 Caching architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         Request                                  │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                      L1: API Cache                               │
│                    (In-memory, 1 min TTL)                        │
└─────────────────────────────────────────────────────────────────┘
                              │ Miss
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                      L2: Redis Cache                             │
│                    (Distributed, 10 min TTL)                     │
└─────────────────────────────────────────────────────────────────┘
                              │ Miss
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                      L3: Database                                │
│                    (Persistent storage)                          │
└─────────────────────────────────────────────────────────────────┘
```

---

## 10. Technology decisions

### 10.1 Technology selection rationale

| Technology | Alternatives Considered | Selection Rationale |
|------------|------------------------|---------------------|
| **FastAPI** | Flask, Django | Async support, OpenAPI docs, Pydantic integration |
| **LangGraph** | LangChain, Custom | Native graph execution, state management |
| **PostgreSQL** | MySQL, MongoDB | ACID compliance, JSON support, reliability |
| **Redis** | Memcached | Persistence, pub/sub, data structures |
| **Next.js** | React SPA, Vue | SSR, App Router, API routes, TypeScript |
| **React Flow** | D3.js, Cytoscape | React integration, performance, features |
| **Zustand** | Redux, MobX | Simplicity, React 19 compatibility |
| **TailwindCSS** | CSS Modules, Styled | Utility-first, design system integration |

### 10.2 Technology stack summary

```
┌─────────────────────────────────────────────────────────────────┐
│                        Frontend Stack                            │
│  Next.js 16 │ React 19 │ TypeScript │ React Flow │ Zustand     │
│  TailwindCSS │ ShadCN UI │ Turbopack                           │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│                        Backend Stack                             │
│  Python 3.11+ │ FastAPI │ LangGraph │ Pydantic │ AsyncIO       │
│  OpenAI SDK │ psycopg │ httpx │ Redis                          │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│                      Infrastructure                              │
│  Docker │ Kubernetes │ PostgreSQL │ Redis │ nginx              │
└─────────────────────────────────────────────────────────────────┘
```

---

## 11. Future roadmap

### 11.1 Planned features

| Feature | Description | Target |
|---------|-------------|--------|
| **Workflow Versioning** | Save multiple versions, diff, rollback | Q1 2026 |
| **Real-time Graph Trace** | Visual replay of workflow execution | Q1 2026 |
| **Logs Dashboard** | Token usage, latency, cost per node | Q2 2026 |
| **Node Marketplace** | Custom node plugins, community contributions | Q2 2026 |
| **Python SDK** | `client.execute(workflow_id, input)` | Q1 2026 |
| **Streaming Execution** | Real-time output streaming | Q2 2026 |
| **Collaborative Editing** | Real-time multi-user editing | Q3 2026 |
| **Webhook Triggers** | Event-triggered workflow execution | Q2 2026 |

### 11.2 Scalability roadmap

| Phase | Target | Timeline |
|-------|--------|----------|
| **Phase 1** | 100 concurrent users, 1000 workflows | Launch |
| **Phase 2** | 1000 concurrent users, 10000 workflows | +6 months |
| **Phase 3** | 10000 concurrent users, 100000 workflows | +12 months |

---

## Appendix A: Glossary

| Term | Definition |
|------|------------|
| **LangGraph** | Python library for building stateful graphs over LLMs |
| **StateGraph** | LangGraph class for defining workflow graphs |
| **WorkflowSpec** | Complete JSON specification for a workflow |
| **GraphState** | State object passed between nodes |
| **Tenant** | Organizational unit for data isolation |

---

**Document Approval**

| Role | Name | Date | Signature |
|------|------|------|-----------|
| Chief Architect | _______________ | _______________ | _______________ |
| Tech Lead | _______________ | _______________ | _______________ |
| Engineering Manager | _______________ | _______________ | _______________ |
