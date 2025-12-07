# Implementation Guide

# AgentFlow Implementation Guide v1.0

**Version:** 1.0.0  
**Date:** December 7, 2025  
**Status:** Approved  
**Audience:** Backend Engineers, Frontend Engineers, DevOps Engineers

---

## Table of Contents

1. [Development environment setup](#1-development-environment-setup)
2. [Backend implementation](#2-backend-implementation)
3. [Frontend implementation](#3-frontend-implementation)
4. [Database setup](#4-database-setup)
5. [Testing setup](#5-testing-setup)
6. [Deployment guide](#6-deployment-guide)
7. [Troubleshooting](#7-troubleshooting)

---

## 1. Development environment setup

### 1.1 Prerequisites

| Tool | Version | Purpose |
|------|---------|---------|
| Python | 3.11+ | Backend runtime |
| Node.js | 20+ | Frontend runtime |
| pnpm | 8+ | Frontend package manager |
| PostgreSQL | 14+ | Database |
| Redis | 7+ | Cache/rate limiting |
| Docker | 24+ | Containerization |
| Git | 2.40+ | Version control |

### 1.2 Clone repository

```bash
# Clone the repository
git clone https://github.com/your-org/agentflow.git
cd agentflow

# Verify structure
ls -la
# Expected: backend/, frontend/, docs/, scripts/, shared/
```

### 1.3 Install system dependencies

**macOS:**
```bash
# Install Homebrew
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Install dependencies
brew install python@3.11 node postgresql redis docker git

# Start services
brew services start postgresql
brew services start redis
```

**Ubuntu/Debian:**
```bash
# Update package list
sudo apt update

# Install dependencies
sudo apt install -y python3.11 python3.11-venv python3-pip nodejs npm postgresql redis-server docker.io git

# Start services
sudo systemctl start postgresql
sudo systemctl start redis-server
```

### 1.4 Environment variables

Create `.env` file in project root:

```bash
# Backend configuration
DATABASE_URL=postgresql://postgres:password@localhost:5432/agentflow
REDIS_URL=redis://localhost:6379
OPENAI_API_KEY=sk-...

# Frontend configuration
NEXT_PUBLIC_CORE_URL=http://localhost:8000

# Development
DEBUG=true
LOG_LEVEL=debug
```

---

## 2. Backend implementation

### 2.1 Setup Python environment

```bash
cd backend

# Create virtual environment
python3.11 -m venv venv

# Activate virtual environment
source venv/bin/activate  # macOS/Linux
# OR
venv\Scripts\activate     # Windows

# Upgrade pip
pip install --upgrade pip

# Install dependencies
pip install -r requirements.txt

# Verify installation
python -c "import fastapi; import langgraph; print('Dependencies installed')"
```

### 2.2 Project structure setup

```bash
cd agentflow_core

# Create __init__.py files (if missing)
touch __init__.py
touch api/__init__.py
touch api/models/__init__.py
touch api/routes/__init__.py
touch runtime/__init__.py
touch nodes/__init__.py
touch sources/__init__.py
touch utils/__init__.py

# Verify structure
tree -L 3
```

### 2.3 Implement core modules

#### 2.3.1 State definition

**File:** `runtime/state.py`

```python
from typing import TypedDict, Any, Optional

class GraphState(TypedDict, total=False):
    """State object passed between nodes during workflow execution."""
    user_input: str
    intent: str
    text_result: Optional[str]
    image_result: Optional[Any]
    db_result: Optional[Any]
    final_output: Optional[Any]
    tokens_used: int
    cost: float
    execution_time: float
    metadata: dict
    errors: list
```

#### 2.3.2 Pydantic models

**File:** `api/models/workflow_model.py`

```python
from pydantic import BaseModel, Field
from typing import List, Optional, Any, Dict, Union

class NodeModel(BaseModel):
    id: str
    type: str
    metadata: Optional[Dict[str, Any]] = None

class EdgeModel(BaseModel):
    from_node: str = Field(..., alias="from")
    to: Union[str, List[str]]
    condition: Optional[str] = None

class BandwidthModel(BaseModel):
    max_messages_per_second: Optional[int] = None
    max_requests_per_minute: Optional[int] = None
    max_tokens_per_minute: Optional[int] = None

class QueueModel(BaseModel):
    id: str
    from_node: str = Field(..., alias="from")
    to: str
    bandwidth: Optional[BandwidthModel] = None

class SourceModel(BaseModel):
    id: str
    kind: str
    config: Dict[str, Any]

class WorkflowSpecModel(BaseModel):
    nodes: List[NodeModel]
    edges: List[EdgeModel]
    queues: List[QueueModel] = Field(default_factory=list)
    sources: List[SourceModel]
    start_node: str
    
    class Config:
        populate_by_name = True
```

#### 2.3.3 Validator implementation

**File:** `runtime/validator.py`

```python
from typing import List
from agentflow_core.api.models.workflow_model import WorkflowSpecModel, ValidationError

def validate_workflow(spec: WorkflowSpecModel) -> List[ValidationError]:
    """Validates a workflow specification."""
    errors = []
    
    node_ids = {node.id for node in spec.nodes}
    
    # Validate start node
    if spec.start_node not in node_ids:
        errors.append(ValidationError(
            code="E005",
            message=f"Start node '{spec.start_node}' does not exist",
            field="start_node"
        ))
    
    # Validate edges
    for edge in spec.edges:
        if edge.from_node not in node_ids:
            errors.append(ValidationError(
                code="E006",
                message=f"Edge references non-existent source node '{edge.from_node}'",
                field="edges"
            ))
        
        to_nodes = edge.to if isinstance(edge.to, list) else [edge.to]
        for to_node in to_nodes:
            if to_node not in node_ids:
                errors.append(ValidationError(
                    code="E006",
                    message=f"Edge references non-existent destination node '{to_node}'",
                    field="edges"
                ))
    
    return errors
```

#### 2.3.4 Node implementations

**File:** `nodes/llm_node.py`

```python
from agentflow_core.runtime.state import GraphState
from agentflow_core.runtime.registry import registry
from agentflow_core.sources.llm_openai import get_llm_client

def create_llm_node(node_id: str, metadata: dict):
    """Creates an LLM node that calls a language model."""
    
    def llm_node(state: GraphState) -> GraphState:
        source_id = metadata.get('source')
        if not source_id:
            raise ValueError(f"LLM node '{node_id}' missing source")
        
        source = registry.get_source(source_id)
        llm_client = get_llm_client(source)
        
        user_input = state.get('user_input', '')
        prompt = metadata.get('prompt', user_input)
        
        response = llm_client.chat.completions.create(
            model=source.config.get('model_name', 'gpt-4'),
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": prompt}
            ]
        )
        
        state['text_result'] = response.choices[0].message.content
        state['tokens_used'] = state.get('tokens_used', 0) + response.usage.total_tokens
        
        return state
    
    return llm_node
```

### 2.4 Run backend server

```bash
cd backend

# Activate virtual environment
source venv/bin/activate

# Run development server
uvicorn agentflow_core.api.main:app --reload --host 0.0.0.0 --port 8000

# Verify server is running
curl http://localhost:8000/health
# Expected: {"status": "ok", "version": "1.0.0", "uptime": 0.123}
```

### 2.5 Test backend API

```bash
# Test validation endpoint
curl -X POST http://localhost:8000/workflows/validate \
  -H "Content-Type: application/json" \
  -d '{
    "nodes": [{"id": "input", "type": "input"}],
    "edges": [],
    "queues": [],
    "sources": [],
    "start_node": "input"
  }'

# Expected: {"valid": true, "errors": []}
```

---

## 3. Frontend implementation

### 3.1 Setup Node.js environment

```bash
cd frontend/agentflow-studio

# Install pnpm (if not already installed)
npm install -g pnpm

# Install dependencies
pnpm install

# Verify installation
pnpm list
```

### 3.2 Project structure setup

```bash
# Verify structure
tree -L 2 app components lib

# Expected:
# app/
#   ├── layout.tsx
#   ├── page.tsx
#   ├── globals.css
#   └── designer/
# components/
# lib/
```

### 3.3 Implement core components

#### 3.3.1 Workflow store

**File:** `lib/useWorkflowStore.ts`

```typescript
'use client';

import { create } from 'zustand';

export interface WorkflowNode {
  id: string;
  type: string;
  position: { x: number; y: number };
  data: any;
}

export interface WorkflowEdge {
  id: string;
  source: string;
  target: string;
}

interface WorkflowState {
  nodes: WorkflowNode[];
  edges: WorkflowEdge[];
  sources: any[];
  
  setNodes: (nodes: WorkflowNode[]) => void;
  setEdges: (edges: WorkflowEdge[]) => void;
  
  addNode: (node: WorkflowNode) => void;
  removeNode: (id: string) => void;
  
  generateSpec: () => any;
  clear: () => void;
}

export const useWorkflowStore = create<WorkflowState>((set, get) => ({
  nodes: [],
  edges: [],
  sources: [],
  
  setNodes: (nodes) => set({ nodes }),
  setEdges: (edges) => set({ edges }),
  
  addNode: (node) => set((state) => ({
    nodes: [...state.nodes, node]
  })),
  
  removeNode: (id) => set((state) => ({
    nodes: state.nodes.filter((n) => n.id !== id),
    edges: state.edges.filter((e) => e.source !== id && e.target !== id)
  })),
  
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
        to: e.target
      })),
      queues: [],
      sources: state.sources,
      start_node: state.nodes[0]?.id || 'input'
    };
  },
  
  clear: () => set({
    nodes: [],
    edges: [],
    sources: []
  })
}));
```

#### 3.3.2 API client

**File:** `lib/api.ts`

```typescript
const CORE_URL = process.env.NEXT_PUBLIC_CORE_URL || 'http://localhost:8000';

export const api = {
  validateWorkflow: async (spec: any) => {
    const response = await fetch(`${CORE_URL}/workflows/validate`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(spec)
    });
    
    if (!response.ok) {
      throw new Error('Validation failed');
    }
    
    return response.json();
  },
  
  executeWorkflow: async (spec: any, initialState: any) => {
    const response = await fetch(`${CORE_URL}/workflows/execute`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        workflow: spec,
        initial_state: initialState
      })
    });
    
    if (!response.ok) {
      throw new Error('Execution failed');
    }
    
    return response.json();
  }
};
```

#### 3.3.3 Workflow canvas

**File:** `components/WorkflowCanvas.tsx`

```typescript
'use client';

import { useCallback } from 'react';
import ReactFlow, {
  Node,
  Edge,
  addEdge,
  Connection,
  useNodesState,
  useEdgesState,
} from 'reactflow';
import 'reactflow/dist/style.css';
import { useWorkflowStore } from '@/lib/useWorkflowStore';

export function WorkflowCanvas() {
  const { nodes, edges, setNodes, setEdges } = useWorkflowStore();
  
  const [rfNodes, setRfNodes, onNodesChange] = useNodesState(nodes);
  const [rfEdges, setRfEdges, onEdgesChange] = useEdgesState(edges);
  
  const onConnect = useCallback(
    (params: Connection) => {
      const newEdges = addEdge(params, rfEdges);
      setRfEdges(newEdges);
      setEdges(newEdges);
    },
    [rfEdges, setRfEdges, setEdges]
  );
  
  return (
    <div className="w-full h-full">
      <ReactFlow
        nodes={rfNodes}
        edges={rfEdges}
        onNodesChange={onNodesChange}
        onEdgesChange={onEdgesChange}
        onConnect={onConnect}
        fitView
      />
    </div>
  );
}
```

### 3.4 Run frontend development server

```bash
cd frontend/agentflow-studio

# Start development server
pnpm dev

# Server will start on http://localhost:3000
```

### 3.5 Verify frontend

Open browser: `http://localhost:3000`

Expected: AgentFlow Studio UI loads with workflow canvas

---

## 4. Database setup

### 4.1 Initialize PostgreSQL

```bash
# Start PostgreSQL
brew services start postgresql  # macOS
# OR
sudo systemctl start postgresql # Linux

# Create database
createdb agentflow

# Verify connection
psql -d agentflow -c "SELECT version();"
```

### 4.2 Setup Alembic migrations

```bash
cd backend

# Activate virtual environment
source venv/bin/activate

# Install Alembic
pip install alembic

# Initialize Alembic
alembic init migrations

# Configure alembic.ini
# Edit: sqlalchemy.url = postgresql://postgres:password@localhost:5432/agentflow
```

### 4.3 Create initial migration

**File:** `migrations/versions/001_initial_schema.py`

```python
"""Initial schema

Revision ID: 001
Revises: 
Create Date: 2025-12-07 10:00:00.000000
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID, JSONB

revision = '001'
down_revision = None

def upgrade():
    op.create_table(
        'users',
        sa.Column('id', UUID(as_uuid=True), primary_key=True),
        sa.Column('email', sa.String(255), nullable=False, unique=True),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('created_at', sa.TIMESTAMP(timezone=True), nullable=False),
    )
    
    op.create_table(
        'workflows',
        sa.Column('id', UUID(as_uuid=True), primary_key=True),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('spec', JSONB, nullable=False),
        sa.Column('user_id', UUID(as_uuid=True), nullable=False),
        sa.Column('created_at', sa.TIMESTAMP(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id']),
    )

def downgrade():
    op.drop_table('workflows')
    op.drop_table('users')
```

### 4.4 Run migrations

```bash
# Apply migrations
alembic upgrade head

# Verify tables created
psql -d agentflow -c "\dt"

# Expected output:
#  public | users      | table | postgres
#  public | workflows  | table | postgres
```

---

## 5. Testing setup

### 5.1 Backend testing

```bash
cd backend

# Install test dependencies
pip install pytest pytest-asyncio pytest-cov httpx

# Create test structure
mkdir -p tests
touch tests/__init__.py
touch tests/test_api.py
touch tests/test_validator.py
```

**File:** `tests/test_validator.py`

```python
import pytest
from agentflow_core.api.models.workflow_model import WorkflowSpecModel
from agentflow_core.runtime.validator import validate_workflow

def test_validate_valid_workflow():
    spec = WorkflowSpecModel(
        nodes=[{"id": "input", "type": "input"}],
        edges=[],
        queues=[],
        sources=[],
        start_node="input"
    )
    
    errors = validate_workflow(spec)
    assert len(errors) == 0

def test_validate_missing_start_node():
    spec = WorkflowSpecModel(
        nodes=[{"id": "input", "type": "input"}],
        edges=[],
        queues=[],
        sources=[],
        start_node="nonexistent"
    )
    
    errors = validate_workflow(spec)
    assert len(errors) > 0
    assert any(e.code == "E005" for e in errors)
```

### 5.2 Run backend tests

```bash
cd backend

# Run all tests
pytest

# Run with coverage
pytest --cov=agentflow_core --cov-report=html

# View coverage report
open htmlcov/index.html
```

### 5.3 Frontend testing

```bash
cd frontend/agentflow-studio

# Install test dependencies
pnpm add -D @testing-library/react @testing-library/jest-dom jest

# Create test file
mkdir -p __tests__
```

**File:** `__tests__/useWorkflowStore.test.ts`

```typescript
import { renderHook, act } from '@testing-library/react';
import { useWorkflowStore } from '@/lib/useWorkflowStore';

describe('useWorkflowStore', () => {
  it('should add a node', () => {
    const { result } = renderHook(() => useWorkflowStore());
    
    act(() => {
      result.current.addNode({
        id: 'test-node',
        type: 'llm',
        position: { x: 0, y: 0 },
        data: {}
      });
    });
    
    expect(result.current.nodes).toHaveLength(1);
    expect(result.current.nodes[0].id).toBe('test-node');
  });
});
```

### 5.4 Run frontend tests

```bash
cd frontend/agentflow-studio

# Run tests
pnpm test

# Run with coverage
pnpm test --coverage
```

---

## 6. Deployment guide

### 6.1 Docker deployment

**File:** `docker-compose.yml`

```yaml
version: '3.8'

services:
  postgres:
    image: postgres:14
    environment:
      POSTGRES_DB: agentflow
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: password
    volumes:
      - pgdata:/var/lib/postgresql/data
    ports:
      - "5432:5432"
  
  redis:
    image: redis:7
    volumes:
      - redisdata:/data
    ports:
      - "6379:6379"
  
  core:
    build:
      context: ./backend
      dockerfile: Dockerfile
    environment:
      DATABASE_URL: postgresql://postgres:password@postgres:5432/agentflow
      REDIS_URL: redis://redis:6379
      OPENAI_API_KEY: ${OPENAI_API_KEY}
    depends_on:
      - postgres
      - redis
    ports:
      - "8000:8000"
  
  studio:
    build:
      context: ./frontend/agentflow-studio
      dockerfile: Dockerfile
    environment:
      NEXT_PUBLIC_CORE_URL: http://core:8000
    depends_on:
      - core
    ports:
      - "3000:3000"

volumes:
  pgdata:
  redisdata:
```

### 6.2 Build and run containers

```bash
# Build images
docker-compose build

# Start services
docker-compose up -d

# Verify services
docker-compose ps

# View logs
docker-compose logs -f core
docker-compose logs -f studio
```

### 6.3 Kubernetes deployment

**File:** `k8s/deployment.yaml`

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: agentflow-core
spec:
  replicas: 3
  selector:
    matchLabels:
      app: agentflow-core
  template:
    metadata:
      labels:
        app: agentflow-core
    spec:
      containers:
      - name: core
        image: agentflow-core:latest
        ports:
        - containerPort: 8000
        env:
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: agentflow-secrets
              key: database-url
        - name: REDIS_URL
          value: redis://redis-service:6379
        - name: OPENAI_API_KEY
          valueFrom:
            secretKeyRef:
              name: agentflow-secrets
              key: openai-api-key
        resources:
          requests:
            memory: "512Mi"
            cpu: "500m"
          limits:
            memory: "2Gi"
            cpu: "2000m"
        livenessProbe:
          httpGet:
            path: /health/live
            port: 8000
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /health/ready
            port: 8000
          initialDelaySeconds: 10
          periodSeconds: 5
```

### 6.4 Deploy to Kubernetes

```bash
# Apply configurations
kubectl apply -f k8s/

# Verify deployment
kubectl get pods
kubectl get services

# View logs
kubectl logs -f deployment/agentflow-core
```

---

## 7. Troubleshooting

### 7.1 Backend issues

| Issue | Solution |
|-------|----------|
| Module not found | `pip install -r requirements.txt` |
| Database connection error | Check DATABASE_URL, verify PostgreSQL is running |
| Port already in use | Change port or kill process: `lsof -ti:8000 \| xargs kill -9` |
| Import errors | Ensure `__init__.py` files exist in all packages |

### 7.2 Frontend issues

| Issue | Solution |
|-------|----------|
| Dependencies error | `pnpm install` or `rm -rf node_modules && pnpm install` |
| CORS errors | Add backend URL to CORS allow list |
| Build errors | Check Node.js version: `node --version` (should be 20+) |
| Type errors | Run `pnpm tsc --noEmit` to check TypeScript errors |

### 7.3 Database issues

| Issue | Solution |
|-------|----------|
| Connection refused | `brew services start postgresql` or `sudo systemctl start postgresql` |
| Authentication failed | Check credentials in DATABASE_URL |
| Migration errors | Run `alembic downgrade base` then `alembic upgrade head` |
| Table not found | Verify migrations applied: `alembic current` |

### 7.4 Docker issues

| Issue | Solution |
|-------|----------|
| Image build fails | Check Dockerfile syntax, verify base image exists |
| Container won't start | Check logs: `docker logs <container-id>` |
| Port conflicts | Change port mapping in docker-compose.yml |
| Volume permission errors | Use named volumes or fix permissions |

---

**Document Approval**

| Role | Name | Date | Signature |
|------|------|------|-----------|
| Lead Engineer | _______________ | _______________ | _______________ |
| DevOps Engineer | _______________ | _______________ | _______________ |
| QA Lead | _______________ | _______________ | _______________ |
