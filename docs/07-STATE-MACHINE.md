# State Machine Documentation

# AgentFlow State Machine v1.0

**Version:** 1.0.0  
**Date:** December 7, 2025  
**Status:** Approved

---

## Table of Contents

1. [Overview](#1-overview)
2. [GraphState state machine](#2-graphstate-state-machine)
3. [Workflow execution state machine](#3-workflow-execution-state-machine)
4. [Workflow lifecycle state machine](#4-workflow-lifecycle-state-machine)
5. [Source state machine](#5-source-state-machine)
6. [API key state machine](#6-api-key-state-machine)
7. [Node execution states](#7-node-execution-states)

---

## 1. Overview

### 1.1 State machine purpose

AgentFlow uses state machines to:

- **Control workflow execution** - Manage state transitions during runtime
- **Track workflow lifecycle** - Draft → Published → Archived
- **Manage sources** - Active → Inactive → Deleted
- **Monitor API keys** - Active → Revoked → Expired
- **Handle node execution** - Pending → Running → Completed/Failed

### 1.2 State machine notation

```
┌─────────────┐
│   State     │  ← State box
└─────────────┘
      │
      │ event / condition  ← Transition label
      ▼
┌─────────────┐
│   State     │
└─────────────┘
      │
      │ [final]  ← Final state indicator
      ▼
   ●  ← End state
```

### 1.3 State types

| Type | Description | Example |
|------|-------------|---------|
| **Initial** | Starting state | `PENDING`, `DRAFT` |
| **Intermediate** | Transitional state | `RUNNING`, `PROCESSING` |
| **Final** | Terminal state | `COMPLETED`, `DELETED` |
| **Error** | Error state | `FAILED`, `CANCELLED` |

---

## 2. GraphState state machine

### 2.1 State diagram

```
                    [Workflow Execution Begins]
                              │
                              ▼
                    ┌─────────────────┐
                    │     INITIAL     │
                    │                 │
                    │ user_input set  │
                    └─────────────────┘
                              │
                              │ start workflow
                              ▼
                    ┌─────────────────┐
                    │   INPUT_NODE    │
                    │                 │
                    │ Process input   │
                    └─────────────────┘
                              │
                              │ route to next node
                              ▼
                    ┌─────────────────┐
                    │  ROUTER_NODE    │
                    │                 │
                    │ Determine intent│
                    └─────────────────┘
                              │
                    ┌─────────┼─────────┐
                    │         │         │
          text      │    image│    data │
                    │         │         │
                    ▼         ▼         ▼
          ┌─────────────┐ ┌─────────────┐ ┌─────────────┐
          │  LLM_NODE   │ │ IMAGE_NODE  │ │   DB_NODE   │
          │             │ │             │ │             │
          │ text_result │ │image_result │ │  db_result  │
          └─────────────┘ └─────────────┘ └─────────────┘
                    │         │         │
                    └─────────┼─────────┘
                              │
                              │ aggregate results
                              ▼
                    ┌─────────────────┐
                    │ AGGREGATOR_NODE │
                    │                 │
                    │ final_output    │
                    └─────────────────┘
                              │
                              │ [final]
                              ▼
                    ┌─────────────────┐
                    │    COMPLETED    │
                    │                 │
                    │ Return state    │
                    └─────────────────┘
                              │
                              ▼
                             ●
```

### 2.2 State transitions

| From State | To State | Event | Condition |
|------------|----------|-------|-----------|
| `INITIAL` | `INPUT_NODE` | workflow start | user_input provided |
| `INPUT_NODE` | `ROUTER_NODE` | input processed | valid input |
| `ROUTER_NODE` | `LLM_NODE` | intent determined | intent == 'text' |
| `ROUTER_NODE` | `IMAGE_NODE` | intent determined | intent == 'image' |
| `ROUTER_NODE` | `DB_NODE` | intent determined | intent == 'database' |
| `LLM_NODE` | `AGGREGATOR_NODE` | LLM completed | text_result set |
| `IMAGE_NODE` | `AGGREGATOR_NODE` | image generated | image_result set |
| `DB_NODE` | `AGGREGATOR_NODE` | query executed | db_result set |
| `AGGREGATOR_NODE` | `COMPLETED` | aggregation done | final_output set |

### 2.3 State attributes

**INITIAL:**
```json
{
  "user_input": "Tell me about quantum computing",
  "metadata": {
    "start_time": 1701234567.890
  }
}
```

**INPUT_NODE:**
```json
{
  "user_input": "Tell me about quantum computing",
  "metadata": {
    "start_time": 1701234567.890,
    "input_processed": true
  }
}
```

**ROUTER_NODE:**
```json
{
  "user_input": "Tell me about quantum computing",
  "intent": "text",
  "metadata": {
    "start_time": 1701234567.890,
    "input_processed": true,
    "intent_determined": true
  }
}
```

**LLM_NODE:**
```json
{
  "user_input": "Tell me about quantum computing",
  "intent": "text",
  "text_result": "Quantum computing is...",
  "tokens_used": 150,
  "metadata": {
    "start_time": 1701234567.890,
    "llm_duration": 2.5
  }
}
```

**AGGREGATOR_NODE:**
```json
{
  "user_input": "Tell me about quantum computing",
  "intent": "text",
  "text_result": "Quantum computing is...",
  "final_output": {
    "text": "Quantum computing is..."
  },
  "tokens_used": 150,
  "metadata": {
    "start_time": 1701234567.890,
    "llm_duration": 2.5,
    "aggregation_complete": true
  }
}
```

**COMPLETED:**
```json
{
  "user_input": "Tell me about quantum computing",
  "intent": "text",
  "text_result": "Quantum computing is...",
  "final_output": {
    "text": "Quantum computing is..."
  },
  "tokens_used": 150,
  "metadata": {
    "start_time": 1701234567.890,
    "end_time": 1701234570.123,
    "execution_time": 2.233
  }
}
```

---

## 3. Workflow execution state machine

### 3.1 State diagram

```
                    [Execution Request]
                              │
                              ▼
                    ┌─────────────────┐
                    │     PENDING     │
                    │                 │
                    │ Awaiting start  │
                    └─────────────────┘
                              │
                              │ validate & start
                              ▼
                    ┌─────────────────┐
                    │    RUNNING      │
                    │                 │
                    │ Executing nodes │
                    └─────────────────┘
                              │
                    ┌─────────┼─────────┐
                    │         │         │
              success│    error│   cancel│
                    │         │         │
                    ▼         ▼         ▼
          ┌─────────────┐ ┌─────────────┐ ┌─────────────┐
          │  COMPLETED  │ │   FAILED    │ │  CANCELLED  │
          │             │ │             │ │             │
          │ [final]     │ │  [error]    │ │  [final]    │
          └─────────────┘ └─────────────┘ └─────────────┘
                    │         │         │
                    └─────────┼─────────┘
                              │
                              ▼
                             ●
```

### 3.2 State transitions

| From State | To State | Event | Condition |
|------------|----------|-------|-----------|
| `PENDING` | `RUNNING` | start execution | validation passed |
| `RUNNING` | `COMPLETED` | workflow finished | all nodes succeeded |
| `RUNNING` | `FAILED` | error occurred | node threw exception |
| `RUNNING` | `CANCELLED` | user cancellation | user triggered cancel |

### 3.3 State attributes

**PENDING:**
```json
{
  "status": "pending",
  "initial_state": {"user_input": "..."},
  "started_at": null,
  "completed_at": null
}
```

**RUNNING:**
```json
{
  "status": "running",
  "initial_state": {"user_input": "..."},
  "started_at": "2025-12-07T10:30:00Z",
  "completed_at": null,
  "current_node": "llm"
}
```

**COMPLETED:**
```json
{
  "status": "completed",
  "initial_state": {"user_input": "..."},
  "final_state": {"final_output": "..."},
  "started_at": "2025-12-07T10:30:00Z",
  "completed_at": "2025-12-07T10:30:02Z",
  "execution_time": 2.5,
  "tokens_used": 150
}
```

**FAILED:**
```json
{
  "status": "failed",
  "initial_state": {"user_input": "..."},
  "error_message": "OpenAI API error: Rate limit exceeded",
  "started_at": "2025-12-07T10:30:00Z",
  "completed_at": "2025-12-07T10:30:01Z",
  "failed_node": "llm"
}
```

---

## 4. Workflow lifecycle state machine

### 4.1 State diagram

```
                    [Workflow Created]
                              │
                              ▼
                    ┌─────────────────┐
                    │      DRAFT      │
                    │                 │
                    │ Being edited    │
                    └─────────────────┘
                              │
                    ┌─────────┼─────────┐
                    │         │         │
               publish│    delete│   edit│
                    │         │         │
                    ▼         ▼         │
          ┌─────────────┐ ┌─────────────┐ │
          │  PUBLISHED  │ │   DELETED   │ │
          │             │ │             │ │
          │ In use      │ │  [final]    │◄┘
          └─────────────┘ └─────────────┘
                    │         
                    │         
              archive│delete  
                    │         
                    ▼         
          ┌─────────────┐    
          │  ARCHIVED   │    
          │             │    
          │ Read-only   │    
          └─────────────┘    
                    │
               delete│
                    │
                    ▼
          ┌─────────────┐
          │   DELETED   │
          │             │
          │  [final]    │
          └─────────────┘
                    │
                    ▼
                   ●
```

### 4.2 State transitions

| From State | To State | Event | Condition |
|------------|----------|-------|-----------|
| `DRAFT` | `PUBLISHED` | publish | validation passed |
| `DRAFT` | `DELETED` | delete | user confirmed |
| `PUBLISHED` | `ARCHIVED` | archive | no longer needed |
| `PUBLISHED` | `DELETED` | delete | user confirmed |
| `PUBLISHED` | `DRAFT` | unpublish | edit needed |
| `ARCHIVED` | `DELETED` | delete | permanent removal |

### 4.3 State attributes

**DRAFT:**
```json
{
  "status": "draft",
  "name": "Customer Support Workflow",
  "spec": {...},
  "created_at": "2025-12-07T10:00:00Z",
  "updated_at": "2025-12-07T10:15:00Z"
}
```

**PUBLISHED:**
```json
{
  "status": "published",
  "name": "Customer Support Workflow",
  "spec": {...},
  "published_at": "2025-12-07T10:20:00Z",
  "version": 1
}
```

**ARCHIVED:**
```json
{
  "status": "archived",
  "name": "Customer Support Workflow",
  "spec": {...},
  "archived_at": "2025-12-07T12:00:00Z",
  "archived_by": "user_id"
}
```

**DELETED:**
```json
{
  "status": "deleted",
  "name": "Customer Support Workflow",
  "deleted_at": "2025-12-07T13:00:00Z",
  "deleted_by": "user_id"
}
```

---

## 5. Source state machine

### 5.1 State diagram

```
                    [Source Created]
                              │
                              ▼
                    ┌─────────────────┐
                    │     ACTIVE      │
                    │                 │
                    │ In use          │
                    └─────────────────┘
                              │
                    ┌─────────┼─────────┐
                    │         │         │
              deactivate│  delete│  activate│
                    │         │         │
                    ▼         ▼         │
          ┌─────────────┐ ┌─────────────┐ │
          │  INACTIVE   │ │   DELETED   │ │
          │             │ │             │ │
          │ Not in use  │ │  [final]    │◄┘
          └─────────────┘ └─────────────┘
                    │
               delete│
                    │
                    ▼
          ┌─────────────┐
          │   DELETED   │
          │             │
          │  [final]    │
          └─────────────┘
                    │
                    ▼
                   ●
```

### 5.2 State transitions

| From State | To State | Event | Condition |
|------------|----------|-------|-----------|
| `ACTIVE` | `INACTIVE` | deactivate | user action |
| `ACTIVE` | `DELETED` | delete | not in use |
| `INACTIVE` | `ACTIVE` | activate | user action |
| `INACTIVE` | `DELETED` | delete | permanent removal |

### 5.3 State attributes

**ACTIVE:**
```json
{
  "status": "active",
  "name": "OpenAI GPT-4",
  "kind": "llm",
  "config": {"model_name": "gpt-4"},
  "created_at": "2025-12-07T10:00:00Z"
}
```

**INACTIVE:**
```json
{
  "status": "inactive",
  "name": "OpenAI GPT-4",
  "kind": "llm",
  "config": {"model_name": "gpt-4"},
  "deactivated_at": "2025-12-07T12:00:00Z"
}
```

**DELETED:**
```json
{
  "status": "deleted",
  "name": "OpenAI GPT-4",
  "deleted_at": "2025-12-07T13:00:00Z",
  "deleted_by": "user_id"
}
```

---

## 6. API key state machine

### 6.1 State diagram

```
                    [API Key Created]
                              │
                              ▼
                    ┌─────────────────┐
                    │     ACTIVE      │
                    │                 │
                    │ Valid for use   │
                    └─────────────────┘
                              │
                    ┌─────────┼─────────┐
                    │         │         │
                revoke│   expire│         │
                    │         │         │
                    ▼         ▼         │
          ┌─────────────┐ ┌─────────────┐
          │   REVOKED   │ │   EXPIRED   │
          │             │ │             │
          │  [final]    │ │  [final]    │
          └─────────────┘ └─────────────┘
                    │         │
                    └─────────┘
                              │
                              ▼
                             ●
```

### 6.2 State transitions

| From State | To State | Event | Condition |
|------------|----------|-------|-----------|
| `ACTIVE` | `REVOKED` | revoke | user/admin action |
| `ACTIVE` | `EXPIRED` | time passed | expires_at reached |

### 6.3 State attributes

**ACTIVE:**
```json
{
  "status": "active",
  "name": "Production API Key",
  "key_hash": "$2b$12$...",
  "created_at": "2025-12-07T10:00:00Z",
  "expires_at": "2026-12-07T10:00:00Z",
  "last_used_at": "2025-12-07T11:30:00Z"
}
```

**REVOKED:**
```json
{
  "status": "revoked",
  "name": "Production API Key",
  "revoked_at": "2025-12-07T12:00:00Z",
  "revoked_by": "user_id",
  "reason": "Security concern"
}
```

**EXPIRED:**
```json
{
  "status": "expired",
  "name": "Production API Key",
  "expired_at": "2026-12-07T10:00:00Z"
}
```

---

## 7. Node execution states

### 7.1 Generic node state diagram

```
                    [Node Invoked]
                              │
                              ▼
                    ┌─────────────────┐
                    │     PENDING     │
                    │                 │
                    │ Awaiting exec   │
                    └─────────────────┘
                              │
                              │ check rate limit
                              ▼
                    ┌─────────────────┐
                    │  RATE_LIMITED   │
                    │                 │
                    │ Waiting...      │
                    └─────────────────┘
                              │
                              │ rate limit cleared
                              ▼
                    ┌─────────────────┐
                    │    RUNNING      │
                    │                 │
                    │ Executing logic │
                    └─────────────────┘
                              │
                    ┌─────────┼─────────┐
                    │         │         │
              success│    error│   timeout│
                    │         │         │
                    ▼         ▼         ▼
          ┌─────────────┐ ┌─────────────┐ ┌─────────────┐
          │  COMPLETED  │ │   FAILED    │ │  TIMED_OUT  │
          │             │ │             │ │             │
          │ [final]     │ │  [error]    │ │  [error]    │
          └─────────────┘ └─────────────┘ └─────────────┘
                    │         │         │
                    └─────────┼─────────┘
                              │
                              ▼
                             ●
```

### 7.2 Node state transitions

| From State | To State | Event | Condition |
|------------|----------|-------|-----------|
| `PENDING` | `RATE_LIMITED` | rate limit check | limit exceeded |
| `PENDING` | `RUNNING` | rate limit check | limit OK |
| `RATE_LIMITED` | `RUNNING` | time passed | limit cleared |
| `RUNNING` | `COMPLETED` | execution finished | success |
| `RUNNING` | `FAILED` | error occurred | exception thrown |
| `RUNNING` | `TIMED_OUT` | timeout | max duration exceeded |

### 7.3 Node-specific states

**LLM Node:**
```json
{
  "node_id": "llm",
  "status": "running",
  "started_at": "2025-12-07T10:30:00.500Z",
  "prompt": "Tell me about quantum computing",
  "tokens_sent": 10,
  "tokens_received": null
}
```

```json
{
  "node_id": "llm",
  "status": "completed",
  "started_at": "2025-12-07T10:30:00.500Z",
  "completed_at": "2025-12-07T10:30:02.800Z",
  "duration": 2.3,
  "tokens_sent": 10,
  "tokens_received": 140,
  "result": "Quantum computing is..."
}
```

**Image Node:**
```json
{
  "node_id": "image",
  "status": "running",
  "started_at": "2025-12-07T10:30:00.500Z",
  "prompt": "A sunset over mountains",
  "model": "dall-e-3"
}
```

```json
{
  "node_id": "image",
  "status": "completed",
  "started_at": "2025-12-07T10:30:00.500Z",
  "completed_at": "2025-12-07T10:30:08.200Z",
  "duration": 7.7,
  "result": {
    "url": "https://oaidalleapiprodscus.blob.core.windows.net/...",
    "size": "1024x1024"
  }
}
```

**Database Node:**
```json
{
  "node_id": "db",
  "status": "running",
  "started_at": "2025-12-07T10:30:00.500Z",
  "query": "SELECT * FROM users WHERE id = 1"
}
```

```json
{
  "node_id": "db",
  "status": "completed",
  "started_at": "2025-12-07T10:30:00.500Z",
  "completed_at": "2025-12-07T10:30:00.650Z",
  "duration": 0.15,
  "rows_returned": 1,
  "result": [{"id": 1, "name": "John Doe"}]
}
```

---

**Document Approval**

| Role | Name | Date | Signature |
|------|------|------|-----------|
| System Architect | _______________ | _______________ | _______________ |
| Backend Engineer | _______________ | _______________ | _______________ |
| QA Engineer | _______________ | _______________ | _______________ |
