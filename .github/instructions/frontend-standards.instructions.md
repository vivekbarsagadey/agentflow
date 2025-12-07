---
applyTo: 'frontend/**'
---

# Frontend Development Standards - Next.js 16+ & TypeScript

> **Target Stack**: Next.js 16+, React 19+, TypeScript 5.0+, Turbopack, React Flow v12

**Last Updated**: December 7, 2025  
**Applies To**: All frontend code in `frontend/agentflow-studio/`

---

## Table of Contents

1. [Next.js 16+ Specific Standards](#nextjs-16-specific-standards)
2. [TypeScript Standards](#typescript-standards)
3. [React 19+ Standards](#react-19-standards)
4. [File Structure & Naming](#file-structure--naming)
5. [Component Patterns](#component-patterns)
6. [State Management](#state-management)
7. [Performance Optimization](#performance-optimization)
8. [Code Style & Formatting](#code-style--formatting)
9. [Testing Standards](#testing-standards)
10. [Accessibility (a11y)](#accessibility-a11y)

---

## 1. Next.js 16+ Specific Standards

### 1.1 App Router (Required)

**✅ DO**: Use App Router exclusively (not Pages Router)

```typescript
// ✅ CORRECT - App Router structure
app/
├── layout.tsx           # Root layout
├── page.tsx            # Home page
├── designer/
│   ├── layout.tsx      # Designer layout
│   └── page.tsx        # Designer page
└── api/
    └── workflows/
        └── route.ts    # API route handler
```

```typescript
// ❌ WRONG - Pages Router (deprecated)
pages/
├── index.tsx
├── designer.tsx
└── api/
    └── workflows.ts
```

### 1.2 Server Components by Default

**✅ DO**: Use React Server Components (RSC) by default

```typescript
// ✅ CORRECT - Server Component (default)
// app/workflows/page.tsx
import { getWorkflows } from '@/lib/api';

export default async function WorkflowsPage() {
  const workflows = await getWorkflows(); // Direct async call
  
  return (
    <div>
      {workflows.map((wf) => (
        <WorkflowCard key={wf.id} workflow={wf} />
      ))}
    </div>
  );
}
```

```typescript
// ❌ WRONG - Using useEffect in Server Component
export default function WorkflowsPage() {
  const [workflows, setWorkflows] = useState([]);
  
  useEffect(() => {
    fetch('/api/workflows').then(/*...*/); // Unnecessary client-side fetch
  }, []);
  
  return <div>{/*...*/}</div>;
}
```

**✅ DO**: Use `'use client'` directive only when needed

```typescript
// ✅ CORRECT - Client Component when needed
'use client';

import { useState } from 'react';
import { useWorkflowStore } from '@/lib/useWorkflowStore';

export function WorkflowCanvas() {
  const [selectedNode, setSelectedNode] = useState(null);
  const { nodes, edges } = useWorkflowStore();
  
  return <ReactFlow nodes={nodes} edges={edges} />;
}
```

### 1.3 Server Actions (Preferred for Mutations)

**✅ DO**: Use Server Actions for data mutations

```typescript
// ✅ CORRECT - Server Action
// app/actions/workflows.ts
'use server';

import { revalidatePath } from 'next/cache';

export async function createWorkflow(formData: FormData) {
  const name = formData.get('name') as string;
  
  const response = await fetch(`${process.env.CORE_API_URL}/workflows`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ name })
  });
  
  if (!response.ok) {
    return { error: 'Failed to create workflow' };
  }
  
  revalidatePath('/workflows');
  return { success: true };
}
```

```typescript
// ✅ CORRECT - Using Server Action in Client Component
'use client';

import { createWorkflow } from '@/app/actions/workflows';
import { useTransition } from 'react';

export function CreateWorkflowForm() {
  const [isPending, startTransition] = useTransition();
  
  const handleSubmit = (formData: FormData) => {
    startTransition(async () => {
      await createWorkflow(formData);
    });
  };
  
  return (
    <form action={handleSubmit}>
      <input name="name" required />
      <button disabled={isPending}>Create</button>
    </form>
  );
}
```

### 1.4 Turbopack Configuration

**✅ DO**: Optimize for Turbopack in `next.config.ts`

```typescript
// ✅ CORRECT - next.config.ts
import type { NextConfig } from 'next';

const config: NextConfig = {
  // Enable Turbopack for dev and build
  turbopack: {
    // Turbopack-specific optimizations
    resolveAlias: {
      '@': './src',
    },
  },
  
  // Modern JavaScript output
  output: 'standalone',
  
  // Optimize images
  images: {
    domains: ['api.agentflow.com'],
    formats: ['image/avif', 'image/webp'],
  },
  
  // Strict mode
  reactStrictMode: true,
  
  // TypeScript strict mode
  typescript: {
    ignoreBuildErrors: false,
  },
  
  // ESLint during builds
  eslint: {
    ignoreDuringBuilds: false,
  },
};

export default config;
```

### 1.5 Metadata API

**✅ DO**: Use Metadata API for SEO

```typescript
// ✅ CORRECT - Static Metadata
// app/designer/page.tsx
import type { Metadata } from 'next';

export const metadata: Metadata = {
  title: 'Workflow Designer | AgentFlow',
  description: 'Design and orchestrate multi-agent workflows visually',
  openGraph: {
    title: 'Workflow Designer',
    description: 'Visual workflow orchestration',
    images: ['/og-image.png'],
  },
};

export default function DesignerPage() {
  return <div>Designer</div>;
}
```

```typescript
// ✅ CORRECT - Dynamic Metadata
// app/workflows/[id]/page.tsx
export async function generateMetadata({ params }: Props): Promise<Metadata> {
  const workflow = await getWorkflow(params.id);
  
  return {
    title: `${workflow.name} | AgentFlow`,
    description: workflow.description,
  };
}
```

### 1.6 Route Handlers (API Routes)

**✅ DO**: Use new Route Handler format

```typescript
// ✅ CORRECT - Route Handler
// app/api/workflows/route.ts
import { NextRequest, NextResponse } from 'next/server';

export async function GET(request: NextRequest) {
  const searchParams = request.nextUrl.searchParams;
  const userId = searchParams.get('userId');
  
  const workflows = await fetchWorkflows(userId);
  
  return NextResponse.json({ workflows });
}

export async function POST(request: NextRequest) {
  const body = await request.json();
  
  // Validate
  if (!body.name) {
    return NextResponse.json(
      { error: 'Name is required' },
      { status: 400 }
    );
  }
  
  const workflow = await createWorkflow(body);
  
  return NextResponse.json({ workflow }, { status: 201 });
}
```

---

## 2. TypeScript Standards

### 2.1 Strict Type Safety

**✅ DO**: Enable strict TypeScript in `tsconfig.json`

```json
{
  "compilerOptions": {
    "strict": true,
    "strictNullChecks": true,
    "strictFunctionTypes": true,
    "noImplicitAny": true,
    "noImplicitThis": true,
    "alwaysStrict": true,
    "noUnusedLocals": true,
    "noUnusedParameters": true,
    "noImplicitReturns": true,
    "noFallthroughCasesInSwitch": true,
    "forceConsistentCasingInFileNames": true,
    "skipLibCheck": true
  }
}
```

### 2.2 Type Definitions

**✅ DO**: Define explicit types for all data structures

```typescript
// ✅ CORRECT - Explicit types
// lib/types.ts
export interface WorkflowNode {
  id: string;
  type: 'input' | 'router' | 'llm' | 'image' | 'db' | 'aggregator';
  position: { x: number; y: number };
  data: Record<string, unknown>;
}

export interface WorkflowEdge {
  id: string;
  source: string;
  target: string;
  sourceHandle?: string;
  targetHandle?: string;
}

export interface WorkflowSpec {
  nodes: WorkflowNode[];
  edges: WorkflowEdge[];
  sources: Source[];
  queues: Queue[];
  start_node: string;
}
```

```typescript
// ❌ WRONG - Using 'any'
export interface WorkflowNode {
  id: string;
  type: any; // Never use 'any'
  position: any;
  data: any;
}
```

**✅ DO**: Use type guards for runtime validation

```typescript
// ✅ CORRECT - Type guard
export function isWorkflowNode(obj: unknown): obj is WorkflowNode {
  return (
    typeof obj === 'object' &&
    obj !== null &&
    'id' in obj &&
    'type' in obj &&
    'position' in obj &&
    typeof (obj as WorkflowNode).id === 'string'
  );
}

// Usage
const data = await response.json();
if (isWorkflowNode(data)) {
  // TypeScript knows data is WorkflowNode here
  console.log(data.type);
}
```

### 2.3 Generics

**✅ DO**: Use generics for reusable components

```typescript
// ✅ CORRECT - Generic component
interface DataTableProps<T> {
  data: T[];
  columns: Array<{
    key: keyof T;
    header: string;
    render?: (value: T[keyof T]) => React.ReactNode;
  }>;
  onRowClick?: (row: T) => void;
}

export function DataTable<T>({ data, columns, onRowClick }: DataTableProps<T>) {
  return (
    <table>
      <thead>
        <tr>
          {columns.map((col) => (
            <th key={String(col.key)}>{col.header}</th>
          ))}
        </tr>
      </thead>
      <tbody>
        {data.map((row, idx) => (
          <tr key={idx} onClick={() => onRowClick?.(row)}>
            {columns.map((col) => (
              <td key={String(col.key)}>
                {col.render ? col.render(row[col.key]) : String(row[col.key])}
              </td>
            ))}
          </tr>
        ))}
      </tbody>
    </table>
  );
}
```

### 2.4 Utility Types

**✅ DO**: Use TypeScript utility types

```typescript
// ✅ CORRECT - Using utility types
type PartialWorkflow = Partial<WorkflowSpec>;
type ReadonlyWorkflow = Readonly<WorkflowSpec>;
type NodeType = Pick<WorkflowNode, 'id' | 'type'>;
type NodeWithoutPosition = Omit<WorkflowNode, 'position'>;
type RequiredNode = Required<WorkflowNode>;

// Extract types from arrays
type NodeTypes = WorkflowNode['type']; // 'input' | 'router' | ...

// Conditional types
type FilterByType<T, U> = T extends U ? T : never;
```

---

## 3. React 19+ Standards

### 3.1 Hooks Rules

**✅ DO**: Follow React 19 hooks best practices

```typescript
// ✅ CORRECT - Proper hook usage
'use client';

import { useState, useEffect, useCallback, useMemo } from 'react';

export function WorkflowEditor({ initialWorkflow }: Props) {
  const [workflow, setWorkflow] = useState(initialWorkflow);
  
  // Memoize expensive calculations
  const nodeCount = useMemo(() => {
    return workflow.nodes.length;
  }, [workflow.nodes]);
  
  // Memoize callbacks
  const addNode = useCallback((node: WorkflowNode) => {
    setWorkflow((prev) => ({
      ...prev,
      nodes: [...prev.nodes, node]
    }));
  }, []);
  
  // Effects
  useEffect(() => {
    const handleKeyPress = (e: KeyboardEvent) => {
      if (e.key === 's' && (e.metaKey || e.ctrlKey)) {
        e.preventDefault();
        saveWorkflow();
      }
    };
    
    window.addEventListener('keydown', handleKeyPress);
    return () => window.removeEventListener('keydown', handleKeyPress);
  }, [workflow]);
  
  return <div>{/*...*/}</div>;
}
```

### 3.2 React 19 Transitions

**✅ DO**: Use transitions for non-urgent updates

```typescript
// ✅ CORRECT - Using useTransition
'use client';

import { useTransition } from 'react';

export function WorkflowList() {
  const [isPending, startTransition] = useTransition();
  const [workflows, setWorkflows] = useState([]);
  const [searchTerm, setSearchTerm] = useState('');
  
  const handleSearch = (term: string) => {
    setSearchTerm(term); // Urgent: update input immediately
    
    startTransition(() => {
      // Non-urgent: filter can wait
      setWorkflows(filterWorkflows(allWorkflows, term));
    });
  };
  
  return (
    <div>
      <input
        value={searchTerm}
        onChange={(e) => handleSearch(e.target.value)}
      />
      {isPending && <Spinner />}
      <WorkflowGrid workflows={workflows} />
    </div>
  );
}
```

### 3.3 Suspense Boundaries

**✅ DO**: Use Suspense for data fetching

```typescript
// ✅ CORRECT - Suspense usage
// app/workflows/page.tsx
import { Suspense } from 'react';

export default function WorkflowsPage() {
  return (
    <div>
      <h1>Workflows</h1>
      <Suspense fallback={<WorkflowsSkeleton />}>
        <WorkflowList />
      </Suspense>
    </div>
  );
}

// Async Server Component
async function WorkflowList() {
  const workflows = await getWorkflows();
  return <div>{/* render workflows */}</div>;
}
```

### 3.4 Error Boundaries

**✅ DO**: Implement error boundaries

```typescript
// ✅ CORRECT - Error Boundary
'use client';

import { Component, ReactNode } from 'react';

interface Props {
  children: ReactNode;
  fallback?: ReactNode;
}

interface State {
  hasError: boolean;
  error?: Error;
}

export class ErrorBoundary extends Component<Props, State> {
  constructor(props: Props) {
    super(props);
    this.state = { hasError: false };
  }
  
  static getDerivedStateFromError(error: Error): State {
    return { hasError: true, error };
  }
  
  componentDidCatch(error: Error, errorInfo: React.ErrorInfo) {
    console.error('ErrorBoundary caught:', error, errorInfo);
  }
  
  render() {
    if (this.state.hasError) {
      return this.props.fallback || (
        <div className="error-container">
          <h2>Something went wrong</h2>
          <p>{this.state.error?.message}</p>
          <button onClick={() => this.setState({ hasError: false })}>
            Try again
          </button>
        </div>
      );
    }
    
    return this.props.children;
  }
}
```

---

## 4. File Structure & Naming

### 4.1 Naming Conventions

```typescript
// ✅ CORRECT - Naming conventions

// Components: PascalCase
WorkflowCanvas.tsx
NodePalette.tsx
PropertiesPanel.tsx

// Utilities/Hooks: camelCase
useWorkflowStore.ts
formatDate.ts
apiClient.ts

// Constants: UPPER_SNAKE_CASE
const MAX_NODES = 100;
const API_BASE_URL = 'https://api.agentflow.com';

// Types/Interfaces: PascalCase
interface WorkflowNode {}
type NodeType = string;

// Files: kebab-case for non-components
workflow-utils.ts
api-client.ts
validation-helpers.ts
```

### 4.2 Directory Structure

```
app/
├── (auth)/                    # Route group (doesn't affect URL)
│   ├── login/
│   │   └── page.tsx
│   └── layout.tsx
├── designer/
│   ├── [id]/                  # Dynamic route
│   │   └── page.tsx
│   ├── layout.tsx
│   └── page.tsx
├── api/
│   └── workflows/
│       └── route.ts
├── layout.tsx                 # Root layout
├── page.tsx                   # Home page
└── globals.css

components/                    # Shared components
├── ui/                       # UI primitives (ShadCN)
│   ├── button.tsx
│   ├── input.tsx
│   └── dialog.tsx
├── workflow/                 # Domain components
│   ├── WorkflowCanvas.tsx
│   ├── NodePalette.tsx
│   └── PropertiesPanel.tsx
└── layout/
    ├── Header.tsx
    └── Sidebar.tsx

lib/                          # Utilities
├── types.ts                  # Type definitions
├── utils.ts                  # General utilities
├── api.ts                    # API client
├── hooks/                    # Custom hooks
│   ├── useWorkflowStore.ts
│   └── useDebounce.ts
└── validators/               # Validation functions
    └── workflow-validator.ts
```

---

## 5. Component Patterns

### 5.1 Component Structure

**✅ DO**: Follow consistent component structure

```typescript
// ✅ CORRECT - Component structure
'use client';

import { useState, useEffect, type FC } from 'react';
import { cn } from '@/lib/utils';

// 1. Type definitions
interface WorkflowCanvasProps {
  workflowId: string;
  onSave?: (workflow: WorkflowSpec) => void;
  className?: string;
}

// 2. Component definition
export const WorkflowCanvas: FC<WorkflowCanvasProps> = ({
  workflowId,
  onSave,
  className,
}) => {
  // 3. Hooks
  const [nodes, setNodes] = useState<Node[]>([]);
  const [edges, setEdges] = useState<Edge[]>([]);
  
  useEffect(() => {
    loadWorkflow(workflowId);
  }, [workflowId]);
  
  // 4. Event handlers
  const handleNodeAdd = (node: Node) => {
    setNodes((prev) => [...prev, node]);
  };
  
  const handleSave = () => {
    const spec = generateSpec(nodes, edges);
    onSave?.(spec);
  };
  
  // 5. Render
  return (
    <div className={cn('workflow-canvas', className)}>
      {/* Component JSX */}
    </div>
  );
};

// 6. Display name (for debugging)
WorkflowCanvas.displayName = 'WorkflowCanvas';
```

### 5.2 Props Patterns

**✅ DO**: Use proper prop patterns

```typescript
// ✅ CORRECT - Discriminated unions for variant props
interface ButtonBaseProps {
  children: React.ReactNode;
  onClick?: () => void;
  disabled?: boolean;
}

interface PrimaryButton extends ButtonBaseProps {
  variant: 'primary';
  icon?: never;
}

interface IconButton extends ButtonBaseProps {
  variant: 'icon';
  icon: React.ReactNode;
}

type ButtonProps = PrimaryButton | IconButton;

export function Button(props: ButtonProps) {
  if (props.variant === 'icon') {
    return <button>{props.icon}</button>; // TypeScript knows icon exists
  }
  
  return <button>{props.children}</button>;
}
```

### 5.3 Composition Patterns

**✅ DO**: Use composition over prop drilling

```typescript
// ✅ CORRECT - Compound component pattern
interface WorkflowBuilderContextValue {
  nodes: Node[];
  edges: Edge[];
  addNode: (node: Node) => void;
}

const WorkflowBuilderContext = createContext<WorkflowBuilderContextValue | null>(null);

export function WorkflowBuilder({ children }: { children: React.ReactNode }) {
  const [nodes, setNodes] = useState<Node[]>([]);
  const [edges, setEdges] = useState<Edge[]>([]);
  
  const addNode = (node: Node) => setNodes((prev) => [...prev, node]);
  
  return (
    <WorkflowBuilderContext.Provider value={{ nodes, edges, addNode }}>
      {children}
    </WorkflowBuilderContext.Provider>
  );
}

// Sub-components
WorkflowBuilder.Canvas = function Canvas() {
  const { nodes, edges } = useContext(WorkflowBuilderContext)!;
  return <ReactFlow nodes={nodes} edges={edges} />;
};

WorkflowBuilder.Palette = function Palette() {
  const { addNode } = useContext(WorkflowBuilderContext)!;
  return <div>{/* Palette UI */}</div>;
};

// Usage
<WorkflowBuilder>
  <WorkflowBuilder.Palette />
  <WorkflowBuilder.Canvas />
</WorkflowBuilder>
```

---

## 6. State Management

### 6.1 Zustand Store Pattern

**✅ DO**: Use Zustand with TypeScript

```typescript
// ✅ CORRECT - Zustand store
// lib/useWorkflowStore.ts
import { create } from 'zustand';
import { devtools, persist } from 'zustand/middleware';

interface WorkflowState {
  nodes: WorkflowNode[];
  edges: WorkflowEdge[];
  sources: Source[];
  
  // Actions
  setNodes: (nodes: WorkflowNode[]) => void;
  addNode: (node: WorkflowNode) => void;
  removeNode: (id: string) => void;
  updateNode: (id: string, updates: Partial<WorkflowNode>) => void;
  
  setEdges: (edges: WorkflowEdge[]) => void;
  addEdge: (edge: WorkflowEdge) => void;
  
  // Computed/Selectors
  getNodeById: (id: string) => WorkflowNode | undefined;
  generateSpec: () => WorkflowSpec;
  
  // Utils
  clear: () => void;
}

export const useWorkflowStore = create<WorkflowState>()(
  devtools(
    persist(
      (set, get) => ({
        nodes: [],
        edges: [],
        sources: [],
        
        setNodes: (nodes) => set({ nodes }),
        
        addNode: (node) => set((state) => ({
          nodes: [...state.nodes, node]
        })),
        
        removeNode: (id) => set((state) => ({
          nodes: state.nodes.filter((n) => n.id !== id),
          edges: state.edges.filter((e) => 
            e.source !== id && e.target !== id
          )
        })),
        
        updateNode: (id, updates) => set((state) => ({
          nodes: state.nodes.map((n) => 
            n.id === id ? { ...n, ...updates } : n
          )
        })),
        
        setEdges: (edges) => set({ edges }),
        
        addEdge: (edge) => set((state) => ({
          edges: [...state.edges, edge]
        })),
        
        getNodeById: (id) => {
          return get().nodes.find((n) => n.id === id);
        },
        
        generateSpec: () => {
          const state = get();
          return {
            nodes: state.nodes,
            edges: state.edges,
            sources: state.sources,
            queues: [],
            start_node: state.nodes[0]?.id || ''
          };
        },
        
        clear: () => set({
          nodes: [],
          edges: [],
          sources: []
        })
      }),
      { name: 'workflow-store' }
    )
  )
);
```

---

## 7. Performance Optimization

### 7.1 Memoization

**✅ DO**: Memoize expensive computations

```typescript
// ✅ CORRECT - Proper memoization
'use client';

import { useMemo, useCallback } from 'react';

export function WorkflowAnalytics({ workflow }: Props) {
  // Memoize expensive calculation
  const statistics = useMemo(() => {
    return {
      nodeCount: workflow.nodes.length,
      edgeCount: workflow.edges.length,
      complexity: calculateComplexity(workflow),
      estimatedCost: estimateCost(workflow)
    };
  }, [workflow]);
  
  // Memoize callback
  const handleExport = useCallback(() => {
    const data = JSON.stringify(workflow, null, 2);
    downloadFile(data, 'workflow.json');
  }, [workflow]);
  
  return (
    <div>
      <StatCard label="Nodes" value={statistics.nodeCount} />
      <button onClick={handleExport}>Export</button>
    </div>
  );
}
```

### 7.2 Code Splitting

**✅ DO**: Use dynamic imports for code splitting

```typescript
// ✅ CORRECT - Dynamic import
import dynamic from 'next/dynamic';

const WorkflowCanvas = dynamic(
  () => import('@/components/workflow/WorkflowCanvas'),
  {
    loading: () => <CanvasSkeleton />,
    ssr: false // Disable SSR for client-only components
  }
);

export default function DesignerPage() {
  return (
    <div>
      <WorkflowCanvas />
    </div>
  );
}
```

### 7.3 Image Optimization

**✅ DO**: Use Next.js Image component

```typescript
// ✅ CORRECT - Optimized images
import Image from 'next/image';

export function WorkflowThumbnail({ url, alt }: Props) {
  return (
    <Image
      src={url}
      alt={alt}
      width={300}
      height={200}
      quality={85}
      placeholder="blur"
      blurDataURL="data:image/jpeg;base64,..."
    />
  );
}
```

---

## 8. Code Style & Formatting

### 8.1 ESLint Configuration

**✅ DO**: Use strict ESLint rules

```javascript
// eslint.config.mjs
import { FlatCompat } from '@eslint/eslintrc';

const compat = new FlatCompat();

export default [
  ...compat.extends('next/core-web-vitals', 'next/typescript'),
  {
    rules: {
      '@typescript-eslint/no-explicit-any': 'error',
      '@typescript-eslint/no-unused-vars': 'error',
      'react/jsx-key': 'error',
      'react-hooks/rules-of-hooks': 'error',
      'react-hooks/exhaustive-deps': 'warn',
      'no-console': ['warn', { allow: ['warn', 'error'] }],
    }
  }
];
```

### 8.2 Prettier Configuration

**✅ DO**: Use Prettier for consistent formatting

```json
{
  "semi": true,
  "trailingComma": "es5",
  "singleQuote": true,
  "printWidth": 100,
  "tabWidth": 2,
  "useTabs": false,
  "arrowParens": "always",
  "endOfLine": "lf"
}
```

---

## 9. Testing Standards

### 9.1 Unit Testing with Jest

**✅ DO**: Write comprehensive unit tests

```typescript
// ✅ CORRECT - Component test
import { render, screen, fireEvent } from '@testing-library/react';
import { WorkflowCanvas } from './WorkflowCanvas';

describe('WorkflowCanvas', () => {
  it('renders nodes correctly', () => {
    const nodes = [
      { id: '1', type: 'input', position: { x: 0, y: 0 }, data: {} }
    ];
    
    render(<WorkflowCanvas nodes={nodes} edges={[]} />);
    
    expect(screen.getByTestId('node-1')).toBeInTheDocument();
  });
  
  it('adds node on palette click', () => {
    const onNodeAdd = jest.fn();
    
    render(<WorkflowCanvas nodes={[]} edges={[]} onNodeAdd={onNodeAdd} />);
    
    fireEvent.click(screen.getByText('Add LLM Node'));
    
    expect(onNodeAdd).toHaveBeenCalledWith(
      expect.objectContaining({ type: 'llm' })
    );
  });
});
```

---

## 10. Accessibility (a11y)

### 10.1 Semantic HTML

**✅ DO**: Use semantic HTML elements

```typescript
// ✅ CORRECT - Semantic HTML
export function WorkflowList({ workflows }: Props) {
  return (
    <section aria-labelledby="workflows-heading">
      <h2 id="workflows-heading">Your Workflows</h2>
      <ul role="list">
        {workflows.map((wf) => (
          <li key={wf.id}>
            <article>
              <h3>{wf.name}</h3>
              <p>{wf.description}</p>
            </article>
          </li>
        ))}
      </ul>
    </section>
  );
}
```

### 10.2 ARIA Attributes

**✅ DO**: Add ARIA attributes for accessibility

```typescript
// ✅ CORRECT - ARIA attributes
export function WorkflowCanvas() {
  return (
    <div
      role="application"
      aria-label="Workflow designer canvas"
      aria-describedby="canvas-instructions"
    >
      <div id="canvas-instructions" className="sr-only">
        Use arrow keys to navigate, Enter to select, Delete to remove nodes
      </div>
      {/* Canvas content */}
    </div>
  );
}
```

---

## Quick Reference

### Common Patterns

```typescript
// Server Component (async)
export default async function Page() {
  const data = await fetchData();
  return <Component data={data} />;
}

// Client Component
'use client';
export function Component() {
  const [state, setState] = useState();
  return <div />;
}

// Server Action
'use server';
export async function action(formData: FormData) {
  // mutation logic
  revalidatePath('/path');
}

// Dynamic Route
// app/workflows/[id]/page.tsx
export default function Page({ params }: { params: { id: string } }) {
  return <div>{params.id}</div>;
}
```

---

**Document Version**: 1.0.0  
**Last Updated**: December 7, 2025  
**Maintained by**: AgentFlow Frontend Team
