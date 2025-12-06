**single combined file named `Schema.md`** that contains:

### ✅ Workflow Schema

### ✅ Node Schema

### ✅ Edge Schema

### ✅ Queue Schema

### ✅ Source Schema

### ✅ Execution State Schema

### ✅ With explanations + examples

### ❗ *NOT the JSON Schema draft format*, but a **clean human-readable schema document**.

Here is the complete **Schema.md**, structured exactly like a real engineering documentation file.

---

# 📄 **Schema.md — AgentFlow Unified Schema Specification**

**Version:** 1.0
**Audience:** Backend, Frontend, Architects, Flow Designer UI Team
**Purpose:** Defines the complete schema structure for workflows, nodes, edges, queues, sources, and execution state.

---

# -----------------------------------------------------------

# **1. Workflow Schema (Top-Level)**

# -----------------------------------------------------------

A workflow is defined as:

```json
{
  "start_node": "string",
  "nodes": [Node],
  "edges": [Edge],
  "queues": [Queue],
  "sources": [Source]
}
```

### **Fields**

| Field        | Type          | Description                                 |
| ------------ | ------------- | ------------------------------------------- |
| `start_node` | string        | Node where execution begins                 |
| `nodes`      | array<Node>   | All nodes used in the workflow              |
| `edges`      | array<Edge>   | Defines directional flow between nodes      |
| `queues`     | array<Queue>  | Defines bandwidth constraints between nodes |
| `sources`    | array<Source> | External resources used by nodes            |

---

# -----------------------------------------------------------

# **2. Node Schema**

# -----------------------------------------------------------

A **node** represents a computation unit (LLM call, router, input, etc.)

### **Structure:**

```json
{
  "id": "string",
  "type": "input | router | llm | image | db | aggregator",
  "metadata": {
    "source": "string",
    "config": {}
  }
}
```

### **Fields**

| Field             | Type   | Required                      | Description                        |
| ----------------- | ------ | ----------------------------- | ---------------------------------- |
| `id`              | string | yes                           | Unique identifier                  |
| `type`            | enum   | yes                           | Node type                          |
| `metadata.source` | string | only for llm, image, db nodes | References a Source ID             |
| `metadata.config` | object | optional                      | Node-specific custom configuration |

### **Supported Node Types**

| Type         | Description                        |
| ------------ | ---------------------------------- |
| `input`      | Accepts user input                 |
| `router`     | Routes flow to different branches  |
| `llm`        | Calls an LLM                       |
| `image`      | Calls image generation model       |
| `db`         | Executes database queries          |
| `aggregator` | Combines results into final output |

---

# -----------------------------------------------------------

# **3. Edge Schema**

# -----------------------------------------------------------

Defines the connections between nodes.

### **Structure:**

```json
{
  "from": "string",
  "to": "string | string[]"
}
```

### **Fields**

| Field  | Type                    | Required | Description               |
| ------ | ----------------------- | -------- | ------------------------- |
| `from` | string                  | yes      | Node ID where edge begins |
| `to`   | string or array<string> | yes      | Next node(s)              |

### Notes

* `router` nodes often have multiple `to` targets.
* Execution order is determined by LangGraph engine.

---

# -----------------------------------------------------------

# **4. Queue Schema**

# -----------------------------------------------------------

Queues define bandwidth and control for node-to-node communication.

### **Structure:**

```json
{
  "id": "string",
  "from": "string",
  "to": "string",
  "bandwidth": {
    "max_messages_per_second": 1,
    "max_requests_per_minute": 30,
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

### **Fields**

| Field       | Type   | Required | Description                 |
| ----------- | ------ | -------- | --------------------------- |
| `id`        | string | yes      | Queue identifier            |
| `from`      | string | yes      | Node ID                     |
| `to`        | string | yes      | Node ID                     |
| `bandwidth` | object | optional | Rate limiting rules         |
| `subqueues` | array  | optional | Weighted execution priority |

---

# -----------------------------------------------------------

# **5. Source Schema**

# -----------------------------------------------------------

A **source** defines an external system such as LLM, image model, database, or API.

### **Structure:**

```json
{
  "id": "string",
  "kind": "llm | image | db | api",
  "config": {
    "model_name": "string",
    "api_key": "string",
    "url": "string",
    "connection_string": "string"
  }
}
```

### **Fields**

| Field    | Type   | Required | Description                                |
| -------- | ------ | -------- | ------------------------------------------ |
| `id`     | string | yes      | Unique identifier for referencing in nodes |
| `kind`   | enum   | yes      | Type of external system                    |
| `config` | object | yes      | Connection/configuration details           |

### **Source Types**

| Kind    | Example                | Used By            |
| ------- | ---------------------- | ------------------ |
| `llm`   | GPT-4.1, Claude 3      | LLM Nodes          |
| `image` | DALL·E, Midjourney API | Image Nodes        |
| `db`    | PostgreSQL connection  | DB Nodes           |
| `api`   | REST endpoint          | API Nodes (future) |

---

# -----------------------------------------------------------

# **6. Execution State Schema**

# -----------------------------------------------------------

This is the **state object passed between nodes** during execution.

### **Structure:**

```json
{
  "user_input": "string",
  "intent": "text | image | db",
  "text_result": "string",
  "image_result": "binary/base64",
  "db_result": {},
  "final_output": {},
  "metadata": {},
  "tokens_used": 0,
  "cost": 0
}
```

### **Fields**

| Field          | Type   | Description                  |
| -------------- | ------ | ---------------------------- |
| `user_input`   | string | Raw input                    |
| `intent`       | string | Determined by router         |
| `text_result`  | string | Output from LLM nodes        |
| `image_result` | base64 | Output from image nodes      |
| `db_result`    | object | SQL query results            |
| `final_output` | object | Combined output in last node |
| `metadata`     | object | Execution-related info       |
| `tokens_used`  | number | Token usage (optional)       |
| `cost`         | number | Billing estimation           |

---

# -----------------------------------------------------------

# **7. Example Complete Workflow (Valid)**

# -----------------------------------------------------------

```json
{
  "start_node": "input",

  "nodes": [
    { "id": "input", "type": "input" },
    { "id": "router", "type": "router" },
    { "id": "llm-text", "type": "llm", "metadata": { "source": "openai" } },
    { "id": "image-gen", "type": "image", "metadata": { "source": "openai" } },
    { "id": "final", "type": "aggregator" }
  ],

  "edges": [
    { "from": "input", "to": "router" },
    { "from": "router", "to": ["llm-text", "image-gen"] },
    { "from": "llm-text", "to": "final" },
    { "from": "image-gen", "to": "final" }
  ],

  "queues": [
    {
      "id": "q1",
      "from": "router",
      "to": "llm-text",
      "bandwidth": { "max_messages_per_second": 1 }
    }
  ],

  "sources": [
    {
      "id": "openai",
      "kind": "llm",
      "config": {
        "model_name": "gpt-4.1",
        "api_key": "sk-xxxxx"
      }
    }
  ]
}
```

---

# -----------------------------------------------------------

# **8. Example Invalid Workflow**

# -----------------------------------------------------------

```json
{
  "nodes": [
    { "id": "wrongType", "type": "xyz" }
  ]
}
```

Errors:

* Invalid node type
* Missing start_node
* Missing edges
* Missing sources

---

# -----------------------------------------------------------

# **9. Rules Enforced by Backend**

# -----------------------------------------------------------

### Node rules:

✔ Unique IDs
✔ Valid types
✔ Required metadata for special nodes

### Edge rules:

✔ Node references must exist
✔ No self-loop edges unless intentional

### Queue rules:

✔ Unique queue IDs
✔ Queue endpoints must exist
✔ Bandwidth numbers ≥ 0

### Source rules:

✔ LLM nodes MUST reference valid LLM source
✔ DB nodes MUST include connection string

### Workflow rules:

✔ Must have 1 input node (optional rule)
✔ Must have 1 aggregator node (recommended)
✔ Router must have ≥ 1 outgoing edge

---

# -----------------------------------------------------------

# 🎉 `Schema.md` is complete.

# -----------------------------------------------------------

If you want, I can also generate:

### 🔥 Ready-to-download files:

* `workflow.schema.json`
* `node.schema.json`
* `queue.schema.json`

### 🔥 Auto-validator code in:

* Python (Pydantic)
* TypeScript (Zod)
* JSON Schema validation

### 🔥 Visual diagram of schema relationships

### 🔥 Shell script that generates schema files

Just tell me.
