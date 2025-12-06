**FRONTEND-SPEC.md specifically for Next.js 16**

### ✔ React 19 support

### ✔ Turbopack Stable

### ✔ Server Components stronger defaults

### ✔ Revised API Route handling

### ✔ Enhanced `server-actions`

### ✔ Edge-first execution

### ✔ Optimized bundling for large apps

Below is the **updated and accurate NEXT 16 version of FRONTEND-SPEC.md**.

---

# 📄 **FRONTEND-SPEC.md — AgentFlow Studio (Next.js 16 Edition)**

**Version:** 2.0
**Tech Stack:**

* **Next.js 16 (App Router)**
* **React 19**
* **Turbopack**
* **React Flow v12**
* **TypeScript**
* **ShadCN UI**
* **TailwindCSS**

---

# ---------------------------------------------------------

# **1. Architectural Overview (Next.js 16 Specific)**

# ---------------------------------------------------------

### Next.js 16 introduces:

✔ Default **React Server Components (RSC)**
✔ Stable **Turbopack** for dev + prod
✔ New `server-actions` for mutating server data
✔ Full-edge compatibility
✔ Enhanced caching model

### Our implementation must support:

* All UI = **Client Components** (React Flow requires it)
* API calls via **serverless/edge routes** under `/app/api/*`
* Workflows saved using **server actions**
* Designer runs fully client-side
* JSON Preview & Tests run client-side

---

# ---------------------------------------------------------

# **2. Project Folder Structure**

# ---------------------------------------------------------

Updated for **Next 16** best practices:

```
frontend/
│
├── app/
│   ├── designer/
│   │   ├── page.tsx                    (Client Component)
│   │   ├── canvas/
│   │   │   ├── WorkflowCanvas.tsx
│   │   │   └── CanvasNode.tsx
│   │   ├── panels/
│   │   │   ├── NodePalette.tsx
│   │   │   ├── PropertiesPanel.tsx
│   │   │   ├── SourceManager.tsx
│   │   │   ├── QueueManager.tsx
│   │   │   └── JsonPreview.tsx
│   │   ├── test-run/
│   │   │   └── TestRunPanel.tsx
│   │   └── hooks/
│   │       └── useWorkflowStore.ts      (Zustand)
│   │
│   ├── api/
│   │   ├── workflows/route.ts
│   │   ├── sources/route.ts
│   │   └── queues/route.ts
│   │
│   └── layout.tsx
│
├── lib/
│   ├── api.ts
│   ├── validators.ts
│   └── utils.ts
│
├── components/ui/      (ShadCN)
├── public/icons/
└── styles/globals.css
```

---

# ---------------------------------------------------------

# **3. Component Specifications (Next.js 16)**

# ---------------------------------------------------------

All canvas-related components must be marked as:

```tsx
"use client";
```

because React Flow + Zustand work ONLY in Client Components.

Panels and managers follow the same rule.

---

# ---------------------------------------------------------

# **4. State Management**

# ---------------------------------------------------------

We use **Zustand** because:

* Lightweight
* No Redux boilerplate
* Fully compatible with Client Components
* Perfect for real-time panels + canvas sync

### Store File: `useWorkflowStore.ts`

```ts
"use client";

import { create } from "zustand";

export const useWorkflowStore = create<WorkflowState>((set, get) => ({
  nodes: [],
  edges: [],
  queues: [],
  sources: [],
  startNode: "input",

  setNodes: (nodes) => set({ nodes }),
  setEdges: (edges) => set({ edges }),
  setQueues: (queues) => set({ queues }),
  setSources: (sources) => set({ sources }),
  setStartNode: (id) => set({ startNode: id }),

  generateSpec: () => ({
    nodes: get().nodes,
    edges: get().edges,
    queues: get().queues,
    sources: get().sources,
    start_node: get().startNode,
  }),
}));
```

---

# ---------------------------------------------------------

# **5. API Integration (Next.js 16)**

# ---------------------------------------------------------

### Backend API calls MUST NOT use `fetch('/api/...')` directly in `/app/api`.

Instead:

✔ UI should call internal functions
✔ `/lib/api.ts` should manage all backend URLs
✔ Execution should NOT use server actions

---

## **5.1 /lib/api.ts**

```ts
export const api = {
  validateWorkflow: async (spec) =>
    fetch(process.env.NEXT_PUBLIC_CORE_URL + "/workflows/validate", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ workflow: spec }),
    }).then((r) => r.json()),

  executeWorkflow: async (spec, initial) =>
    fetch(process.env.NEXT_PUBLIC_CORE_URL + "/workflows/execute", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ workflow: spec, initial_state: initial }),
    }).then((r) => r.json()),

  // sources + queues also defined here…
};
```

---

# ---------------------------------------------------------

# **6. Server Actions (Next 16 Feature)**

# ---------------------------------------------------------

Server Actions are used ONLY for saving workflows locally (not runtime execution).

Example:

`app/designer/actions.ts`

```ts
"use server";

import { saveWorkflowToDb } from "@/lib/db";

export async function saveWorkflowAction(spec) {
  return await saveWorkflowToDb(spec);
}
```

Called from UI:

```tsx
await saveWorkflowAction(spec);
```

---

# ---------------------------------------------------------

# **7. Designer Page Requirements**

# ---------------------------------------------------------

`app/designer/page.tsx`

* Client Component
* Contains:

  * Canvas (left)
  * JSON Preview (right)
  * Properties panel (right drawer)
  * Node palette (left drawer)

### Layout (expected)

```
 -----------------------------------------------------
| Palette |          CANVAS AREA          | Properties |
 -----------------------------------------------------
| JSON Preview (collapsible)                           |
 -----------------------------------------------------
| Test Run Panel (bottom collapsible)                 |
 -----------------------------------------------------
```

---

# ---------------------------------------------------------

# **8. Workflow Canvas (React Flow)**

# ---------------------------------------------------------

**React Flow v12** must be used.

Supported features:

* drag/drop nodes
* connect nodes using handles
* selection
* zoom / pan
* custom node rendering

We create custom node types:

```ts
const nodeTypes = {
  inputNode: InputNode,
  routerNode: RouterNode,
  llmNode: LLMNode,
  imageNode: ImageNode,
  dbNode: DBNode,
  aggregatorNode: AggregatorNode,
};
```

Render:

```tsx
<ReactFlow
  nodes={nodes}
  edges={edges}
  onNodesChange={onNodesChange}
  onEdgesChange={onEdgesChange}
  onConnect={handleConnect}
  nodeTypes={nodeTypes}
  fitView
/>
```

---

# ---------------------------------------------------------

# **9. JSON Preview Panel**

# ---------------------------------------------------------

Fast, accurate JSON preview via:

```tsx
<pre className="bg-zinc-900 text-zinc-200 text-sm p-4 overflow-auto">
  {JSON.stringify(spec, null, 2)}
</pre>
```

---

# ---------------------------------------------------------

# **10. Test Run Panel**

# ---------------------------------------------------------

Workflow execution triggered via backend API:

```ts
const result = await api.executeWorkflow(
  generateSpec(),
  { user_input }
);
```

Displays:

* execution trace
* final state
* errors

---

# ---------------------------------------------------------

# **11. Source Manager**

# ---------------------------------------------------------

Fields show dynamically based on:

```
LLM → model_name, api_key  
DB → conn_string  
Image → model, api_key  
API → base_url, headers, auth  
```

All use ShadCN form components.

---

# ---------------------------------------------------------

# **12. Queue Manager**

# ---------------------------------------------------------

Editable:

```
max_messages_per_second
max_requests_per_minute
tokens_per_minute
subqueues (id + weight)
```

Validation must match backend.

---

# ---------------------------------------------------------

# **13. UI/UX Requirements**

# ---------------------------------------------------------

### Canvas:

* Figma-like smooth dragging
* Snap-to-grid (optional)
* Node hover toolbar (delete/duplicate)
* Error nodes glow red

### Properties Panel:

* Opens on selecting node
* Auto-updates store on change

### JSON Preview:

* Live
* Collapsible
* Syntax highlighting

### Test Run:

* Bottom drawer
* Shows raw state + formatted details

---

# ---------------------------------------------------------

# **14. Error Handling**

# ---------------------------------------------------------

UI notifies using ShadCN toast:

* Validation errors
* Backend failures
* Unconnected nodes
* Missing fields

Nodes with issues → red border.

---

# ---------------------------------------------------------

# **15. Environment Variables (Next 16)**

```
NEXT_PUBLIC_CORE_URL=https://agentflow-core.yourdomain.com
NEXT_PUBLIC_ENV=development
```

These must be accessible on client.

---

# ---------------------------------------------------------

# **16. Performance Requirements**

# ---------------------------------------------------------

* React Flow diagram MUST NOT re-render whole app
* Zustand slices should minimize updates
* Turbopack used for hot reload

---

# ---------------------------------------------------------

# **17. Future Additions**

# ---------------------------------------------------------

* Real-time multiplayer (WebRTC + CRDT)
* AI-powered diagram generator
* Execution heatmaps
* Node template library
* Versioned workflows

---

# ---------------------------------------------------------

# 🎉 FRONTEND-SPEC.md (Next.js 16 Edition) is COMPLETE

# ---------------------------------------------------------

Would you like me to generate:

### 🔥 WORKFLOW-SCHEMA.md (Complete JSON Schema for validation)

### 🔥 UI WIREFRAMES (Figma-style ASCII + descriptions)

### 🔥 FULL FILE SCAFFOLDING (All empty files + folder tree)

### 🔥 Shell script to generate frontend project structure

Just tell me **which one you want next**.
