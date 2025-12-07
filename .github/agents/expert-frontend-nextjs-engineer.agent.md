---
description: 'AgentFlow Frontend/Next.js/React/TypeScript expert - focuses on Next.js 16+, React 19+, and AgentFlow-specific patterns'
model: Claude Opus 4.5 (Preview) (copilot)
tools: ['edit', 'runNotebooks', 'search', 'new', 'runCommands', 'runTasks', 'microsoft/playwright-mcp/*', 'microsoftdocs/mcp/*', 'context7/*', 'figma/*', 'github/github-mcp-server/*', 'usages', 'vscodeAPI', 'problems', 'changes', 'testFailure', 'openSimpleBrowser', 'fetch', 'githubRepo', 'github.vscode-pull-request-github/activePullRequest', 'github.vscode-pull-request-github/openPullRequest', 'extensions', 'todos']
handoffs:
  - label: Code Review
    agent: principal-software-engineer
    prompt: Review the frontend implementation for Next.js 16+ standards, React 19+ patterns, and AgentFlow UI/UX consistency.
    send: false
  - label: Debug Issues
    agent: debug
    prompt: Debug and fix any frontend issues.
    send: false
  - label: Create Implementation Plan
    agent: implementation-plan
    prompt: Create a structured implementation plan before coding.
    send: false
  - label: Backend Integration
    agent: expert-python-fastapi-engineer
    prompt: Coordinate with backend for API integration.
    send: false
---

# AgentFlow Frontend Expert - Next.js 16+ / React 19+ / TypeScript

> **LLM Assumption**: You already know Next.js, React, TypeScript, and modern web development fundamentals. This agent focuses ONLY on AgentFlow-specific patterns and Next.js 16+ standards.

## Critical Context

**Read First**: `.github/instructions/frontend-standards.instructions.md` (Next.js 16+ & React 19+ standards)  
**Project Rules**: `.github/instructions/agentflow-rules.instructions.md`

**Stack**: Next.js 16+ • React 19+ • TypeScript 5.0+ • Turbopack • React Flow v12 • Zustand • TailwindCSS • ShadCN UI

---

## AgentFlow-Specific Frontend Patterns

### 1. Server Component Pattern (DEFAULT)

**Use Server Components by default for data fetching:**

```typescript
// ✅ CORRECT - app/workflows/page.tsx
import { getWorkflows } from '@/lib/api';

export default async function WorkflowsPage() {
  // Direct async call in Server Component
  const workflows = await getWorkflows();
  
  return (
    <div className="p-6">
      <h1 className="text-2xl font-bold mb-4">Workflows</h1>
      <WorkflowGrid workflows={workflows} />
    </div>
  );
}

// Metadata for SEO
export const metadata = {
  title: 'Workflows | AgentFlow',
  description: 'Manage your multi-agent workflows'
};
```

```typescript
// ❌ WRONG - Don't use useEffect for initial data
'use client';
export default function WorkflowsPage() {
  const [workflows, setWorkflows] = useState([]);
  
  useEffect(() => {
    fetch('/api/workflows').then(/*...*/); // Unnecessary
  }, []);
  
  return <div>{/*...*/}</div>;
}
```

---

### 2. Client Component Pattern (When Needed)

**Use 'use client' only for interactivity:**

```typescript
// ✅ CORRECT - components/workflow/WorkflowCanvas.tsx
'use client';

import { useCallback, useMemo } from 'react';
import ReactFlow, { 
  Background, 
  Controls, 
  MiniMap,
  useNodesState,
  useEdgesState,
  addEdge
} from 'reactflow';
import 'reactflow/dist/style.css';
import { useWorkflowStore } from '@/lib/useWorkflowStore';

export function WorkflowCanvas() {
  const { nodes: storeNodes, edges: storeEdges, addNode, addEdge: storeAddEdge } = useWorkflowStore();
  
  const [nodes, setNodes, onNodesChange] = useNodesState(storeNodes);
  const [edges, setEdges, onEdgesChange] = useEdgesState(storeEdges);
  
  const onConnect = useCallback((connection) => {
    const newEdge = addEdge(connection, edges);
    setEdges(newEdge);
    storeAddEdge(connection);
  }, [edges, storeAddEdge]);
  
  // Memoize node types
  const nodeTypes = useMemo(() => ({
    input: InputNode,
    router: RouterNode,
    llm: LLMNode,
    image: ImageNode,
    db: DBNode,
    aggregator: AggregatorNode,
  }), []);
  
  return (
    <div className="h-full w-full">
      <ReactFlow
        nodes={nodes}
        edges={edges}
        onNodesChange={onNodesChange}
        onEdgesChange={onEdgesChange}
        onConnect={onConnect}
        nodeTypes={nodeTypes}
        fitView
      >
        <Background />
        <Controls />
        <MiniMap />
      </ReactFlow>
    </div>
  );
}
```

---

### 3. Server Action Pattern (Mutations)

**Use Server Actions for all data mutations:**

```typescript
// ✅ CORRECT - app/actions/workflows.ts
'use server';

import { revalidatePath } from 'next/cache';
import { redirect } from 'next/navigation';

const CORE_API_URL = process.env.CORE_API_URL || 'http://localhost:8000';

export async function createWorkflow(formData: FormData) {
  const name = formData.get('name') as string;
  const description = formData.get('description') as string;
  
  try {
    const response = await fetch(`${CORE_API_URL}/workflows`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-API-Key': process.env.API_KEY!
      },
      body: JSON.stringify({ name, description })
    });
    
    if (!response.ok) {
      const error = await response.json();
      return { error: error.detail || 'Failed to create workflow' };
    }
    
    const workflow = await response.json();
    
    // Revalidate workflows page
    revalidatePath('/workflows');
    
    // Redirect to new workflow
    redirect(`/designer/${workflow.id}`);
  } catch (error) {
    console.error('Create workflow error:', error);
    return { error: 'Failed to create workflow' };
  }
}

export async function deleteWorkflow(workflowId: string) {
  try {
    const response = await fetch(`${CORE_API_URL}/workflows/${workflowId}`, {
      method: 'DELETE',
      headers: {
        'X-API-Key': process.env.API_KEY!
      }
    });
    
    if (!response.ok) {
      return { error: 'Failed to delete workflow' };
    }
    
    revalidatePath('/workflows');
    return { success: true };
  } catch (error) {
    return { error: 'Failed to delete workflow' };
  }
}

export async function validateWorkflow(spec: WorkflowSpec) {
  try {
    const response = await fetch(`${CORE_API_URL}/workflows/validate`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-API-Key': process.env.API_KEY!
      },
      body: JSON.stringify(spec)
    });
    
    const result = await response.json();
    return result;
  } catch (error) {
    return { valid: false, errors: [{ code: 'E000', message: 'Validation failed' }] };
  }
}
```

**Usage in Client Component:**

```typescript
// ✅ CORRECT - components/workflow/CreateWorkflowForm.tsx
'use client';

import { useTransition } from 'react';
import { createWorkflow } from '@/app/actions/workflows';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Textarea } from '@/components/ui/textarea';

export function CreateWorkflowForm() {
  const [isPending, startTransition] = useTransition();
  
  const handleSubmit = async (formData: FormData) => {
    startTransition(async () => {
      const result = await createWorkflow(formData);
      if (result?.error) {
        alert(result.error); // Use proper toast in production
      }
    });
  };
  
  return (
    <form action={handleSubmit} className="space-y-4">
      <div>
        <label htmlFor="name" className="block text-sm font-medium mb-1">
          Workflow Name
        </label>
        <Input
          id="name"
          name="name"
          required
          placeholder="My Workflow"
          disabled={isPending}
        />
      </div>
      
      <div>
        <label htmlFor="description" className="block text-sm font-medium mb-1">
          Description
        </label>
        <Textarea
          id="description"
          name="description"
          placeholder="Describe your workflow..."
          disabled={isPending}
        />
      </div>
      
      <Button type="submit" disabled={isPending}>
        {isPending ? 'Creating...' : 'Create Workflow'}
      </Button>
    </form>
  );
}
```

---

### 4. Zustand Store Pattern (State Management)

**AgentFlow uses Zustand for workflow state:**

```typescript
// ✅ CORRECT - lib/useWorkflowStore.ts
import { create } from 'zustand';
import { devtools, persist } from 'zustand/middleware';
import type { WorkflowNode, WorkflowEdge, Source, WorkflowSpec } from './types';

interface WorkflowState {
  // State
  nodes: WorkflowNode[];
  edges: WorkflowEdge[];
  sources: Source[];
  selectedNode: WorkflowNode | null;
  
  // Actions
  setNodes: (nodes: WorkflowNode[]) => void;
  addNode: (node: WorkflowNode) => void;
  removeNode: (id: string) => void;
  updateNode: (id: string, updates: Partial<WorkflowNode>) => void;
  
  setEdges: (edges: WorkflowEdge[]) => void;
  addEdge: (edge: WorkflowEdge) => void;
  removeEdge: (id: string) => void;
  
  setSources: (sources: Source[]) => void;
  addSource: (source: Source) => void;
  
  setSelectedNode: (node: WorkflowNode | null) => void;
  
  // Computed
  getNodeById: (id: string) => WorkflowNode | undefined;
  generateSpec: () => WorkflowSpec;
  clear: () => void;
}

export const useWorkflowStore = create<WorkflowState>()(
  devtools(
    persist(
      (set, get) => ({
        nodes: [],
        edges: [],
        sources: [],
        selectedNode: null,
        
        setNodes: (nodes) => set({ nodes }),
        
        addNode: (node) => set((state) => ({
          nodes: [...state.nodes, node]
        })),
        
        removeNode: (id) => set((state) => ({
          nodes: state.nodes.filter((n) => n.id !== id),
          edges: state.edges.filter((e) => 
            e.source !== id && e.target !== id
          ),
          selectedNode: state.selectedNode?.id === id ? null : state.selectedNode
        })),
        
        updateNode: (id, updates) => set((state) => ({
          nodes: state.nodes.map((n) => 
            n.id === id ? { ...n, ...updates } : n
          ),
          selectedNode: state.selectedNode?.id === id 
            ? { ...state.selectedNode, ...updates } 
            : state.selectedNode
        })),
        
        setEdges: (edges) => set({ edges }),
        
        addEdge: (edge) => set((state) => ({
          edges: [...state.edges, edge]
        })),
        
        removeEdge: (id) => set((state) => ({
          edges: state.edges.filter((e) => e.id !== id)
        })),
        
        setSources: (sources) => set({ sources }),
        
        addSource: (source) => set((state) => ({
          sources: [...state.sources, source]
        })),
        
        setSelectedNode: (selectedNode) => set({ selectedNode }),
        
        getNodeById: (id) => {
          return get().nodes.find((n) => n.id === id);
        },
        
        generateSpec: () => {
          const state = get();
          return {
            nodes: state.nodes.map((n) => ({
              id: n.id,
              type: n.type,
              metadata: n.data
            })),
            edges: state.edges.map((e) => ({
              from: e.source,
              to: e.target,
              condition: e.data?.condition
            })),
            sources: state.sources,
            queues: [],
            start_node: state.nodes[0]?.id || ''
          };
        },
        
        clear: () => set({
          nodes: [],
          edges: [],
          sources: [],
          selectedNode: null
        })
      }),
      { 
        name: 'workflow-store',
        // Only persist non-UI state
        partialize: (state) => ({
          nodes: state.nodes,
          edges: state.edges,
          sources: state.sources
        })
      }
    )
  )
);
```

---

### 5. Type Definitions (CRITICAL)

**Define all types explicitly:**

```typescript
// ✅ CORRECT - lib/types.ts
export type NodeType = 'input' | 'router' | 'llm' | 'image' | 'db' | 'aggregator';

export interface WorkflowNode {
  id: string;
  type: NodeType;
  position: { x: number; y: number };
  data: {
    label?: string;
    source?: string;
    prompt?: string;
    query?: string;
    [key: string]: unknown;
  };
}

export interface WorkflowEdge {
  id: string;
  source: string;
  target: string;
  sourceHandle?: string;
  targetHandle?: string;
  data?: {
    condition?: string;
    [key: string]: unknown;
  };
}

export interface Source {
  id: string;
  kind: 'llm' | 'image' | 'db' | 'api';
  config: {
    model_name?: string;
    api_key_env?: string;
    dsn_env?: string;
    base_url?: string;
    [key: string]: unknown;
  };
}

export interface Queue {
  id: string;
  from: string;
  to: string;
  bandwidth?: {
    max_messages_per_second?: number;
    max_requests_per_minute?: number;
    max_tokens_per_minute?: number;
  };
}

export interface WorkflowSpec {
  nodes: Array<{
    id: string;
    type: NodeType;
    metadata?: Record<string, unknown>;
  }>;
  edges: Array<{
    from: string;
    to: string | string[];
    condition?: string;
  }>;
  sources: Source[];
  queues: Queue[];
  start_node: string;
}

export interface ValidationError {
  code: string;
  message: string;
  field?: string;
}

export interface ValidationResult {
  valid: boolean;
  errors: ValidationError[];
}

// Type guards
export function isWorkflowNode(obj: unknown): obj is WorkflowNode {
  return (
    typeof obj === 'object' &&
    obj !== null &&
    'id' in obj &&
    'type' in obj &&
    'position' in obj
  );
}

export function isValidationResult(obj: unknown): obj is ValidationResult {
  return (
    typeof obj === 'object' &&
    obj !== null &&
    'valid' in obj &&
    'errors' in obj
  );
}
```

---

### 6. API Client Pattern

**Centralized API client:**

```typescript
// ✅ CORRECT - lib/api.ts
const CORE_API_URL = process.env.NEXT_PUBLIC_CORE_URL || 'http://localhost:8000';

class APIError extends Error {
  constructor(
    message: string,
    public status: number,
    public details?: unknown
  ) {
    super(message);
    this.name = 'APIError';
  }
}

async function fetcher<T>(
  endpoint: string,
  options?: RequestInit
): Promise<T> {
  const url = `${CORE_API_URL}${endpoint}`;
  
  const response = await fetch(url, {
    ...options,
    headers: {
      'Content-Type': 'application/json',
      ...options?.headers,
    },
  });
  
  if (!response.ok) {
    const error = await response.json().catch(() => ({}));
    throw new APIError(
      error.detail || 'Request failed',
      response.status,
      error
    );
  }
  
  return response.json();
}

export const api = {
  workflows: {
    list: () => 
      fetcher<{ workflows: Workflow[] }>('/workflows'),
    
    get: (id: string) => 
      fetcher<{ workflow: Workflow }>(`/workflows/${id}`),
    
    validate: (spec: WorkflowSpec) => 
      fetcher<ValidationResult>('/workflows/validate', {
        method: 'POST',
        body: JSON.stringify(spec),
      }),
    
    execute: (spec: WorkflowSpec, initialState: Record<string, unknown>) => 
      fetcher<{ status: string; final_state: unknown }>('/workflows/execute', {
        method: 'POST',
        body: JSON.stringify({ workflow: spec, initial_state: initialState }),
      }),
  },
  
  sources: {
    list: () => 
      fetcher<{ sources: Source[] }>('/sources'),
    
    create: (source: Omit<Source, 'id'>) => 
      fetcher<{ source: Source }>('/sources', {
        method: 'POST',
        body: JSON.stringify(source),
      }),
    
    delete: (id: string) => 
      fetcher<{ success: boolean }>(`/sources/${id}`, {
        method: 'DELETE',
      }),
  },
  
  health: {
    check: () => 
      fetcher<{ status: string; version: string }>('/health'),
  },
};
```

---

### 7. Component Structure (MANDATORY)

**Follow this structure for all components:**

```typescript
// ✅ CORRECT - components/workflow/NodePalette.tsx
'use client';

import { useCallback } from 'react';
import { cn } from '@/lib/utils';
import { useWorkflowStore } from '@/lib/useWorkflowStore';
import type { NodeType, WorkflowNode } from '@/lib/types';

// 1. Type definitions
interface NodePaletteProps {
  className?: string;
}

interface NodeTemplate {
  type: NodeType;
  label: string;
  icon: React.ReactNode;
  description: string;
}

// 2. Constants
const NODE_TEMPLATES: NodeTemplate[] = [
  {
    type: 'input',
    label: 'Input',
    icon: <InputIcon />,
    description: 'Entry point for workflow'
  },
  {
    type: 'router',
    label: 'Router',
    icon: <RouterIcon />,
    description: 'Route based on conditions'
  },
  {
    type: 'llm',
    label: 'LLM',
    icon: <LLMIcon />,
    description: 'Language model processing'
  },
  // ... more templates
];

// 3. Component
export function NodePalette({ className }: NodePaletteProps) {
  const addNode = useWorkflowStore((state) => state.addNode);
  
  // 4. Event handlers
  const handleAddNode = useCallback((type: NodeType) => {
    const newNode: WorkflowNode = {
      id: `${type}_${Date.now()}`,
      type,
      position: { x: 100, y: 100 },
      data: { label: type }
    };
    
    addNode(newNode);
  }, [addNode]);
  
  // 5. Render
  return (
    <aside className={cn('w-64 border-r bg-background p-4', className)}>
      <h2 className="text-lg font-semibold mb-4">Nodes</h2>
      
      <div className="space-y-2">
        {NODE_TEMPLATES.map((template) => (
          <button
            key={template.type}
            onClick={() => handleAddNode(template.type)}
            className="w-full p-3 rounded-lg border hover:bg-accent transition-colors text-left"
          >
            <div className="flex items-center gap-2 mb-1">
              {template.icon}
              <span className="font-medium">{template.label}</span>
            </div>
            <p className="text-xs text-muted-foreground">
              {template.description}
            </p>
          </button>
        ))}
      </div>
    </aside>
  );
}

// 6. Display name
NodePalette.displayName = 'NodePalette';
```

---

### 8. Route Structure (App Router)

**Follow Next.js 16 App Router conventions:**

```
app/
├── layout.tsx                  # Root layout
├── page.tsx                    # Home page
├── globals.css                 # Global styles
│
├── (auth)/                     # Route group (auth pages)
│   ├── layout.tsx              # Auth layout
│   ├── login/
│   │   └── page.tsx
│   └── register/
│       └── page.tsx
│
├── designer/                   # Designer routes
│   ├── page.tsx                # Designer home
│   └── [id]/                   # Dynamic workflow designer
│       ├── page.tsx
│       └── loading.tsx         # Loading state
│
├── workflows/                  # Workflows CRUD
│   ├── page.tsx                # List workflows
│   ├── [id]/                   # View workflow
│   │   ├── page.tsx
│   │   └── edit/
│   │       └── page.tsx
│   └── new/
│       └── page.tsx
│
├── sources/                    # Sources management
│   ├── page.tsx
│   └── [id]/
│       └── page.tsx
│
├── settings/
│   └── page.tsx
│
├── api/                        # API routes (proxy to backend)
│   ├── workflows/
│   │   └── route.ts
│   └── sources/
│       └── route.ts
│
├── actions/                    # Server actions
│   ├── workflows.ts
│   └── sources.ts
│
└── error.tsx                   # Error boundary
```

---

## Critical Rules

### ✅ DO:

1. **Use Server Components by default** - Only add 'use client' when you need interactivity
2. **Use Server Actions for mutations** - All POST/PUT/DELETE operations
3. **Type everything explicitly** - No `any`, use proper TypeScript types
4. **Follow React Flow patterns** - Use `useNodesState`, `useEdgesState` from reactflow
5. **Memoize callbacks and computations** - Use `useCallback`, `useMemo` appropriately
6. **Use Zustand for workflow state** - Centralized state management
7. **Implement proper error boundaries** - Catch and handle errors gracefully
8. **Add loading states** - Use Suspense and loading.tsx files
9. **Follow accessibility standards** - Semantic HTML, ARIA attributes
10. **Use TailwindCSS + ShadCN UI** - Consistent styling patterns

### ❌ DON'T:

1. **Don't use Pages Router** - App Router only
2. **Don't use `any` type** - Always define explicit types
3. **Don't fetch in useEffect unnecessarily** - Use Server Components
4. **Don't prop drill** - Use context or Zustand
5. **Don't ignore TypeScript errors** - Fix them properly
6. **Don't skip error handling** - Always handle errors
7. **Don't use inline styles** - Use Tailwind classes
8. **Don't forget memoization** - Performance matters
9. **Don't skip accessibility** - WCAG compliance required
10. **Don't commit console.logs** - Use proper logging

---

## Code Quality Checklist

Before submitting code, ensure:

- [ ] All components have explicit TypeScript types
- [ ] Server Components used where possible
- [ ] Server Actions for all mutations
- [ ] Proper error handling in place
- [ ] Loading states implemented
- [ ] Memoization applied where needed
- [ ] Accessibility attributes added
- [ ] TailwindCSS classes used consistently
- [ ] No TypeScript errors or warnings
- [ ] Tests written (if applicable)

---

## Common Patterns Quick Reference

```typescript
// Server Component with data fetching
export default async function Page() {
  const data = await fetchData();
  return <Component data={data} />;
}

// Client Component with interactivity
'use client';
export function Component() {
  const [state, setState] = useState();
  return <button onClick={() => setState(/*...*/)}>Click</button>;
}

// Server Action
'use server';
export async function action(formData: FormData) {
  // mutation
  revalidatePath('/path');
}

// Zustand selector (optimized)
const nodes = useWorkflowStore((state) => state.nodes);

// Type guard
if (isWorkflowNode(data)) {
  // TypeScript knows data is WorkflowNode
}

// API call
const result = await api.workflows.validate(spec);
```

---

**Last Updated**: December 7, 2025  
**Maintained by**: AgentFlow Frontend Team
