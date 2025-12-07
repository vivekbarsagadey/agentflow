# Sequence Diagrams

# AgentFlow Sequence Diagrams v1.0

**Version:** 1.0.0  
**Date:** December 7, 2025  
**Status:** Approved

---

## Table of Contents

1. [Overview](#1-overview)
2. [Workflow creation sequence](#2-workflow-creation-sequence)
3. [Workflow validation sequence](#3-workflow-validation-sequence)
4. [Workflow execution sequence](#4-workflow-execution-sequence)
5. [Source management sequence](#5-source-management-sequence)
6. [Authentication sequence](#6-authentication-sequence)
7. [Error handling sequences](#7-error-handling-sequences)
8. [Node execution sequences](#8-node-execution-sequences)

---

## 1. Overview

### 1.1 Diagram notation

```
Actor          Component      Database       External
  │               │               │              │
  │  Request      │               │              │
  ├──────────────>│               │              │
  │               │  Query        │              │
  │               ├──────────────>│              │
  │               │               │              │
  │               │  Result       │              │
  │               │<──────────────┤              │
  │  Response     │               │              │
  │<──────────────┤               │              │
  │               │               │              │
```

### 1.2 Actors and components

| Symbol | Name | Description |
|--------|------|-------------|
| `User` | End User | Workflow designer/engineer |
| `Studio` | AgentFlow Studio | Next.js frontend application |
| `Core` | AgentFlow Core | FastAPI backend API |
| `Validator` | Validator Module | Workflow validation logic |
| `Builder` | Builder Module | LangGraph graph builder |
| `Executor` | Executor Module | Workflow execution engine |
| `Registry` | Registry Module | Source/queue storage |
| `DB` | PostgreSQL | Persistent storage |
| `Redis` | Redis | Rate limiting/cache |
| `OpenAI` | OpenAI API | External LLM service |
| `DALL-E` | DALL-E API | External image service |

---

## 2. Workflow creation sequence

### 2.1 Create workflow via Studio

```
User          Studio        Core          Validator     Registry      DB
 │              │            │                │            │          │
 │ Open Designer│            │                │            │          │
 ├─────────────>│            │                │            │          │
 │              │            │                │            │          │
 │              │ Load UI    │                │            │          │
 │              │            │                │            │          │
 │ Drag Node    │            │                │            │          │
 ├─────────────>│            │                │            │          │
 │              │            │                │            │          │
 │              │ Update     │                │            │          │
 │              │ State      │                │            │          │
 │              │            │                │            │          │
 │ Connect Nodes│            │                │            │          │
 ├─────────────>│            │                │            │          │
 │              │            │                │            │          │
 │              │ Update     │                │            │          │
 │              │ State      │                │            │          │
 │              │            │                │            │          │
 │ Add Source   │            │                │            │          │
 ├─────────────>│            │                │            │          │
 │              │            │                │            │          │
 │              │ Update     │                │            │          │
 │              │ State      │                │            │          │
 │              │            │                │            │          │
 │ Click Save   │            │                │            │          │
 ├─────────────>│            │                │            │          │
 │              │            │                │            │          │
 │              │ POST /workflows             │            │          │
 │              ├───────────>│                │            │          │
 │              │            │                │            │          │
 │              │            │ Validate       │            │          │
 │              │            ├───────────────>│            │          │
 │              │            │                │            │          │
 │              │            │ Schema + Logic │            │          │
 │              │            │ Check          │            │          │
 │              │            │                │            │          │
 │              │            │ Valid          │            │          │
 │              │            │<───────────────┤            │          │
 │              │            │                │            │          │
 │              │            │ Register Sources            │          │
 │              │            ├────────────────────────────>│          │
 │              │            │                │            │          │
 │              │            │ Save Workflow               │          │
 │              │            ├────────────────────────────────────────>│
 │              │            │                │            │          │
 │              │            │ Workflow ID                 │          │
 │              │            │<────────────────────────────────────────┤
 │              │            │                │            │          │
 │              │ 201 Created│                │            │          │
 │              │ + workflow │                │            │          │
 │              │<───────────┤                │            │          │
 │              │            │                │            │          │
 │ Success      │            │                │            │          │
 │ Message      │            │                │            │          │
 │<─────────────┤            │                │            │          │
```

### 2.2 Create workflow via API

```
Client        Core          Validator     DB
 │              │                │          │
 │ POST /workflows              │          │
 │ + WorkflowSpec               │          │
 ├─────────────>│                │          │
 │              │                │          │
 │              │ Parse JSON     │          │
 │              │                │          │
 │              │ Validate       │          │
 │              ├───────────────>│          │
 │              │                │          │
 │              │ Check Schema   │          │
 │              │ Check References│         │
 │              │                │          │
 │              │ Errors/Valid   │          │
 │              │<───────────────┤          │
 │              │                │          │
 │              │ INSERT workflow│          │
 │              ├───────────────────────────>│
 │              │                │          │
 │              │ workflow_id    │          │
 │              │<───────────────────────────┤
 │              │                │          │
 │ 201 Created  │                │          │
 │ + workflow_id│                │          │
 │<─────────────┤                │          │
```

---

## 3. Workflow validation sequence

### 3.1 Validation flow

```
Studio        Core          Validator     Registry
 │              │                │            │
 │ POST /workflows/validate     │            │
 │ + WorkflowSpec               │            │
 ├─────────────>│                │            │
 │              │                │            │
 │              │ Parse JSON     │            │
 │              │                │            │
 │              │ Validate       │            │
 │              ├───────────────>│            │
 │              │                │            │
 │              │                │ Check Schema
 │              │                │            │
 │              │                │ Collect node IDs
 │              │                │            │
 │              │                │ Check start_node exists
 │              │                │            │
 │              │                │ Check edges reference valid nodes
 │              │                │            │
 │              │                │ Check queues reference valid nodes
 │              │                │            │
 │              │                │ Check nodes have sources
 │              │                │            │
 │              │                │ Detect cycles
 │              │                │            │
 │              │ ValidationResult│           │
 │              │ (valid: true/false)         │
 │              │ (errors: [...])│            │
 │              │<───────────────┤            │
 │              │                │            │
 │ 200 OK       │                │            │
 │ + validation │                │            │
 │   result     │                │            │
 │<─────────────┤                │            │
```

### 3.2 Validation with errors

```
Studio        Core          Validator
 │              │                │
 │ POST /workflows/validate     │
 │ + WorkflowSpec (invalid)     │
 ├─────────────>│                │
 │              │                │
 │              │ Validate       │
 │              ├───────────────>│
 │              │                │
 │              │ Check Schema   │
 │              │ ❌ Error: Start node 'xyz' not found
 │              │                │
 │              │ Check Edges    │
 │              │ ❌ Error: Edge references non-existent node
 │              │                │
 │              │ Errors: [...]  │
 │              │<───────────────┤
 │              │                │
 │ 400 Bad Request              │
 │ + errors list│                │
 │<─────────────┤                │
```

---

## 4. Workflow execution sequence

### 4.1 Complete execution flow

```
Studio    Core      Validator  Builder   Registry  Executor  Redis     OpenAI
 │          │           │          │         │         │        │         │
 │ POST /workflows/execute       │         │         │        │         │
 │ + workflow│           │          │         │         │        │         │
 │ + initial_state       │          │         │         │        │         │
 ├─────────>│           │          │         │         │        │         │
 │          │           │          │         │         │        │         │
 │          │ Validate  │          │         │         │        │         │
 │          ├──────────>│          │         │         │        │         │
 │          │           │          │         │         │        │         │
 │          │ Valid     │          │         │         │        │         │
 │          │<──────────┤          │         │         │        │         │
 │          │           │          │         │         │        │         │
 │          │ Build Graph          │         │         │        │         │
 │          ├──────────────────────>│         │         │        │         │
 │          │           │          │         │         │        │         │
 │          │           │          │ Register│         │        │         │
 │          │           │          │ Sources │         │        │         │
 │          │           │          ├────────>│         │        │         │
 │          │           │          │         │         │        │         │
 │          │           │          │ Register│         │        │         │
 │          │           │          │ Queues  │         │        │         │
 │          │           │          ├────────>│         │        │         │
 │          │           │          │         │         │        │         │
 │          │           │          │ Create  │         │        │         │
 │          │           │          │ Nodes   │         │        │         │
 │          │           │          │         │         │        │         │
 │          │           │          │ Add     │         │        │         │
 │          │           │          │ Edges   │         │        │         │
 │          │           │          │         │         │        │         │
 │          │ Compiled Graph       │         │         │        │         │
 │          │<──────────────────────┤         │         │        │         │
 │          │           │          │         │         │        │         │
 │          │ Execute Workflow                │         │        │         │
 │          ├────────────────────────────────────────>│        │         │
 │          │           │          │         │         │        │         │
 │          │           │          │         │         │ Invoke │         │
 │          │           │          │         │         │ input_node       │
 │          │           │          │         │         │        │         │
 │          │           │          │         │         │ Invoke │         │
 │          │           │          │         │         │ router_node      │
 │          │           │          │         │         │        │         │
 │          │           │          │         │         │ Check Rate Limit │
 │          │           │          │         │         ├───────>│         │
 │          │           │          │         │         │        │         │
 │          │           │          │         │         │ OK     │         │
 │          │           │          │         │         │<───────┤         │
 │          │           │          │         │         │        │         │
 │          │           │          │         │         │ Invoke │         │
 │          │           │          │         │         │ llm_node         │
 │          │           │          │         │         │        │         │
 │          │           │          │         │         │ Get Source       │
 │          │           │          │         ├────────>│        │         │
 │          │           │          │         │         │        │         │
 │          │           │          │         │ Source  │        │         │
 │          │           │          │         │<────────┤        │         │
 │          │           │          │         │         │        │         │
 │          │           │          │         │         │ Call LLM         │
 │          │           │          │         │         ├────────────────>│
 │          │           │          │         │         │        │         │
 │          │           │          │         │         │ Response         │
 │          │           │          │         │         │<────────────────┤
 │          │           │          │         │         │        │         │
 │          │           │          │         │         │ Update State     │
 │          │           │          │         │         │        │         │
 │          │           │          │         │         │ Invoke │         │
 │          │           │          │         │         │ aggregator_node  │
 │          │           │          │         │         │        │         │
 │          │           │          │         │         │ Create final_output
 │          │           │          │         │         │        │         │
 │          │ Final State                    │         │        │         │
 │          │<────────────────────────────────────────┤        │         │
 │          │           │          │         │         │        │         │
 │ 200 OK   │           │          │         │         │        │         │
 │ + final_state        │          │         │         │        │         │
 │<─────────┤           │          │         │         │        │         │
```

### 4.2 Execution with rate limiting

```
Executor     Redis        OpenAI
   │           │             │
   │ Invoke llm_node        │
   │           │             │
   │ Check Rate Limit       │
   ├──────────>│             │
   │           │             │
   │           │ Check tokens_used
   │           │ Check requests_per_minute
   │           │             │
   │ Rate Limited            │
   │ (wait 500ms)            │
   │<──────────┤             │
   │           │             │
   │ Sleep 500ms             │
   │           │             │
   │ Retry     │             │
   ├──────────>│             │
   │           │             │
   │ OK        │             │
   │<──────────┤             │
   │           │             │
   │ Call LLM                │
   ├────────────────────────>│
   │           │             │
   │ Response                │
   │<────────────────────────┤
```

### 4.3 Execution failure scenario

```
Studio    Core      Executor   OpenAI
 │          │           │         │
 │ POST /workflows/execute       │
 ├─────────>│           │         │
 │          │           │         │
 │          │ Execute   │         │
 │          ├──────────>│         │
 │          │           │         │
 │          │           │ Call LLM│
 │          │           ├────────>│
 │          │           │         │
 │          │           │ ❌ Error: Rate limit exceeded
 │          │           │<────────┤
 │          │           │         │
 │          │           │ Throw Exception
 │          │           │         │
 │          │ Error     │         │
 │          │<──────────┤         │
 │          │           │         │
 │ 500 Internal Server Error     │
 │ + error_message       │         │
 │<─────────┤           │         │
```

---

## 5. Source management sequence

### 5.1 Create source

```
Studio        Core          Registry      DB
 │              │               │          │
 │ POST /sources│               │          │
 │ + source_spec│               │          │
 ├─────────────>│               │          │
 │              │               │          │
 │              │ Validate      │          │
 │              │ Source        │          │
 │              │               │          │
 │              │ Check Exists  │          │
 │              ├──────────────>│          │
 │              │               │          │
 │              │ Not Found     │          │
 │              │<──────────────┤          │
 │              │               │          │
 │              │ Save Source              │
 │              ├─────────────────────────>│
 │              │               │          │
 │              │ source_id                │
 │              │<─────────────────────────┤
 │              │               │          │
 │              │ Register                 │
 │              ├──────────────>│          │
 │              │               │          │
 │ 201 Created  │               │          │
 │ + source     │               │          │
 │<─────────────┤               │          │
```

### 5.2 List sources

```
Studio        Core          Registry      DB
 │              │               │          │
 │ GET /sources │               │          │
 ├─────────────>│               │          │
 │              │               │          │
 │              │ Load Sources             │
 │              ├─────────────────────────>│
 │              │               │          │
 │              │ sources[]                │
 │              │<─────────────────────────┤
 │              │               │          │
 │ 200 OK       │               │          │
 │ + sources[]  │               │          │
 │<─────────────┤               │          │
```

### 5.3 Update source

```
Studio        Core          Registry      DB
 │              │               │          │
 │ PUT /sources/{id}            │          │
 │ + updated_source             │          │
 ├─────────────>│               │          │
 │              │               │          │
 │              │ Check Exists             │
 │              ├─────────────────────────>│
 │              │               │          │
 │              │ Found                    │
 │              │<─────────────────────────┤
 │              │               │          │
 │              │ Update Source            │
 │              ├─────────────────────────>│
 │              │               │          │
 │              │ Success                  │
 │              │<─────────────────────────┤
 │              │               │          │
 │              │ Update Registry          │
 │              ├──────────────>│          │
 │              │               │          │
 │ 200 OK       │               │          │
 │ + source     │               │          │
 │<─────────────┤               │          │
```

### 5.4 Delete source

```
Studio        Core          Registry      DB
 │              │               │          │
 │ DELETE /sources/{id}         │          │
 ├─────────────>│               │          │
 │              │               │          │
 │              │ Check In Use             │
 │              ├─────────────────────────>│
 │              │               │          │
 │              │ Not Used                 │
 │              │<─────────────────────────┤
 │              │               │          │
 │              │ Soft Delete              │
 │              ├─────────────────────────>│
 │              │               │          │
 │              │ Success                  │
 │              │<─────────────────────────┤
 │              │               │          │
 │              │ Remove from Registry     │
 │              ├──────────────>│          │
 │              │               │          │
 │ 200 OK       │               │          │
 │<─────────────┤               │          │
```

---

## 6. Authentication sequence

### 6.1 API key authentication

```
Client        Core          Auth Module   DB
 │              │               │          │
 │ POST /workflows/execute     │          │
 │ Header: X-API-Key           │          │
 ├─────────────>│               │          │
 │              │               │          │
 │              │ Extract Key   │          │
 │              │               │          │
 │              │ Validate Key  │          │
 │              ├──────────────>│          │
 │              │               │          │
 │              │               │ Check key_hash
 │              │               ├─────────>│
 │              │               │          │
 │              │               │ Key found│
 │              │               │ + user_id│
 │              │               │<─────────┤
 │              │               │          │
 │              │ Valid         │          │
 │              │ + user_id     │          │
 │              │<──────────────┤          │
 │              │               │          │
 │              │ Process Request          │
 │              │               │          │
 │ 200 OK       │               │          │
 │<─────────────┤               │          │
```

### 6.2 Invalid API key

```
Client        Core          Auth Module
 │              │               │
 │ POST /workflows/execute     │
 │ Header: X-API-Key (invalid) │
 ├─────────────>│               │
 │              │               │
 │              │ Validate Key  │
 │              ├──────────────>│
 │              │               │
 │              │ Invalid       │
 │              │<──────────────┤
 │              │               │
 │ 401 Unauthorized            │
 │ + error      │               │
 │<─────────────┤               │
```

### 6.3 JWT authentication (future)

```
Client        Core          Auth Server   DB
 │              │               │          │
 │ POST /auth/login            │          │
 │ + credentials │               │          │
 ├─────────────────────────────>│          │
 │              │               │          │
 │              │               │ Verify   │
 │              │               ├─────────>│
 │              │               │          │
 │              │               │ Valid    │
 │              │               │<─────────┤
 │              │               │          │
 │              │ JWT Token     │          │
 │<─────────────────────────────┤          │
 │              │               │          │
 │ POST /workflows/execute     │          │
 │ Header: Authorization: Bearer <JWT>    │
 ├─────────────>│               │          │
 │              │               │          │
 │              │ Verify JWT    │          │
 │              ├──────────────>│          │
 │              │               │          │
 │              │ Valid         │          │
 │              │ + user_id     │          │
 │              │<──────────────┤          │
 │              │               │          │
 │              │ Process Request          │
 │              │               │          │
 │ 200 OK       │               │          │
 │<─────────────┤               │          │
```

---

## 7. Error handling sequences

### 7.1 Validation error

```
Studio        Core          Validator
 │              │               │
 │ POST /workflows/validate     │
 │ + invalid_spec│               │
 ├─────────────>│               │
 │              │               │
 │              │ Validate      │
 │              ├──────────────>│
 │              │               │
 │              │ ❌ Errors found│
 │              │<──────────────┤
 │              │               │
 │ 400 Bad Request              │
 │ + validation_errors          │
 │<─────────────┤               │
 │              │               │
 │ Display Errors│              │
 │ in UI        │               │
```

### 7.2 External service failure

```
Executor     OpenAI
   │           │
   │ Call LLM  │
   ├──────────>│
   │           │
   │ ❌ 503 Service Unavailable
   │<──────────┤
   │           │
   │ Retry (1) │
   ├──────────>│
   │           │
   │ ❌ Timeout│
   │<──────────┤
   │           │
   │ Retry (2) │
   ├──────────>│
   │           │
   │ ❌ Timeout│
   │<──────────┤
   │           │
   │ Give Up   │
   │           │
   │ Throw ServiceUnavailableError
```

### 7.3 Database connection failure

```
Core          DB
 │             │
 │ Query       │
 ├────────────>│
 │             │
 │ ❌ Connection refused
 │<────────────┤
 │             │
 │ Retry (1)   │
 ├────────────>│
 │             │
 │ ❌ Timeout  │
 │<────────────┤
 │             │
 │ Circuit Breaker OPEN
 │             │
 │ Return 503 Service Unavailable
```

---

## 8. Node execution sequences

### 8.1 LLM node execution

```
Executor     Registry     Source       Redis        OpenAI
   │            │           │            │             │
   │ Invoke llm_node        │            │             │
   │            │           │            │             │
   │ Get metadata           │            │             │
   ├───────────>│           │            │             │
   │            │           │            │             │
   │ source_id  │           │            │             │
   │<───────────┤           │            │             │
   │            │           │            │             │
   │ Get source │           │            │             │
   ├───────────>│           │            │             │
   │            │           │            │             │
   │ source_config          │            │             │
   │<───────────┤           │            │             │
   │            │           │            │             │
   │ Get client │           │            │             │
   ├────────────────────────>│            │             │
   │            │           │            │             │
   │ OpenAI client          │            │             │
   │<────────────────────────┤            │             │
   │            │           │            │             │
   │ Check rate limit                    │             │
   ├────────────────────────────────────>│             │
   │            │           │            │             │
   │ OK         │           │            │             │
   │<────────────────────────────────────┤             │
   │            │           │            │             │
   │ chat.completions.create                           │
   ├──────────────────────────────────────────────────>│
   │            │           │            │             │
   │ Response (text_result)                            │
   │<──────────────────────────────────────────────────┤
   │            │           │            │             │
   │ Update state           │            │             │
   │ (text_result, tokens_used)           │             │
   │            │           │            │             │
   │ Return state           │            │             │
```

### 8.2 Image node execution

```
Executor     Registry     Source       DALL-E
   │            │           │             │
   │ Invoke image_node      │             │
   │            │           │             │
   │ Get source │           │             │
   ├───────────>│           │             │
   │            │           │             │
   │ source     │           │             │
   │<───────────┤           │             │
   │            │           │             │
   │ Get client │           │             │
   ├────────────────────────>│             │
   │            │           │             │
   │ OpenAI client          │             │
   │<────────────────────────┤             │
   │            │           │             │
   │ images.generate                       │
   │ (prompt, size)                        │
   ├──────────────────────────────────────>│
   │            │           │             │
   │ Image URL                             │
   │<──────────────────────────────────────┤
   │            │           │             │
   │ Update state           │             │
   │ (image_result)         │             │
   │            │           │             │
   │ Return state           │             │
```

### 8.3 Database node execution

```
Executor     Registry     Source       PostgreSQL
   │            │           │             │
   │ Invoke db_node         │             │
   │            │           │             │
   │ Get source │           │             │
   ├───────────>│           │             │
   │            │           │             │
   │ source     │           │             │
   │<───────────┤           │             │
   │            │           │             │
   │ Get connection         │             │
   ├────────────────────────>│             │
   │            │           │             │
   │            │           │ Connect     │
   │            │           ├────────────>│
   │            │           │             │
   │            │           │ Connection  │
   │            │           │<────────────┤
   │            │           │             │
   │ Connection │           │             │
   │<────────────────────────┤             │
   │            │           │             │
   │ Execute query                         │
   ├──────────────────────────────────────>│
   │            │           │             │
   │ Results                               │
   │<──────────────────────────────────────┤
   │            │           │             │
   │ Update state           │             │
   │ (db_result)            │             │
   │            │           │             │
   │ Return state           │             │
```

### 8.4 Router node execution

```
Executor     State
   │            │
   │ Invoke router_node
   │            │
   │ Get user_input
   ├───────────>│
   │            │
   │ user_input │
   │<───────────┤
   │            │
   │ Classify intent
   │ (keyword-based or LLM)
   │            │
   │ Update state
   │ (intent)   │
   ├───────────>│
   │            │
   │ Return state
   │<───────────┤
```

### 8.5 Aggregator node execution

```
Executor     State
   │            │
   │ Invoke aggregator_node
   │            │
   │ Get all results
   ├───────────>│
   │            │
   │ text_result│
   │ image_result
   │ db_result  │
   │<───────────┤
   │            │
   │ Combine into
   │ final_output
   │            │
   │ Update state
   │ (final_output)
   ├───────────>│
   │            │
   │ Return state
   │<───────────┤
```

---

**Document Approval**

| Role | Name | Date | Signature |
|------|------|------|-----------|
| System Architect | _______________ | _______________ | _______________ |
| Backend Engineer | _______________ | _______________ | _______________ |
| QA Engineer | _______________ | _______________ | _______________ |
