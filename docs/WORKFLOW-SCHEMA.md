# 📄 **WORKFLOW-SCHEMA.md — AgentFlow Workflow Specification Schema**

**Version:** 1.0
**Standard:** JSON Schema Draft 2020–12
**Used By:** Backend, Frontend, API, LLD, Nodes Engine

---

# ---------------------------------------------------------

# **1. Overview**

# ---------------------------------------------------------

Every workflow in AgentFlow is defined using a strict JSON structure containing:

* **nodes**
* **edges**
* **queues**
* **sources**
* **start_node**

This document defines that schema formally.

---

# ---------------------------------------------------------

# **2. Full JSON Schema (Draft 2020–12)**

# ---------------------------------------------------------

You can save this as:

```
workflow.schema.json
```

---

## 🧩 **2.1 Root Schema**

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "https://agentflow.ai/workflow.schema.json",
  "title": "AgentFlow Workflow Specification",
  "type": "object",

  "required": ["nodes", "edges", "queues", "sources", "start_node"],

  "properties": {
    "nodes": {
      "type": "array",
      "items": { "$ref": "#/$defs/node" },
      "minItems": 1
    },

    "edges": {
      "type": "array",
      "items": { "$ref": "#/$defs/edge" }
    },

    "queues": {
      "type": "array",
      "items": { "$ref": "#/$defs/queue" }
    },

    "sources": {
      "type": "array",
      "items": { "$ref": "#/$defs/source" }
    },

    "start_node": {
      "type": "string"
    }
  },

  "$defs": {}
}
```

---

# ---------------------------------------------------------

# **3. Node Schema**

# ---------------------------------------------------------

A node represents one step in the workflow graph.

---

## 🟦 **3.1 Node Definition**

```json
{
  "$id": "#/$defs/node",
  "type": "object",

  "required": ["id", "type"],

  "properties": {
    "id": {
      "type": "string",
      "pattern": "^[A-Za-z0-9._-]+$"
    },

    "type": {
      "type": "string",
      "enum": [
        "input",
        "router",
        "llm",
        "image",
        "db",
        "aggregator"
      ]
    },

    "metadata": {
      "type": "object",
      "properties": {
        "source": { "type": "string" },
        "config": { "type": "object" }
      },
      "additionalProperties": true
    }
  }
}
```

---

# ---------------------------------------------------------

# **4. Edge Schema**

# ---------------------------------------------------------

Edges define directional routing between nodes.

---

## 🟧 **4.1 Edge Definition**

```json
{
  "$id": "#/$defs/edge",
  "type": "object",

  "required": ["from", "to"],

  "properties": {
    "from": { "type": "string" },

    "to": {
      "anyOf": [
        { "type": "string" },
        {
          "type": "array",
          "items": { "type": "string" }
        }
      ]
    }
  }
}
```

---

# ---------------------------------------------------------

# **5. Queue Schema**

# ---------------------------------------------------------

Queues define capacity/bandwidth between nodes.

---

## 🟩 **5.1 Queue Definition**

```json
{
  "$id": "#/$defs/queue",
  "type": "object",

  "required": ["id", "from", "to"],

  "properties": {
    "id": {
      "type": "string",
      "pattern": "^[A-Za-z0-9._-]+$"
    },

    "from": { "type": "string" },
    "to": { "type": "string" },

    "bandwidth": {
      "type": "object",
      "properties": {
        "max_messages_per_second": { "type": "number", "minimum": 0 },
        "max_requests_per_minute": { "type": "number", "minimum": 0 },
        "tokens_per_minute": { "type": "number", "minimum": 0 }
      },
      "additionalProperties": false
    },

    "subqueues": {
      "type": "array",
      "items": {
        "type": "object",
        "required": ["id", "weight"],
        "properties": {
          "id": { "type": "string" },
          "weight": {
            "type": "number",
            "minimum": 0,
            "maximum": 1
          }
        }
      }
    }
  }
}
```

---

# ---------------------------------------------------------

# **6. Source Schema**

# ---------------------------------------------------------

A source defines external systems an agent node can call.

---

## 🟪 **6.1 Source Definition**

```json
{
  "$id": "#/$defs/source",
  "type": "object",

  "required": ["id", "kind", "config"],

  "properties": {
    "id": {
      "type": "string",
      "pattern": "^[A-Za-z0-9._-]+$"
    },

    "kind": {
      "type": "string",
      "enum": ["llm", "image", "db", "api"]
    },

    "config": {
      "type": "object",
      "properties": {
        "model_name": { "type": "string" },
        "api_key": { "type": "string" },
        "url": { "type": "string", "format": "uri" },
        "connection_string": { "type": "string" }
      },
      "additionalProperties": true
    }
  }
}
```

---

# ---------------------------------------------------------

# **7. Example Valid Workflow JSON**

# ---------------------------------------------------------

```json
{
  "start_node": "input",

  "nodes": [
    { "id": "input", "type": "input" },
    { "id": "router", "type": "router" },
    {
      "id": "llm-text",
      "type": "llm",
      "metadata": { "source": "openai" }
    },
    {
      "id": "image-gen",
      "type": "image",
      "metadata": { "source": "openai-img" }
    },
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
        "api_key": "sk-xxx"
      }
    }
  ]
}
```

---

# ---------------------------------------------------------

# **8. Example Invalid Workflow JSON**

# ---------------------------------------------------------

### ❌ Missing required node fields

```json
{
  "nodes": [
    { "type": "llm" }
  ]
}
```

### ❌ Invalid node type

```json
{
  "nodes": [
    { "id": "test", "type": "wrongtype" }
  ]
}
```

### ❌ Queue bandwidth invalid

```json
{
  "queues": [
    {
      "id": "q1",
      "from": "a",
      "to": "b",
      "bandwidth": { "max_messages_per_second": -1 }
    }
  ]
}
```

---

# ---------------------------------------------------------

# **9. Backend Enforcement Rules**

# ---------------------------------------------------------

Backend must validate:

✔ All node IDs must be unique
✔ Edges must reference valid node IDs
✔ Sources used by nodes must exist
✔ Start node must exist
✔ No queue should map invalid `from` → `to`
✔ Node type-specific validation:

* `llm` must have a `source`
* `db` must have `connection_string`

---

# ---------------------------------------------------------

# **10. Frontend Enforcement Rules**

# ---------------------------------------------------------

Frontend Studio must ensure:

✔ No invalid node can be created
✔ Remove edges if nodes are deleted
✔ Validation errors appear in red
✔ JSON Preview updates live
✔ Cannot execute until schema is valid

---

# ---------------------------------------------------------

# 🎉 `WORKFLOW-SCHEMA.md` IS READY

# ---------------------------------------------------------

If you want next:

### 🔥 AUTO-GENERATED VALIDATOR CODE (Python + TS)

### 🔥 READY-TO-USE JSON schema file

### 🔥 Runtime schema-checker integration

### 🔥 Figma-style UI layout diagrams

### 🔥 PDF export of all spec docs (HLD, LLD, API, Backend, Frontend, Schema)

Just tell me **what you want.**
