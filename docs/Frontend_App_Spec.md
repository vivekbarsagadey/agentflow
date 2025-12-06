
---

## 2. `Frontend_App_Spec.md` – AgentFlow Studio (Next.js) Spec

```md
# AgentFlow Studio – Frontend Application Specification

Version: 0.1  
Tech: Next.js (App Router), React, TypeScript

---

## 1. Purpose

**AgentFlow Studio** is the visual designer frontend for AgentFlow.  
It allows users to:

- Visually design workflows as graphs (nodes + edges)
- Configure queues (bandwidth, sub-queues)
- Configure sources (LLM, image, DB, APIs)
- Preview and export valid **WorkflowSpec JSON**
- Call AgentFlow Core APIs to validate and test workflows

---

## 2. Technology Stack

- **Framework**: Next.js (App Router, latest LTS)
- **Language**: TypeScript
- **UI Library**: React (with optional Tailwind/shadcn if desired)
- **State Management**: React hooks + local component state (initial version)
- **Canvas Engine**: React Flow or similar (for drag–drop node graph)
- **HTTP Client**: native `fetch` (Next.js route handlers)

---

## 3. Routing Structure

All routes are under `frontend/agentflow-studio/app/`.

### 3.1 `/` – Dashboard

- **File**: `app/page.tsx`
- Purpose:
  - Welcome screen
  - List of existing workflows (fetched from backend `/workflows`)
  - Quick actions: "New Workflow", "Open Designer", "Manage Sources"

### 3.2 `/designer` – Workflow Designer

- **File**: `app/designer/page.tsx`
- Purpose:
  - Main canvas view for creating/editing workflows
- Core UI Regions:
  - Left panel: Node palette, queues & sources quick access
  - Center: Canvas (graph view)
  - Right panel: Properties + JSON preview
  - Top bar: Workflow name, Save, Validate, Test Run

### 3.3 `/sources` – Source Manager

- **File**: `app/sources/page.tsx`
- Purpose:
  - CRUD UI for sources (`/sources` backend endpoints)
  - Display table of sources with:
    - `id`, `kind`, `provider/model/driver`, `env variables`
  - Forms to create/edit a source

### 3.4 `/settings` – Application Settings

- **File**: `app/settings/page.tsx`
- Purpose:
  - Configure global frontend-level settings:
    - Backend base URL (`AGENTFLOW_CORE_URL`)
    - Theme options (light/dark)
    - Default node types visible, etc.

### 3.5 `/api/*` – Frontend Proxy Routes

- `app/api/workflows/route.ts`
  - Proxies Studio requests to AgentFlow Core for:
    - Validate workflow
    - Save workflow
    - List workflows
- `app/api/execute/route.ts`
  - Proxies test execution requests to AgentFlow Core.

> These routes hide the Core URL from the browser and allow CORS-free calls.

---

## 4. State Model (Frontend)

The core in-memory state of a workflow is represented by `WorkflowSpec` and related types in `lib/types.ts`.

### 4.1 Types

```ts
export type UnitType = "request" | "tokens" | "image" | "query" | string;

export interface WorkflowNode {
  id: string;
  type: "input" | "router" | "llm" | "image" | "db" | "aggregator" | string;
  description?: string;
  source?: string;
  unit?: UnitType;
  max_tokens?: number;
  x?: number;
  y?: number;
}

export interface QueueBandwidth {
  max_messages_per_second?: number;
  max_requests_per_minute?: number;
  max_tokens_per_minute?: number;
  max_queries_per_second?: number;
  burst_size?: number;
}

export interface SubQueueConfig {
  id: string;
  weight: number;
}

export interface WorkflowQueue {
  id: string;
  from: string | string[];
  to: string;
  bandwidth?: QueueBandwidth;
  sub_queues?: SubQueueConfig[];
}

export interface WorkflowEdge {
  from: string;
  to: string | string[];
  queue?: string;
  condition?: string;
}

export interface WorkflowSource {
  id: string;
  kind: "llm" | "image" | "db" | "api" | "iot" | string;
  provider?: string;
  model?: string;
  api_key_env?: string;
  driver?: string;
  dsn_env?: string;
  base_url?: string;
}

export interface WorkflowSpec {
  nodes: WorkflowNode[];
  queues: WorkflowQueue[];
  edges: WorkflowEdge[];
  sources: WorkflowSource[];
  start_node: string;
}
