```prompt
---
description: Write comprehensive tests for AgentFlow backend (pytest) and frontend (React Testing Library)
tools:
  - create_file
  - read_file
  - semantic_search
  - list_code_usages
  - runTests
---

# Write Tests for AgentFlow

You are a testing expert for Python (pytest) and React (React Testing Library/Jest). Write comprehensive, maintainable tests for AgentFlow following best practices.

## AgentFlow Architecture Context

AgentFlow is a visual workflow orchestration platform with:
- **Backend**: Python 3.11+, FastAPI, LangGraph, Pydantic, PostgreSQL, Redis
- **Frontend**: Next.js 16, React 19, React Flow v12, ShadCN UI, TailwindCSS, Zustand
- **Core Concepts**: Nodes (input, router, llm, image, db, aggregator), Edges, Queues, Sources
- **Workflow Structure**: WorkflowSpec with nodes[], edges[], queues[], sources[], start_node

## Backend Testing (Python + pytest)

### Test Structure

```
backend/tests/
├── __init__.py
├── conftest.py              # Shared fixtures
├── test_api.py              # API route tests
├── test_builder.py          # WorkflowBuilder tests
├── test_executor.py         # WorkflowExecutor tests
├── test_validator.py        # WorkflowValidator tests
└── integration/
    ├── test_workflows.py    # End-to-end workflow tests
    └── test_sources.py      # Source integration tests
```

### pytest Configuration

```toml
# pyproject.toml
[tool.pytest.ini_options]
testpaths = ["tests"]
python_files = ["test_*.py"]
python_classes = ["Test*"]
python_functions = ["test_*"]
addopts = [
    "-v",
    "--cov=agentflow_core",
    "--cov-report=term-missing",
    "--cov-report=html",
    "--asyncio-mode=auto"
]
asyncio_mode = "auto"
```

### Common Fixtures

```python
# tests/conftest.py
import pytest
from fastapi.testclient import TestClient
from agentflow_core.api.main import app
from agentflow_core.runtime.state import GraphState


@pytest.fixture
def client():
    """Test client for API routes."""
    return TestClient(app)


@pytest.fixture
def sample_workflow_spec():
    """Sample workflow specification for testing."""
    return {
        "version": "1.0",
        "name": "test_workflow",
        "description": "Test workflow",
        "start_node": "input_node",
        "nodes": [
            {
                "id": "input_node",
                "type": "input",
                "config": {"prompt": "Enter text"}
            },
            {
                "id": "llm_node",
                "type": "llm",
                "config": {
                    "source_ref": "openai_source",
                    "model": "gpt-4",
                    "temperature": 0.7
                }
            },
            {
                "id": "output_node",
                "type": "aggregator",
                "config": {"strategy": "concat"}
            }
        ],
        "edges": [
            {"source": "input_node", "target": "llm_node"},
            {"source": "llm_node", "target": "output_node"}
        ],
        "sources": [
            {
                "id": "openai_source",
                "type": "llm_openai",
                "config": {"api_key_env": "OPENAI_API_KEY"}
            }
        ],
        "queues": []
    }


@pytest.fixture
def sample_graph_state():
    """Sample graph state for node testing."""
    return GraphState(
        input_data={"text": "Hello, world!"},
        node_outputs={},
        current_node="input_node",
        execution_path=[],
        errors=[]
    )


@pytest.fixture
def mock_llm_response(mocker):
    """Mock LLM API response."""
    mock = mocker.patch("agentflow_core.sources.llm_openai.OpenAILLM.invoke")
    mock.return_value = {"content": "Mock LLM response", "tokens": 100}
    return mock
```

### API Route Tests

```python
# tests/test_api.py
import pytest
from fastapi import status


class TestHealthAPI:
    """Test health check endpoints."""
    
    def test_health_check(self, client):
        """Test health endpoint returns OK."""
        response = client.get("/health")
        
        assert response.status_code == status.HTTP_200_OK
        assert response.json()["status"] == "healthy"
    
    def test_readiness_check(self, client):
        """Test readiness endpoint."""
        response = client.get("/health/ready")
        
        assert response.status_code == status.HTTP_200_OK


class TestWorkflowsAPI:
    """Test workflow management endpoints."""
    
    def test_create_workflow(self, client, sample_workflow_spec):
        """Test creating a new workflow."""
        response = client.post(
            "/workflows",
            json=sample_workflow_spec
        )
        
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert "id" in data
        assert data["name"] == "test_workflow"
    
    def test_create_workflow_invalid_spec(self, client):
        """Test creating workflow with invalid spec returns 422."""
        response = client.post(
            "/workflows",
            json={"name": "invalid"}  # Missing required fields
        )
        
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    
    def test_list_workflows(self, client):
        """Test listing all workflows."""
        response = client.get("/workflows")
        
        assert response.status_code == status.HTTP_200_OK
        assert isinstance(response.json(), list)
    
    def test_get_workflow_not_found(self, client):
        """Test getting non-existent workflow returns 404."""
        response = client.get("/workflows/nonexistent_id")
        
        assert response.status_code == status.HTTP_404_NOT_FOUND
    
    def test_execute_workflow(self, client, sample_workflow_spec, mock_llm_response):
        """Test executing a workflow."""
        # Create workflow first
        create_response = client.post("/workflows", json=sample_workflow_spec)
        workflow_id = create_response.json()["id"]
        
        # Execute workflow
        response = client.post(
            f"/workflows/{workflow_id}/execute",
            json={"input_data": {"text": "Test input"}}
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "execution_id" in data
        assert data["status"] in ["completed", "running"]


class TestSourcesAPI:
    """Test source management endpoints."""
    
    def test_create_source(self, client):
        """Test creating a new source."""
        response = client.post(
            "/sources",
            json={
                "name": "test_llm",
                "type": "llm_openai",
                "config": {"api_key_env": "OPENAI_API_KEY"}
            }
        )
        
        assert response.status_code == status.HTTP_201_CREATED
        assert response.json()["type"] == "llm_openai"
    
    def test_list_sources(self, client):
        """Test listing all sources."""
        response = client.get("/sources")
        
        assert response.status_code == status.HTTP_200_OK
```

### Runtime Tests

```python
# tests/test_builder.py
import pytest
from agentflow_core.runtime.builder import WorkflowBuilder
from agentflow_core.runtime.validator import WorkflowValidator


class TestWorkflowBuilder:
    """Test workflow graph building."""
    
    def test_build_simple_workflow(self, sample_workflow_spec):
        """Test building a simple linear workflow."""
        builder = WorkflowBuilder(sample_workflow_spec)
        graph = builder.build()
        
        assert graph is not None
        assert len(builder.nodes) == 3
    
    def test_build_workflow_with_router(self):
        """Test building workflow with conditional routing."""
        spec = {
            "version": "1.0",
            "name": "router_workflow",
            "start_node": "input",
            "nodes": [
                {"id": "input", "type": "input", "config": {}},
                {"id": "router", "type": "router", "config": {
                    "conditions": [
                        {"when": "input.type == 'a'", "then": "branch_a"},
                        {"when": "input.type == 'b'", "then": "branch_b"}
                    ],
                    "default": "branch_a"
                }},
                {"id": "branch_a", "type": "llm", "config": {}},
                {"id": "branch_b", "type": "llm", "config": {}}
            ],
            "edges": [
                {"source": "input", "target": "router"},
                {"source": "router", "target": "branch_a"},
                {"source": "router", "target": "branch_b"}
            ],
            "sources": [],
            "queues": []
        }
        
        builder = WorkflowBuilder(spec)
        graph = builder.build()
        
        assert graph is not None
        assert "router" in builder.nodes
    
    def test_build_invalid_workflow_raises(self):
        """Test that invalid workflow spec raises validation error."""
        invalid_spec = {
            "version": "1.0",
            "name": "invalid",
            "nodes": [],  # No nodes
            "edges": []
        }
        
        with pytest.raises(ValueError):
            builder = WorkflowBuilder(invalid_spec)
            builder.build()


class TestWorkflowValidator:
    """Test workflow validation."""
    
    def test_validate_valid_workflow(self, sample_workflow_spec):
        """Test validating a correct workflow."""
        validator = WorkflowValidator()
        result = validator.validate(sample_workflow_spec)
        
        assert result.is_valid
        assert len(result.errors) == 0
    
    def test_validate_missing_start_node(self, sample_workflow_spec):
        """Test validation catches missing start node."""
        sample_workflow_spec["start_node"] = "nonexistent"
        
        validator = WorkflowValidator()
        result = validator.validate(sample_workflow_spec)
        
        assert not result.is_valid
        assert any("start_node" in err for err in result.errors)
    
    def test_validate_orphan_nodes(self):
        """Test validation catches orphan nodes."""
        spec = {
            "version": "1.0",
            "name": "orphan",
            "start_node": "input",
            "nodes": [
                {"id": "input", "type": "input", "config": {}},
                {"id": "orphan", "type": "llm", "config": {}}  # Not connected
            ],
            "edges": [],
            "sources": [],
            "queues": []
        }
        
        validator = WorkflowValidator()
        result = validator.validate(spec)
        
        assert not result.is_valid
        assert any("orphan" in err for err in result.errors)
    
    def test_validate_cycle_detection(self):
        """Test validation detects cycles."""
        spec = {
            "version": "1.0",
            "name": "cyclic",
            "start_node": "a",
            "nodes": [
                {"id": "a", "type": "input", "config": {}},
                {"id": "b", "type": "llm", "config": {}},
                {"id": "c", "type": "llm", "config": {}}
            ],
            "edges": [
                {"source": "a", "target": "b"},
                {"source": "b", "target": "c"},
                {"source": "c", "target": "a"}  # Creates cycle
            ],
            "sources": [],
            "queues": []
        }
        
        validator = WorkflowValidator()
        result = validator.validate(spec)
        
        assert not result.is_valid
        assert any("cycle" in err.lower() for err in result.errors)
```

### Executor Tests

```python
# tests/test_executor.py
import pytest
from agentflow_core.runtime.executor import WorkflowExecutor
from agentflow_core.runtime.builder import WorkflowBuilder


class TestWorkflowExecutor:
    """Test workflow execution."""
    
    @pytest.mark.asyncio
    async def test_execute_simple_workflow(self, sample_workflow_spec, mock_llm_response):
        """Test executing a simple workflow."""
        builder = WorkflowBuilder(sample_workflow_spec)
        graph = builder.build()
        
        executor = WorkflowExecutor(graph)
        result = await executor.execute({"text": "Hello"})
        
        assert result is not None
        assert "output" in result
    
    @pytest.mark.asyncio
    async def test_execute_with_error_handling(self, sample_workflow_spec, mocker):
        """Test executor handles node errors gracefully."""
        # Mock node to raise error
        mocker.patch(
            "agentflow_core.nodes.llm_node.LLMNode.execute",
            side_effect=Exception("LLM API error")
        )
        
        builder = WorkflowBuilder(sample_workflow_spec)
        graph = builder.build()
        
        executor = WorkflowExecutor(graph)
        result = await executor.execute({"text": "Hello"})
        
        assert result["status"] == "error"
        assert "LLM API error" in result["error"]
    
    @pytest.mark.asyncio
    async def test_execution_state_tracking(self, sample_workflow_spec, mock_llm_response):
        """Test that execution path is tracked."""
        builder = WorkflowBuilder(sample_workflow_spec)
        graph = builder.build()
        
        executor = WorkflowExecutor(graph)
        result = await executor.execute({"text": "Hello"})
        
        assert "execution_path" in result
        assert len(result["execution_path"]) > 0
```

---

## Frontend Testing (React Testing Library)

### Test Structure

```
frontend/agentflow-studio/
├── __tests__/
│   ├── components/
│   │   ├── WorkflowCanvas.test.tsx
│   │   ├── NodePalette.test.tsx
│   │   ├── PropertiesPanel.test.tsx
│   │   └── QueueEditor.test.tsx
│   ├── lib/
│   │   ├── mappers.test.ts
│   │   └── schema.test.ts
│   └── pages/
│       ├── designer.test.tsx
│       └── sources.test.tsx
└── setupTests.ts
```

### Component Tests

```typescript
// __tests__/components/NodePalette.test.tsx
import { render, screen, fireEvent } from '@testing-library/react';
import { NodePalette } from '../../components/NodePalette';

describe('NodePalette', () => {
  it('renders all node types', () => {
    render(<NodePalette onDragStart={jest.fn()} />);
    
    expect(screen.getByText('Input')).toBeInTheDocument();
    expect(screen.getByText('LLM')).toBeInTheDocument();
    expect(screen.getByText('Router')).toBeInTheDocument();
    expect(screen.getByText('Image')).toBeInTheDocument();
    expect(screen.getByText('Database')).toBeInTheDocument();
    expect(screen.getByText('Aggregator')).toBeInTheDocument();
  });

  it('calls onDragStart with node type when dragged', () => {
    const mockOnDragStart = jest.fn();
    render(<NodePalette onDragStart={mockOnDragStart} />);
    
    const llmNode = screen.getByText('LLM');
    fireEvent.dragStart(llmNode);
    
    expect(mockOnDragStart).toHaveBeenCalledWith(
      expect.objectContaining({ nodeType: 'llm' })
    );
  });
});
```

```typescript
// __tests__/components/PropertiesPanel.test.tsx
import { render, screen, fireEvent } from '@testing-library/react';
import { PropertiesPanel } from '../../components/PropertiesPanel';

describe('PropertiesPanel', () => {
  const mockNode = {
    id: 'node_1',
    type: 'llm',
    data: {
      label: 'LLM Node',
      config: {
        source_ref: 'openai_source',
        model: 'gpt-4',
        temperature: 0.7
      }
    }
  };

  it('renders node properties when node selected', () => {
    render(<PropertiesPanel selectedNode={mockNode} onChange={jest.fn()} />);
    
    expect(screen.getByText('Node Properties')).toBeInTheDocument();
    expect(screen.getByLabelText('Model')).toHaveValue('gpt-4');
    expect(screen.getByLabelText('Temperature')).toHaveValue(0.7);
  });

  it('shows empty state when no node selected', () => {
    render(<PropertiesPanel selectedNode={null} onChange={jest.fn()} />);
    
    expect(screen.getByText('Select a node to view properties')).toBeInTheDocument();
  });

  it('calls onChange when property updated', () => {
    const mockOnChange = jest.fn();
    render(<PropertiesPanel selectedNode={mockNode} onChange={mockOnChange} />);
    
    const tempInput = screen.getByLabelText('Temperature');
    fireEvent.change(tempInput, { target: { value: '0.9' } });
    
    expect(mockOnChange).toHaveBeenCalledWith(
      expect.objectContaining({
        data: expect.objectContaining({
          config: expect.objectContaining({ temperature: 0.9 })
        })
      })
    );
  });
});
```

```typescript
// __tests__/components/WorkflowCanvas.test.tsx
import { render, screen, fireEvent } from '@testing-library/react';
import { ReactFlowProvider } from 'reactflow';
import { WorkflowCanvas } from '../../components/WorkflowCanvas';

describe('WorkflowCanvas', () => {
  const wrapper = ({ children }) => (
    <ReactFlowProvider>{children}</ReactFlowProvider>
  );

  it('renders empty canvas', () => {
    render(<WorkflowCanvas nodes={[]} edges={[]} />, { wrapper });
    
    expect(screen.getByTestId('workflow-canvas')).toBeInTheDocument();
  });

  it('renders nodes from props', () => {
    const nodes = [
      { id: 'node_1', type: 'input', position: { x: 0, y: 0 }, data: { label: 'Input' } },
      { id: 'node_2', type: 'llm', position: { x: 200, y: 0 }, data: { label: 'LLM' } }
    ];
    
    render(<WorkflowCanvas nodes={nodes} edges={[]} />, { wrapper });
    
    expect(screen.getByText('Input')).toBeInTheDocument();
    expect(screen.getByText('LLM')).toBeInTheDocument();
  });

  it('calls onNodeSelect when node clicked', () => {
    const mockOnNodeSelect = jest.fn();
    const nodes = [
      { id: 'node_1', type: 'input', position: { x: 0, y: 0 }, data: { label: 'Input' } }
    ];
    
    render(
      <WorkflowCanvas nodes={nodes} edges={[]} onNodeSelect={mockOnNodeSelect} />,
      { wrapper }
    );
    
    fireEvent.click(screen.getByText('Input'));
    
    expect(mockOnNodeSelect).toHaveBeenCalledWith(nodes[0]);
  });
});
```

### Library Tests

```typescript
// __tests__/lib/mappers.test.ts
import { workflowToReactFlow, reactFlowToWorkflow } from '../../lib/mappers';

describe('workflowToReactFlow', () => {
  it('converts workflow spec to React Flow format', () => {
    const workflow = {
      nodes: [
        { id: 'input_1', type: 'input', config: { prompt: 'Enter text' } },
        { id: 'llm_1', type: 'llm', config: { model: 'gpt-4' } }
      ],
      edges: [
        { source: 'input_1', target: 'llm_1' }
      ]
    };
    
    const { nodes, edges } = workflowToReactFlow(workflow);
    
    expect(nodes).toHaveLength(2);
    expect(nodes[0]).toMatchObject({
      id: 'input_1',
      type: 'input',
      data: expect.objectContaining({ config: { prompt: 'Enter text' } })
    });
    expect(edges).toHaveLength(1);
    expect(edges[0]).toMatchObject({
      source: 'input_1',
      target: 'llm_1'
    });
  });
});

describe('reactFlowToWorkflow', () => {
  it('converts React Flow format back to workflow spec', () => {
    const nodes = [
      { id: 'input_1', type: 'input', position: { x: 0, y: 0 }, data: { config: {} } }
    ];
    const edges = [
      { id: 'e1', source: 'input_1', target: 'llm_1' }
    ];
    
    const workflow = reactFlowToWorkflow(nodes, edges);
    
    expect(workflow.nodes).toHaveLength(1);
    expect(workflow.edges).toHaveLength(1);
  });
});
```

---

## Critical Testing Checklist

### Backend Tests
- [ ] Test workflow validation (schema compliance)
- [ ] Test node execution (each node type)
- [ ] Test edge routing (conditional and default)
- [ ] Test queue rate limiting
- [ ] Test source integration (mock external APIs)
- [ ] Test error handling and recovery
- [ ] Test API authentication and authorization
- [ ] Test validation errors (422 responses)

### Frontend Tests
- [ ] Test component rendering
- [ ] Test user interactions (drag-drop, clicks)
- [ ] Test workflow state management (Zustand)
- [ ] Test React Flow integration
- [ ] Test form validation
- [ ] Test API error states
- [ ] Mock API responses

### Integration Tests
- [ ] Test full workflow creation → execution flow
- [ ] Test source configuration and validation
- [ ] Test real-time execution updates
```
