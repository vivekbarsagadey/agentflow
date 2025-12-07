---
goal: AgentFlow Studio Phase 1 - MVP Implementation Plan
version: 1.0
date_created: 2025-12-07
last_updated: 2025-12-07
owner: Frontend Team
status: 'Planned'
tags: ['feature', 'frontend', 'mvp', 'phase-1']
---

# AgentFlow Studio - Phase 1: MVP Implementation Plan

![Status: Planned](https://img.shields.io/badge/status-Planned-blue)

**Duration:** 8 Weeks  
**Goal:** Build a functional workflow designer with core canvas, node management, properties panel, validation, and backend integration.

---

## 1. Requirements & Constraints

### Core Requirements

- **REQ-001**: Must use Next.js 16 with App Router architecture
- **REQ-002**: Must integrate React Flow v12 for workflow canvas
- **REQ-003**: Must use TypeScript 5+ with strict mode enabled
- **REQ-004**: Must use Zustand for global state management
- **REQ-005**: Must support all 6 node types (Input, Router, LLM, Image, DB, Aggregator)
- **REQ-006**: Must validate workflows via backend API before execution
- **REQ-007**: Must persist workflows to backend database
- **REQ-008**: Must generate valid WorkflowSpec JSON from visual canvas
- **REQ-009**: Must support drag-and-drop node placement
- **REQ-010**: Must provide real-time JSON preview of workflow

### Technical Constraints

- **CON-001**: Desktop-first design (minimum 1280px width)
- **CON-002**: Must work with AgentFlow Core backend API
- **CON-003**: API responses must be type-safe (TypeScript interfaces)
- **CON-004**: Canvas must handle up to 50 nodes without performance degradation
- **CON-005**: Auto-save must debounce to prevent excessive API calls
- **CON-006**: Must follow ShadCN UI component patterns

### Security Requirements

- **SEC-001**: API keys must never be stored in frontend code
- **SEC-002**: All backend API calls must be authenticated
- **SEC-003**: Source configurations must reference environment variables, not store credentials

### Design Guidelines

- **GUD-001**: Follow Material Design or modern UI principles
- **GUD-002**: Use consistent spacing (8px grid system)
- **GUD-003**: Provide clear visual feedback for all user actions
- **GUD-004**: Error messages must be actionable and user-friendly
- **GUD-005**: Loading states must be visible for operations > 300ms

### Best Practices (from Research)

- **PAT-001**: React Flow - Use `useNodesState` and `useEdgesState` for managed state
- **PAT-002**: React Flow - Implement `onNodesChange` and `onEdgesChange` for reactivity
- **PAT-003**: React Flow - Use custom node types for specialized rendering
- **PAT-004**: Zustand - Keep store actions pure and synchronous
- **PAT-005**: Zustand - Use selectors to prevent unnecessary re-renders
- **PAT-006**: Next.js - Use Server Components for data fetching where possible
- **PAT-007**: Next.js - Use Route Handlers for API proxy endpoints
- **PAT-008**: TypeScript - Define interfaces for all data structures
- **PAT-009**: Performance - Memoize expensive calculations with useMemo
- **PAT-010**: Performance - Debounce real-time updates (300ms minimum)

---

## 2. Implementation Steps

### Phase 1.1: Project Setup & Core Infrastructure (Week 1-2)

**GOAL-001:** Establish development environment with all dependencies, project structure, and core infrastructure components.

| Task | Description | Completed | Date |
|------|-------------|-----------|------|
| TASK-001 | Initialize Next.js 16 project with TypeScript using `create-next-app` | | |
| TASK-002 | Configure TypeScript `tsconfig.json` with strict mode and path aliases (`@/*`) | | |
| TASK-003 | Install core dependencies: `@xyflow/react`, `zustand`, `lucide-react` | | |
| TASK-004 | Install and configure ShadCN UI with `npx shadcn-ui@latest init` | | |
| TASK-005 | Configure TailwindCSS 4 with custom theme colors and dark mode | | |
| TASK-006 | Setup project structure: `lib/`, `components/`, `app/` directories | | |
| TASK-007 | Create base TypeScript interfaces in `lib/types.ts` (WorkflowNode, WorkflowEdge, etc.) | | |
| TASK-008 | Create API client skeleton in `lib/api.ts` with fetch wrapper and error handling | | |
| TASK-009 | Setup ESLint and Prettier with Next.js recommended config | | |
| TASK-010 | Create root layout with header, main content area, and theme provider | | |
| TASK-011 | Implement dark mode toggle using `next-themes` package | | |
| TASK-012 | Create basic navigation component with logo and menu items | | |
| TASK-013 | Setup environment variables structure (`.env.local` template) | | |
| TASK-014 | Configure Next.js API proxy routes in `app/api/` directory | | |
| TASK-015 | Initialize Git repository with `.gitignore` for Next.js | | |
| TASK-016 | Create README with setup instructions and architecture overview | | |

**Acceptance Criteria:**
- ✅ `npm run dev` starts development server without errors
- ✅ TypeScript compiles without errors in strict mode
- ✅ TailwindCSS styles apply correctly
- ✅ Dark mode toggle switches theme successfully
- ✅ Project structure matches planned architecture
- ✅ All team members can clone and run locally

**Research Notes:**
- React Flow requires parent container with explicit width/height
- Zustand 4.x has improved TypeScript support with `create<T>()`
- Next.js 16 requires React 19 RC, ensure compatibility

---

### Phase 1.2: Zustand Store & State Management (Week 1-2)

**GOAL-002:** Implement centralized state management with Zustand for workflow data, selections, and UI state.

| Task | Description | Completed | Date |
|------|-------------|-----------|------|
| TASK-017 | Create `lib/stores/useWorkflowStore.ts` with Zustand store factory | | |
| TASK-018 | Define TypeScript interfaces for store state (nodes, edges, queues, sources) | | |
| TASK-019 | Implement `nodes` state with add/remove/update actions | | |
| TASK-020 | Implement `edges` state with add/remove/update actions | | |
| TASK-021 | Implement `sources` state with CRUD actions | | |
| TASK-022 | Implement `queues` state with CRUD actions | | |
| TASK-023 | Add `startNode` state with setter action | | |
| TASK-024 | Add `workflowMetadata` state (id, name, description) | | |
| TASK-025 | Implement `generateSpec()` action to convert store → WorkflowSpec JSON | | |
| TASK-026 | Implement `loadSpec()` action to populate store from WorkflowSpec JSON | | |
| TASK-027 | Implement `clear()` action to reset all state | | |
| TASK-028 | Add `unsavedChanges` flag with automatic tracking | | |
| TASK-029 | Implement Zustand persist middleware for localStorage auto-save | | |
| TASK-030 | Add store selectors for optimized component subscriptions | | |
| TASK-031 | Create store devtools integration for debugging | | |
| TASK-032 | Write unit tests for store actions and state transitions | | |

**Acceptance Criteria:**
- ✅ Store maintains workflow state without prop drilling
- ✅ Actions update state immutably
- ✅ `generateSpec()` produces valid WorkflowSpec JSON
- ✅ `loadSpec()` correctly populates store from JSON
- ✅ Persist middleware saves/restores from localStorage
- ✅ All store actions have 100% unit test coverage

**Code Example:**
```typescript
// lib/stores/useWorkflowStore.ts
import { create } from 'zustand';
import { persist } from 'zustand/middleware';

interface WorkflowNode {
  id: string;
  type: 'input' | 'router' | 'llm' | 'image' | 'db' | 'aggregator';
  position: { x: number; y: number };
  data: Record<string, any>;
}

interface WorkflowState {
  nodes: WorkflowNode[];
  edges: WorkflowEdge[];
  sources: WorkflowSource[];
  queues: WorkflowQueue[];
  startNode: string;
  unsavedChanges: boolean;
  
  addNode: (node: WorkflowNode) => void;
  removeNode: (id: string) => void;
  updateNode: (id: string, updates: Partial<WorkflowNode>) => void;
  generateSpec: () => WorkflowSpec;
  loadSpec: (spec: WorkflowSpec) => void;
  clear: () => void;
}

export const useWorkflowStore = create<WorkflowState>()(
  persist(
    (set, get) => ({
      nodes: [],
      edges: [],
      sources: [],
      queues: [],
      startNode: 'input',
      unsavedChanges: false,
      
      addNode: (node) => set((state) => ({
        nodes: [...state.nodes, node],
        unsavedChanges: true
      })),
      
      removeNode: (id) => set((state) => ({
        nodes: state.nodes.filter(n => n.id !== id),
        edges: state.edges.filter(e => e.source !== id && e.target !== id),
        unsavedChanges: true
      })),
      
      // ... other actions
    }),
    { name: 'agentflow-workflow' }
  )
);
```

---

### Phase 1.3: Workflow Canvas Component (Week 3-4)

**GOAL-003:** Build interactive canvas using React Flow with node placement, movement, and edge connections.

| Task | Description | Completed | Date |
|------|-------------|-----------|------|
| TASK-033 | Create `components/WorkflowCanvas.tsx` base component | | |
| TASK-034 | Import and configure React Flow with required CSS | | |
| TASK-035 | Connect canvas to Zustand store (nodes, edges) | | |
| TASK-036 | Implement `useNodesState` and `useEdgesState` hooks from React Flow | | |
| TASK-037 | Create `onNodesChange` handler with store synchronization | | |
| TASK-038 | Create `onEdgesChange` handler with store synchronization | | |
| TASK-039 | Implement `onConnect` handler for edge creation | | |
| TASK-040 | Add canvas controls (zoom in/out, fit view, reset) | | |
| TASK-041 | Configure background grid with snap-to-grid option | | |
| TASK-042 | Implement node selection (single and multi-select) | | |
| TASK-043 | Add delete handler for selected nodes (Delete key) | | |
| TASK-044 | Implement pan and zoom with mouse/trackpad | | |
| TASK-045 | Add canvas context menu (right-click) | | |
| TASK-046 | Create custom connection line styling | | |
| TASK-047 | Implement edge validation (prevent invalid connections) | | |
| TASK-048 | Add visual feedback for hover states | | |

**Acceptance Criteria:**
- ✅ Canvas renders without errors in full viewport
- ✅ Nodes can be moved by dragging
- ✅ Edges can be created by connecting node handles
- ✅ Zoom/pan works smoothly
- ✅ Selection persists across re-renders
- ✅ Delete key removes selected nodes/edges
- ✅ Canvas state syncs with Zustand store

**Research Notes:**
- Use `<ReactFlow />` component with controlled nodes/edges
- Apply changes using `applyNodeChanges` and `applyEdgeChanges`
- Set `fitView` prop for initial viewport fit
- Use `<Background />` and `<Controls />` built-in components

---

### Phase 1.4: Custom Node Components (Week 3-4)

**GOAL-004:** Create custom node components for each workflow node type with proper styling and handles.

| Task | Description | Completed | Date |
|------|-------------|-----------|------|
| TASK-049 | Create `components/nodes/BaseNode.tsx` with common node structure | | |
| TASK-050 | Create `components/nodes/InputNode.tsx` with single output handle | | |
| TASK-051 | Create `components/nodes/RouterNode.tsx` with multiple output handles | | |
| TASK-052 | Create `components/nodes/LLMNode.tsx` with input/output handles | | |
| TASK-053 | Create `components/nodes/ImageNode.tsx` with input/output handles | | |
| TASK-054 | Create `components/nodes/DBNode.tsx` with input/output handles | | |
| TASK-055 | Create `components/nodes/AggregatorNode.tsx` with multiple input handles | | |
| TASK-056 | Define node type colors and icons using Lucide React | | |
| TASK-057 | Implement node hover state styling | | |
| TASK-058 | Implement node selected state styling | | |
| TASK-059 | Add node labels with truncation for long text | | |
| TASK-060 | Configure handle positions (top, bottom, left, right) | | |
| TASK-061 | Register custom nodes in React Flow `nodeTypes` prop | | |
| TASK-062 | Add node status indicators (valid, error, warning) | | |
| TASK-063 | Implement node double-click to open properties | | |
| TASK-064 | Create node component tests for each type | | |

**Acceptance Criteria:**
- ✅ All 6 node types render with distinct appearance
- ✅ Node handles are positioned correctly
- ✅ Nodes show appropriate icons and colors
- ✅ Selected nodes have visible border/shadow
- ✅ Double-clicking node opens properties panel
- ✅ Node components are responsive to data changes

**Code Example:**
```typescript
// components/nodes/LLMNode.tsx
import { memo } from 'react';
import { Handle, Position, NodeProps } from '@xyflow/react';
import { MessageSquare } from 'lucide-react';

export const LLMNode = memo(({ data, selected }: NodeProps) => {
  return (
    <div className={`px-4 py-2 shadow-md rounded-md bg-white border-2 ${
      selected ? 'border-blue-500' : 'border-gray-300'
    }`}>
      <Handle type="target" position={Position.Top} />
      
      <div className="flex items-center gap-2">
        <MessageSquare className="w-4 h-4 text-blue-600" />
        <div>
          <div className="text-sm font-bold">{data.label || 'LLM'}</div>
          <div className="text-xs text-gray-500">{data.source || 'No source'}</div>
        </div>
      </div>
      
      <Handle type="source" position={Position.Bottom} />
    </div>
  );
});

LLMNode.displayName = 'LLMNode';
```

---

### Phase 1.5: Node Palette Component (Week 3-4)

**GOAL-005:** Create draggable node palette for adding nodes to canvas.

| Task | Description | Completed | Date |
|------|-------------|-----------|------|
| TASK-065 | Create `components/NodePalette.tsx` sidebar component | | |
| TASK-066 | Define node type metadata (icon, label, category) | | |
| TASK-067 | Implement node list rendering with categories | | |
| TASK-068 | Add drag-and-drop functionality using React Flow | | |
| TASK-069 | Implement click-to-add alternative (single-click node, click canvas) | | |
| TASK-070 | Generate unique node IDs on creation (`node_xxx`) | | |
| TASK-071 | Set default node positions (canvas center or cursor position) | | |
| TASK-072 | Add search/filter input for node types | | |
| TASK-073 | Implement collapsible categories (Input, Processing, Output) | | |
| TASK-074 | Add node descriptions on hover (tooltips) | | |
| TASK-075 | Style palette with consistent spacing and colors | | |
| TASK-076 | Make palette responsive (collapsible on smaller screens) | | |

**Acceptance Criteria:**
- ✅ Palette displays all 6 node types
- ✅ Drag-and-drop adds node to canvas at drop position
- ✅ Click-to-add workflow is intuitive
- ✅ Search filters node list in real-time
- ✅ Categories can be collapsed/expanded
- ✅ Palette integrates seamlessly with canvas layout

---

### Phase 1.6: Properties Panel Component (Week 5-6)

**GOAL-006:** Build dynamic properties panel that displays and edits node/edge configuration.

| Task | Description | Completed | Date |
|------|-------------|-----------|------|
| TASK-077 | Create `components/PropertiesPanel.tsx` sidebar component | | |
| TASK-078 | Implement node selection detection from canvas | | |
| TASK-079 | Create dynamic form renderer based on node type | | |
| TASK-080 | Build Input node property form (id, description) | | |
| TASK-081 | Build Router node property form (id, routes, default) | | |
| TASK-082 | Build LLM node property form (id, source, prompt, params) | | |
| TASK-083 | Build Image node property form (id, source, prompt, size) | | |
| TASK-084 | Build DB node property form (id, source, query) | | |
| TASK-085 | Build Aggregator node property form (id, strategy) | | |
| TASK-086 | Implement form validation with Zod schema | | |
| TASK-087 | Add source dropdown populated from store | | |
| TASK-088 | Create code editor component for prompts/queries (textarea with syntax) | | |
| TASK-089 | Implement real-time form updates to store | | |
| TASK-090 | Add "Reset to Defaults" button | | |
| TASK-091 | Display inline validation errors | | |
| TASK-092 | Style panel with ShadCN UI form components | | |

**Acceptance Criteria:**
- ✅ Panel shows properties when node is selected
- ✅ Form fields update store on change
- ✅ Validation errors display inline with helpful messages
- ✅ Source dropdown lists available sources
- ✅ Panel is empty when no node is selected
- ✅ All node types have complete property forms

---

### Phase 1.7: Source Manager Component (Week 5-6)

**GOAL-007:** Create UI for managing workflow sources (LLM, Image, DB, API configurations).

| Task | Description | Completed | Date |
|------|-------------|-----------|------|
| TASK-093 | Create `components/SourceEditor.tsx` component | | |
| TASK-094 | Implement source list view with cards/table | | |
| TASK-095 | Add "Create New Source" button and modal | | |
| TASK-096 | Create source type selector (LLM, Image, DB, API) | | |
| TASK-097 | Build LLM source form (id, provider, model, api_key_env) | | |
| TASK-098 | Build Image source form (id, provider, api_key_env) | | |
| TASK-099 | Build DB source form (id, db_type, connection_string_env) | | |
| TASK-100 | Build API source form (id, base_url, auth_method) | | |
| TASK-101 | Implement source CRUD operations via store | | |
| TASK-102 | Add source deletion with confirmation dialog | | |
| TASK-103 | Implement source search and filtering | | |
| TASK-104 | Add "Test Connection" button (future: API call) | | |
| TASK-105 | Show source usage count (nodes using this source) | | |
| TASK-106 | Prevent deletion of sources in use | | |
| TASK-107 | Add source import/export (JSON) | | |
| TASK-108 | Style source cards with icons and colors | | |

**Acceptance Criteria:**
- ✅ Sources can be created, edited, and deleted
- ✅ Source list displays all configured sources
- ✅ Forms validate required fields
- ✅ API keys use environment variable references
- ✅ In-use sources cannot be deleted
- ✅ Source data persists in Zustand store

---

### Phase 1.8: JSON Preview Component (Week 7)

**GOAL-008:** Display real-time JSON preview of workflow specification.

| Task | Description | Completed | Date |
|------|-------------|-----------|------|
| TASK-109 | Create `components/JsonPreview.tsx` component | | |
| TASK-110 | Use `generateSpec()` from store to get current JSON | | |
| TASK-111 | Implement syntax highlighting (use `react-json-view` or custom) | | |
| TASK-112 | Add "Copy to Clipboard" button with toast notification | | |
| TASK-113 | Add "Download as File" button (save as .json) | | |
| TASK-114 | Implement collapsible JSON sections | | |
| TASK-115 | Add line numbers to JSON display | | |
| TASK-116 | Update JSON in real-time as workflow changes (debounced) | | |
| TASK-117 | Add search functionality within JSON | | |
| TASK-118 | Style preview with monospace font and proper formatting | | |
| TASK-119 | Make preview panel resizable | | |
| TASK-120 | Add toggle to show/hide preview panel | | |

**Acceptance Criteria:**
- ✅ JSON updates within 300ms of workflow changes
- ✅ JSON is properly formatted and indented
- ✅ Copy button copies valid JSON to clipboard
- ✅ Download saves valid .json file
- ✅ Syntax highlighting improves readability
- ✅ Panel can be toggled on/off

---

### Phase 1.9: Validation Panel Component (Week 7)

**GOAL-009:** Implement workflow validation with error display.

| Task | Description | Completed | Date |
|------|-------------|-----------|------|
| TASK-121 | Create `components/ValidationPanel.tsx` component | | |
| TASK-122 | Add "Validate" button to toolbar | | |
| TASK-123 | Create API client function `validateWorkflow()` | | |
| TASK-124 | Call backend `/workflows/validate` endpoint | | |
| TASK-125 | Display validation results (success/error) | | |
| TASK-126 | Show error list with descriptions | | |
| TASK-127 | Implement click-to-highlight error on canvas | | |
| TASK-128 | Add error count badge to validation button | | |
| TASK-129 | Show loading spinner during validation | | |
| TASK-130 | Display validation timestamp | | |
| TASK-131 | Add keyboard shortcut (Ctrl+Shift+V) for validation | | |
| TASK-132 | Cache validation results until workflow changes | | |

**Acceptance Criteria:**
- ✅ Validation calls backend API successfully
- ✅ Errors display with clear descriptions
- ✅ Clicking error highlights affected node on canvas
- ✅ Success state shows clear confirmation
- ✅ Validation is fast (<500ms for typical workflows)
- ✅ Keyboard shortcut triggers validation

---

### Phase 1.10: Backend API Integration (Week 7-8)

**GOAL-010:** Connect frontend to AgentFlow Core backend with full CRUD operations.

| Task | Description | Completed | Date |
|------|-------------|-----------|------|
| TASK-133 | Complete API client in `lib/api.ts` with all endpoints | | |
| TASK-134 | Implement `POST /workflows/validate` client function | | |
| TASK-135 | Implement `POST /workflows` (create) client function | | |
| TASK-136 | Implement `GET /workflows` (list) client function | | |
| TASK-137 | Implement `GET /workflows/{id}` (get) client function | | |
| TASK-138 | Implement `PUT /workflows/{id}` (update) client function | | |
| TASK-139 | Implement `DELETE /workflows/{id}` (delete) client function | | |
| TASK-140 | Add authentication headers (API key) to all requests | | |
| TASK-141 | Implement error handling with user-friendly messages | | |
| TASK-142 | Add retry logic for failed requests (3 retries) | | |
| TASK-143 | Create TypeScript interfaces for API responses | | |
| TASK-144 | Add request/response logging (dev mode) | | |
| TASK-145 | Implement request timeout (10 seconds) | | |
| TASK-146 | Create API response mocks for testing | | |
| TASK-147 | Write integration tests for API client | | |
| TASK-148 | Configure CORS handling in Next.js API routes | | |

**Acceptance Criteria:**
- ✅ All API endpoints have client functions
- ✅ Requests include proper authentication
- ✅ Error responses are handled gracefully
- ✅ TypeScript ensures type safety
- ✅ Retry logic works for transient failures
- ✅ Integration tests pass with mock backend

**Code Example:**
```typescript
// lib/api.ts
const API_BASE_URL = process.env.NEXT_PUBLIC_CORE_URL || 'http://localhost:8000';
const API_KEY = process.env.AGENTFLOW_API_KEY;

export async function validateWorkflow(spec: WorkflowSpec): Promise<ValidationResult> {
  const response = await fetch(`${API_BASE_URL}/workflows/validate`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'X-API-Key': API_KEY || '',
    },
    body: JSON.stringify(spec),
  });
  
  if (!response.ok) {
    throw new Error(`Validation failed: ${response.statusText}`);
  }
  
  return response.json();
}
```

---

### Phase 1.11: Dashboard Component (Week 8)

**GOAL-011:** Create workflow dashboard for listing, searching, and managing workflows.

| Task | Description | Completed | Date |
|------|-------------|-----------|------|
| TASK-149 | Create `app/page.tsx` dashboard page | | |
| TASK-150 | Fetch workflows list from backend on load | | |
| TASK-151 | Display workflow cards in grid layout | | |
| TASK-152 | Show workflow metadata (name, description, date, node count) | | |
| TASK-153 | Implement search functionality (filter by name) | | |
| TASK-154 | Add "New Workflow" button (navigates to designer) | | |
| TASK-155 | Add "Open" action on workflow card | | |
| TASK-156 | Add "Delete" action with confirmation dialog | | |
| TASK-157 | Add "Export" action (download JSON) | | |
| TASK-158 | Show empty state when no workflows exist | | |
| TASK-159 | Add loading skeleton during fetch | | |
| TASK-160 | Implement error state for failed fetch | | |
| TASK-161 | Add pagination for large workflow lists (future) | | |
| TASK-162 | Style dashboard with responsive grid | | |

**Acceptance Criteria:**
- ✅ Dashboard loads and displays workflows
- ✅ Search filters workflows in real-time
- ✅ New Workflow button navigates to designer
- ✅ Open workflow loads it into canvas
- ✅ Delete removes workflow after confirmation
- ✅ Empty state is user-friendly

---

### Phase 1.12: Designer Page & Layout (Week 8)

**GOAL-012:** Create main designer page with integrated canvas, panels, and toolbar.

| Task | Description | Completed | Date |
|------|-------------|-----------|------|
| TASK-163 | Create `app/designer/page.tsx` main designer page | | |
| TASK-164 | Implement three-column layout (palette, canvas, properties) | | |
| TASK-165 | Add top toolbar with Save, Validate, Execute buttons | | |
| TASK-166 | Add bottom status bar with node count, status indicators | | |
| TASK-167 | Implement panel visibility toggles | | |
| TASK-168 | Make panels resizable with drag handles | | |
| TASK-169 | Add workflow name display/edit in header | | |
| TASK-170 | Implement "Save Workflow" functionality (create or update) | | |
| TASK-171 | Add unsaved changes indicator (*) | | |
| TASK-172 | Add "Back to Dashboard" navigation | | |
| TASK-173 | Implement keyboard shortcut (Ctrl+S) for save | | |
| TASK-174 | Show toast notifications for save success/error | | |
| TASK-175 | Handle browser beforeunload event (warn unsaved changes) | | |
| TASK-176 | Test full workflow: create → edit → validate → save | | |

**Acceptance Criteria:**
- ✅ Designer layout is intuitive and functional
- ✅ Save button persists workflow to backend
- ✅ Unsaved changes indicator works correctly
- ✅ Keyboard shortcuts function properly
- ✅ User is warned before losing unsaved changes
- ✅ Complete workflow round-trip succeeds

---

### Phase 1.13: Import/Export Functionality (Week 8)

**GOAL-013:** Enable workflow import from JSON files and export to JSON.

| Task | Description | Completed | Date |
|------|-------------|-----------|------|
| TASK-177 | Add "Import Workflow" button to dashboard | | |
| TASK-178 | Create file picker for JSON files | | |
| TASK-179 | Validate imported JSON against WorkflowSpec schema | | |
| TASK-180 | Load valid workflow into store and navigate to designer | | |
| TASK-181 | Show error message for invalid JSON | | |
| TASK-182 | Add "Export" button in designer toolbar | | |
| TASK-183 | Generate JSON file download with workflow name | | |
| TASK-184 | Add timestamp to exported filename | | |
| TASK-185 | Test import with example workflow files | | |
| TASK-186 | Test export and re-import roundtrip | | |

**Acceptance Criteria:**
- ✅ Valid JSON files can be imported successfully
- ✅ Invalid JSON shows clear error message
- ✅ Exported files are valid WorkflowSpec JSON
- ✅ Export filename includes workflow name and timestamp
- ✅ Import/export roundtrip preserves workflow integrity

---

## 3. Dependencies

### External Dependencies

- **DEP-001**: `@xyflow/react` v12+ for workflow canvas
- **DEP-002**: `zustand` v4+ for state management
- **DEP-003**: `lucide-react` for icons
- **DEP-004**: `next` v16+ with React 19
- **DEP-005**: `typescript` v5+ for type safety
- **DEP-006**: `tailwindcss` v4+ for styling
- **DEP-007**: `zod` for schema validation
- **DEP-008**: `next-themes` for dark mode support
- **DEP-009**: `sonner` or `react-hot-toast` for notifications
- **DEP-010**: `react-json-view` or alternative for JSON preview

### Backend Dependencies

- **DEP-011**: AgentFlow Core backend API must be running
- **DEP-012**: Backend must implement `/workflows/validate` endpoint
- **DEP-013**: Backend must implement `/workflows` CRUD endpoints
- **DEP-014**: Backend must support CORS for frontend origin
- **DEP-015**: Backend must accept API key authentication

### Development Dependencies

- **DEP-016**: `eslint` for code linting
- **DEP-017**: `prettier` for code formatting
- **DEP-018**: `jest` and `@testing-library/react` for unit tests
- **DEP-019**: `playwright` or `cypress` for E2E tests (Phase 2)

---

## 4. Files

### Core Application Files

- **FILE-001**: `app/layout.tsx` - Root layout with theme provider
- **FILE-002**: `app/page.tsx` - Dashboard page
- **FILE-003**: `app/designer/page.tsx` - Main designer page
- **FILE-004**: `app/api/workflows/route.ts` - API proxy for workflows
- **FILE-005**: `app/api/validate/route.ts` - API proxy for validation

### Component Files

- **FILE-006**: `components/WorkflowCanvas.tsx` - React Flow canvas
- **FILE-007**: `components/NodePalette.tsx` - Node palette sidebar
- **FILE-008**: `components/PropertiesPanel.tsx` - Properties editor
- **FILE-009**: `components/SourceEditor.tsx` - Source manager
- **FILE-010**: `components/JsonPreview.tsx` - JSON preview panel
- **FILE-011**: `components/ValidationPanel.tsx` - Validation results
- **FILE-012**: `components/nodes/InputNode.tsx` - Input node component
- **FILE-013**: `components/nodes/RouterNode.tsx` - Router node component
- **FILE-014**: `components/nodes/LLMNode.tsx` - LLM node component
- **FILE-015**: `components/nodes/ImageNode.tsx` - Image node component
- **FILE-016**: `components/nodes/DBNode.tsx` - DB node component
- **FILE-017**: `components/nodes/AggregatorNode.tsx` - Aggregator node

### Library Files

- **FILE-018**: `lib/stores/useWorkflowStore.ts` - Zustand store
- **FILE-019**: `lib/api.ts` - Backend API client
- **FILE-020**: `lib/types.ts` - TypeScript interfaces
- **FILE-021**: `lib/utils.ts` - Utility functions
- **FILE-022**: `lib/validators.ts` - Zod schemas

### Configuration Files

- **FILE-023**: `next.config.ts` - Next.js configuration
- **FILE-024**: `tsconfig.json` - TypeScript configuration
- **FILE-025**: `tailwind.config.ts` - TailwindCSS configuration
- **FILE-026**: `components.json` - ShadCN UI configuration
- **FILE-027**: `.env.local` - Environment variables (not committed)
- **FILE-028**: `.env.example` - Environment variables template

---

## 5. Testing Strategy

### Unit Tests (Jest + React Testing Library)

- Store actions and state transitions
- Component rendering and props
- Utility functions
- API client functions (with mocks)

### Integration Tests

- Canvas + Store integration
- Properties Panel + Store integration
- API client + Backend (with mock server)

### Manual Testing Checklist

- [ ] Create new workflow from dashboard
- [ ] Add nodes to canvas via drag-and-drop
- [ ] Connect nodes with edges
- [ ] Edit node properties
- [ ] Add and configure sources
- [ ] Validate workflow
- [ ] View JSON preview
- [ ] Save workflow
- [ ] Load existing workflow
- [ ] Export workflow to JSON
- [ ] Import workflow from JSON
- [ ] Delete workflow from dashboard
- [ ] Dark mode toggle
- [ ] Keyboard shortcuts

---

## 6. Success Criteria

✅ **Phase 1 is complete when:**

1. User can create a new workflow from dashboard
2. User can drag nodes from palette to canvas
3. User can connect nodes with edges
4. User can edit node properties in properties panel
5. User can create and manage sources (LLM, Image, DB)
6. User can view real-time JSON preview of workflow
7. User can validate workflow via backend API
8. Validation errors display clearly with click-to-highlight
9. User can save workflow to backend database
10. User can load existing workflows from dashboard
11. User can export workflow as JSON file
12. User can import workflow from JSON file
13. Dark mode toggle works correctly
14. All keyboard shortcuts function properly
15. Unsaved changes are tracked and user is warned
16. Backend API integration is stable and type-safe
17. All P0 features are implemented and tested
18. Code follows TypeScript and React best practices
19. No console errors or warnings in production build
20. Ready for handoff to Phase 2 (Execution & Queue Management)

---

## 7. Risks & Mitigation

| Risk | Impact | Probability | Mitigation |
|------|--------|-------------|------------|
| React Flow performance with 50+ nodes | High | Medium | Implement virtualization, optimize re-renders |
| Backend API not ready | High | Medium | Use mock API responses for development |
| Zustand store state complexity | Medium | Medium | Document store structure, write comprehensive tests |
| TypeScript interface mismatches | Medium | High | Generate types from backend OpenAPI spec |
| Browser compatibility issues | Low | Low | Test on Chrome, Firefox, Safari, Edge |
| Dark mode styling inconsistencies | Low | Medium | Use Tailwind dark: variants consistently |
| Large workflow JSON performance | Medium | Low | Debounce JSON preview updates, add pagination |

---

## 8. Next Steps After Phase 1

1. **Phase 2**: Execution Panel, Queue Editor, Dashboard enhancements
2. **Phase 3**: Performance optimization, advanced canvas features
3. **Phase 4**: Enterprise features (version control, collaboration)

---

**Document Version:** 1.0  
**Last Updated:** December 7, 2025  
**Status:** Ready for Implementation  
**Total Tasks:** 186
