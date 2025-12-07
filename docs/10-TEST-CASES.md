# Test Cases

# AgentFlow Test Cases v1.0

**Version:** 1.0.0  
**Date:** December 7, 2025  
**Status:** Approved  
**Audience:** QA Engineers, Backend Engineers, Frontend Engineers

---

## Table of Contents

1. [Test strategy](#1-test-strategy)
2. [Unit tests](#2-unit-tests)
3. [Integration tests](#3-integration-tests)
4. [API tests](#4-api-tests)
5. [UI tests](#5-ui-tests)
6. [Performance tests](#6-performance-tests)
7. [Security tests](#7-security-tests)
8. [Test data](#8-test-data)

---

## 1. Test strategy

### 1.1 Testing pyramid

```
              E2E (5%)
           /           \
        UI Tests (15%)
      /                  \
   Integration (30%)
  /                       \
Unit Tests (50%)
```

| Test Level | Coverage | Purpose |
|------------|----------|---------|
| Unit | 50% | Test individual functions/methods |
| Integration | 30% | Test module interactions |
| API | 10% | Test REST endpoints |
| UI | 5% | Test user interactions |
| E2E | 5% | Test complete workflows |

### 1.2 Test tools

| Tool | Purpose |
|------|---------|
| pytest | Backend unit/integration tests |
| pytest-asyncio | Async test support |
| httpx | API testing |
| Jest | Frontend unit tests |
| React Testing Library | Component testing |
| Playwright | E2E testing |
| Locust | Load testing |

### 1.3 Test environments

| Environment | Purpose | URL |
|-------------|---------|-----|
| Local | Development testing | http://localhost:8000 |
| CI | Automated testing | Internal |
| Staging | Pre-production testing | https://staging.agentflow.com |
| Production | Smoke tests only | https://agentflow.com |

---

## 2. Unit tests

### 2.1 Validator tests

#### TC-UNIT-001: Validate valid workflow

**File:** `backend/tests/test_validator.py`

```python
import pytest
from agentflow_core.api.models.workflow_model import (
    WorkflowSpecModel, NodeModel, EdgeModel, SourceModel
)
from agentflow_core.runtime.validator import validate_workflow

def test_validate_valid_workflow():
    """Test validation of a valid workflow specification."""
    
    # Arrange
    spec = WorkflowSpecModel(
        nodes=[
            NodeModel(id="input", type="input"),
            NodeModel(id="router", type="router", metadata={"source": "src_llm_1"})
        ],
        edges=[
            EdgeModel(**{"from": "input", "to": "router"})
        ],
        queues=[],
        sources=[
            SourceModel(id="src_llm_1", kind="llm", config={"model_name": "gpt-4"})
        ],
        start_node="input"
    )
    
    # Act
    errors = validate_workflow(spec)
    
    # Assert
    assert len(errors) == 0, "Valid workflow should have no errors"
```

**Expected Result:**
- Validation passes with zero errors
- No exceptions raised

---

#### TC-UNIT-002: Validate missing start node

```python
def test_validate_missing_start_node():
    """Test validation fails when start node doesn't exist."""
    
    # Arrange
    spec = WorkflowSpecModel(
        nodes=[NodeModel(id="input", type="input")],
        edges=[],
        queues=[],
        sources=[],
        start_node="nonexistent"
    )
    
    # Act
    errors = validate_workflow(spec)
    
    # Assert
    assert len(errors) == 1
    assert errors[0].code == "E005"
    assert "Start node" in errors[0].message
    assert "does not exist" in errors[0].message
```

**Expected Result:**
- Validation fails with error code E005
- Error message: "Start node 'nonexistent' does not exist"

---

#### TC-UNIT-003: Validate invalid edge reference

```python
def test_validate_invalid_edge():
    """Test validation fails when edge references non-existent node."""
    
    # Arrange
    spec = WorkflowSpecModel(
        nodes=[NodeModel(id="input", type="input")],
        edges=[
            EdgeModel(**{"from": "input", "to": "nonexistent"})
        ],
        queues=[],
        sources=[],
        start_node="input"
    )
    
    # Act
    errors = validate_workflow(spec)
    
    # Assert
    assert len(errors) == 1
    assert errors[0].code == "E006"
    assert "non-existent destination node" in errors[0].message
```

**Expected Result:**
- Validation fails with error code E006
- Error identifies the invalid node reference

---

### 2.2 Builder tests

#### TC-UNIT-004: Build graph from valid workflow

```python
from agentflow_core.runtime.builder import build_graph_from_json

def test_build_graph_from_json():
    """Test building LangGraph from workflow spec."""
    
    # Arrange
    spec = WorkflowSpecModel(
        nodes=[
            NodeModel(id="input", type="input"),
            NodeModel(id="llm", type="llm", metadata={"source": "src_llm_1"})
        ],
        edges=[
            EdgeModel(**{"from": "input", "to": "llm"})
        ],
        queues=[],
        sources=[
            SourceModel(id="src_llm_1", kind="llm", config={"model_name": "gpt-4"})
        ],
        start_node="input"
    )
    
    # Act
    graph = build_graph_from_json(spec)
    
    # Assert
    assert graph is not None
    assert hasattr(graph, 'invoke')
```

**Expected Result:**
- Graph object created successfully
- Graph has `invoke` method for execution

---

### 2.3 Node tests

#### TC-UNIT-005: LLM node execution

```python
from agentflow_core.nodes.llm_node import create_llm_node
from agentflow_core.runtime.state import GraphState

@pytest.mark.asyncio
async def test_llm_node_execution(mocker):
    """Test LLM node generates text response."""
    
    # Arrange
    mock_llm = mocker.patch('agentflow_core.sources.llm_openai.get_llm_client')
    mock_response = mocker.Mock()
    mock_response.choices[0].message.content = "Generated text"
    mock_response.usage.total_tokens = 150
    mock_llm.return_value.chat.completions.create.return_value = mock_response
    
    node = create_llm_node("llm_node", {"source": "src_llm_1", "prompt": "Hello"})
    state = GraphState(user_input="Hello")
    
    # Act
    result = node(state)
    
    # Assert
    assert result['text_result'] == "Generated text"
    assert result['tokens_used'] == 150
```

**Expected Result:**
- LLM node returns generated text
- Token usage tracked in state

---

#### TC-UNIT-006: Router node intent classification

```python
from agentflow_core.nodes.router_node import create_router_node

@pytest.mark.asyncio
async def test_router_node_classification(mocker):
    """Test router node classifies user intent."""
    
    # Arrange
    mock_llm = mocker.patch('agentflow_core.sources.llm_openai.get_llm_client')
    mock_response = mocker.Mock()
    mock_response.choices[0].message.content = "image"
    mock_llm.return_value.chat.completions.create.return_value = mock_response
    
    node = create_router_node("router", {"source": "src_llm_1"})
    state = GraphState(user_input="Generate a sunset image")
    
    # Act
    result = node(state)
    
    # Assert
    assert result['intent'] == "image"
```

**Expected Result:**
- Router classifies intent correctly
- Intent stored in state

---

#### TC-UNIT-007: DB node query execution

```python
from agentflow_core.nodes.db_node import create_db_node

@pytest.mark.asyncio
async def test_db_node_query(mocker):
    """Test DB node executes SQL query."""
    
    # Arrange
    mock_db = mocker.patch('agentflow_core.sources.db_postgres.get_db_connection')
    mock_cursor = mocker.Mock()
    mock_cursor.fetchall.return_value = [("John", 30), ("Jane", 25)]
    mock_db.return_value.cursor.return_value = mock_cursor
    
    node = create_db_node("db", {"source": "src_db_1", "query": "SELECT name, age FROM users"})
    state = GraphState()
    
    # Act
    result = node(state)
    
    # Assert
    assert len(result['db_result']) == 2
    assert result['db_result'][0] == ("John", 30)
```

**Expected Result:**
- Query executed successfully
- Results stored in state

---

### 2.4 Rate limiter tests

#### TC-UNIT-008: Rate limit enforcement

```python
from agentflow_core.runtime.rate_limiter import RateLimiter
import time

def test_rate_limit_enforcement():
    """Test rate limiter enforces message limits."""
    
    # Arrange
    limiter = RateLimiter(max_messages_per_second=2)
    
    # Act & Assert
    assert limiter.check_limit() == True  # 1st request
    assert limiter.check_limit() == True  # 2nd request
    assert limiter.check_limit() == False # 3rd request (exceeded)
    
    time.sleep(1)
    assert limiter.check_limit() == True  # Reset after 1 second
```

**Expected Result:**
- First 2 requests allowed
- 3rd request blocked
- Limit resets after 1 second

---

## 3. Integration tests

### 3.1 Workflow execution tests

#### TC-INT-001: Execute basic workflow

```python
from agentflow_core.runtime.executor import run_workflow

@pytest.mark.asyncio
async def test_execute_basic_workflow(mocker):
    """Test execution of basic text generation workflow."""
    
    # Arrange
    mock_llm = mocker.patch('agentflow_core.sources.llm_openai.get_llm_client')
    mock_response = mocker.Mock()
    mock_response.choices[0].message.content = "Paris is the capital of France"
    mock_response.usage.total_tokens = 50
    mock_llm.return_value.chat.completions.create.return_value = mock_response
    
    spec = WorkflowSpecModel(
        nodes=[
            NodeModel(id="input", type="input"),
            NodeModel(id="llm", type="llm", metadata={"source": "src_llm_1"})
        ],
        edges=[EdgeModel(**{"from": "input", "to": "llm"})],
        queues=[],
        sources=[SourceModel(id="src_llm_1", kind="llm", config={"model_name": "gpt-4"})],
        start_node="input"
    )
    
    initial_state = GraphState(user_input="What is the capital of France?")
    
    # Act
    result = await run_workflow(spec, initial_state)
    
    # Assert
    assert result['text_result'] == "Paris is the capital of France"
    assert result['tokens_used'] == 50
```

**Expected Result:**
- Workflow executes successfully
- Final state contains text result

---

#### TC-INT-002: Execute router workflow

```python
@pytest.mark.asyncio
async def test_execute_router_workflow(mocker):
    """Test execution of router workflow with conditional routing."""
    
    # Arrange
    mock_llm = mocker.patch('agentflow_core.sources.llm_openai.get_llm_client')
    
    # Router classifies intent as "image"
    router_response = mocker.Mock()
    router_response.choices[0].message.content = "image"
    
    # Image generation
    image_response = mocker.Mock()
    image_response.data[0].url = "https://example.com/sunset.png"
    
    mock_llm.return_value.chat.completions.create.return_value = router_response
    mock_llm.return_value.images.generate.return_value = image_response
    
    spec = WorkflowSpecModel(
        nodes=[
            NodeModel(id="input", type="input"),
            NodeModel(id="router", type="router", metadata={"source": "src_llm_1"}),
            NodeModel(id="image", type="image", metadata={"source": "src_img_1"})
        ],
        edges=[
            EdgeModel(**{"from": "input", "to": "router"}),
            EdgeModel(**{"from": "router", "to": "image", "condition": "intent == 'image'"})
        ],
        queues=[],
        sources=[
            SourceModel(id="src_llm_1", kind="llm", config={"model_name": "gpt-4"}),
            SourceModel(id="src_img_1", kind="image", config={"model_name": "dall-e-3"})
        ],
        start_node="input"
    )
    
    initial_state = GraphState(user_input="Generate a sunset image")
    
    # Act
    result = await run_workflow(spec, initial_state)
    
    # Assert
    assert result['intent'] == "image"
    assert result['image_result'] == "https://example.com/sunset.png"
```

**Expected Result:**
- Router classifies intent as "image"
- Image node executes
- Image URL in final state

---

#### TC-INT-003: Execute aggregator workflow

```python
@pytest.mark.asyncio
async def test_execute_aggregator_workflow(mocker):
    """Test execution of workflow with parallel nodes and aggregator."""
    
    # Arrange
    mock_llm = mocker.patch('agentflow_core.sources.llm_openai.get_llm_client')
    
    # LLM response
    llm_response = mocker.Mock()
    llm_response.choices[0].message.content = "France is in Europe"
    llm_response.usage.total_tokens = 50
    
    # Aggregator combines results
    agg_response = mocker.Mock()
    agg_response.choices[0].message.content = "Summary: Paris is capital. France is in Europe."
    agg_response.usage.total_tokens = 30
    
    mock_llm.return_value.chat.completions.create.side_effect = [llm_response, agg_response]
    
    spec = WorkflowSpecModel(
        nodes=[
            NodeModel(id="input", type="input"),
            NodeModel(id="llm1", type="llm", metadata={"source": "src_llm_1", "prompt": "Capital?"}),
            NodeModel(id="llm2", type="llm", metadata={"source": "src_llm_1", "prompt": "Location?"}),
            NodeModel(id="agg", type="aggregator", metadata={"source": "src_llm_1"})
        ],
        edges=[
            EdgeModel(**{"from": "input", "to": ["llm1", "llm2"]}),
            EdgeModel(**{"from": "llm1", "to": "agg"}),
            EdgeModel(**{"from": "llm2", "to": "agg"})
        ],
        queues=[],
        sources=[SourceModel(id="src_llm_1", kind="llm", config={"model_name": "gpt-4"})],
        start_node="input"
    )
    
    initial_state = GraphState(user_input="Tell me about France")
    
    # Act
    result = await run_workflow(spec, initial_state)
    
    # Assert
    assert "Summary" in result['final_output']
    assert result['tokens_used'] == 80
```

**Expected Result:**
- Both LLM nodes execute in parallel
- Aggregator combines results
- Final output contains summary

---

## 4. API tests

### 4.1 Workflow endpoints

#### TC-API-001: POST /workflows/validate (valid)

```python
from fastapi.testclient import TestClient
from agentflow_core.api.main import app

client = TestClient(app)

def test_validate_workflow_valid():
    """Test validation endpoint with valid workflow."""
    
    # Arrange
    payload = {
        "nodes": [{"id": "input", "type": "input"}],
        "edges": [],
        "queues": [],
        "sources": [],
        "start_node": "input"
    }
    
    # Act
    response = client.post("/workflows/validate", json=payload)
    
    # Assert
    assert response.status_code == 200
    data = response.json()
    assert data["valid"] == True
    assert len(data["errors"]) == 0
```

**Expected Result:**
- HTTP 200 OK
- Response: `{"valid": true, "errors": []}`

---

#### TC-API-002: POST /workflows/validate (invalid)

```python
def test_validate_workflow_invalid():
    """Test validation endpoint with invalid workflow."""
    
    # Arrange
    payload = {
        "nodes": [{"id": "input", "type": "input"}],
        "edges": [],
        "queues": [],
        "sources": [],
        "start_node": "nonexistent"
    }
    
    # Act
    response = client.post("/workflows/validate", json=payload)
    
    # Assert
    assert response.status_code == 200
    data = response.json()
    assert data["valid"] == False
    assert len(data["errors"]) > 0
    assert data["errors"][0]["code"] == "E005"
```

**Expected Result:**
- HTTP 200 OK
- Response: `{"valid": false, "errors": [{"code": "E005", ...}]}`

---

#### TC-API-003: POST /workflows/execute

```python
def test_execute_workflow(mocker):
    """Test workflow execution endpoint."""
    
    # Arrange
    mock_llm = mocker.patch('agentflow_core.sources.llm_openai.get_llm_client')
    mock_response = mocker.Mock()
    mock_response.choices[0].message.content = "Result"
    mock_response.usage.total_tokens = 50
    mock_llm.return_value.chat.completions.create.return_value = mock_response
    
    payload = {
        "workflow": {
            "nodes": [
                {"id": "input", "type": "input"},
                {"id": "llm", "type": "llm", "metadata": {"source": "src_llm_1"}}
            ],
            "edges": [{"from": "input", "to": "llm"}],
            "queues": [],
            "sources": [{"id": "src_llm_1", "kind": "llm", "config": {"model_name": "gpt-4"}}],
            "start_node": "input"
        },
        "initial_state": {"user_input": "Hello"}
    }
    
    # Act
    response = client.post("/workflows/execute", json=payload)
    
    # Assert
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert "final_state" in data
```

**Expected Result:**
- HTTP 200 OK
- Response contains final state with results

---

#### TC-API-004: POST /workflows (create)

```python
def test_create_workflow():
    """Test creating a new workflow."""
    
    # Arrange
    payload = {
        "name": "Test Workflow",
        "spec": {
            "nodes": [{"id": "input", "type": "input"}],
            "edges": [],
            "queues": [],
            "sources": [],
            "start_node": "input"
        }
    }
    
    # Act
    response = client.post(
        "/workflows",
        json=payload,
        headers={"X-API-Key": "test-key"}
    )
    
    # Assert
    assert response.status_code == 201
    data = response.json()
    assert "id" in data
    assert data["name"] == "Test Workflow"
```

**Expected Result:**
- HTTP 201 Created
- Response contains workflow ID and name

---

### 4.2 Source endpoints

#### TC-API-005: POST /sources (create)

```python
def test_create_source():
    """Test creating a new source."""
    
    # Arrange
    payload = {
        "id": "src_llm_test",
        "kind": "llm",
        "config": {
            "model_name": "gpt-4",
            "temperature": 0.7
        }
    }
    
    # Act
    response = client.post(
        "/sources",
        json=payload,
        headers={"X-API-Key": "test-key"}
    )
    
    # Assert
    assert response.status_code == 201
    data = response.json()
    assert data["id"] == "src_llm_test"
    assert data["kind"] == "llm"
```

**Expected Result:**
- HTTP 201 Created
- Response contains source details

---

#### TC-API-006: GET /sources

```python
def test_list_sources():
    """Test listing all sources."""
    
    # Act
    response = client.get(
        "/sources",
        headers={"X-API-Key": "test-key"}
    )
    
    # Assert
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
```

**Expected Result:**
- HTTP 200 OK
- Response contains array of sources

---

### 4.3 Health endpoints

#### TC-API-007: GET /health

```python
def test_health_check():
    """Test health check endpoint."""
    
    # Act
    response = client.get("/health")
    
    # Assert
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert "version" in data
    assert "uptime" in data
```

**Expected Result:**
- HTTP 200 OK
- Response: `{"status": "ok", "version": "1.0.0", "uptime": 123.45}`

---

## 5. UI tests

### 5.1 Component tests

#### TC-UI-001: WorkflowCanvas renders

```typescript
import { render, screen } from '@testing-library/react';
import { WorkflowCanvas } from '@/components/WorkflowCanvas';

test('renders workflow canvas', () => {
  render(<WorkflowCanvas />);
  
  const canvas = screen.getByRole('region');
  expect(canvas).toBeInTheDocument();
});
```

**Expected Result:**
- Canvas component renders without errors

---

#### TC-UI-002: Add node to canvas

```typescript
import { render, fireEvent } from '@testing-library/react';
import { WorkflowCanvas } from '@/components/WorkflowCanvas';
import { useWorkflowStore } from '@/lib/useWorkflowStore';

test('adds node to canvas', () => {
  const { result } = renderHook(() => useWorkflowStore());
  
  act(() => {
    result.current.addNode({
      id: 'test-node',
      type: 'llm',
      position: { x: 100, y: 100 },
      data: {}
    });
  });
  
  expect(result.current.nodes).toHaveLength(1);
  expect(result.current.nodes[0].id).toBe('test-node');
});
```

**Expected Result:**
- Node added to store
- Canvas updates to display node

---

#### TC-UI-003: Connect two nodes

```typescript
test('connects two nodes', () => {
  const { result } = renderHook(() => useWorkflowStore());
  
  act(() => {
    result.current.addNode({
      id: 'node1',
      type: 'input',
      position: { x: 0, y: 0 },
      data: {}
    });
    
    result.current.addNode({
      id: 'node2',
      type: 'llm',
      position: { x: 200, y: 0 },
      data: {}
    });
    
    result.current.setEdges([{
      id: 'e1',
      source: 'node1',
      target: 'node2'
    }]);
  });
  
  expect(result.current.edges).toHaveLength(1);
  expect(result.current.edges[0].source).toBe('node1');
  expect(result.current.edges[0].target).toBe('node2');
});
```

**Expected Result:**
- Edge created between nodes
- Canvas displays connection

---

### 5.2 E2E tests

#### TC-E2E-001: Create and execute workflow

```typescript
import { test, expect } from '@playwright/test';

test('create and execute workflow', async ({ page }) => {
  // Navigate to designer
  await page.goto('http://localhost:3000/designer');
  
  // Add input node
  await page.click('[data-node-type="input"]');
  await page.click('.canvas', { position: { x: 100, y: 100 } });
  
  // Add LLM node
  await page.click('[data-node-type="llm"]');
  await page.click('.canvas', { position: { x: 300, y: 100 } });
  
  // Connect nodes
  await page.dragAndDrop('.node-handle-source', '.node-handle-target');
  
  // Configure source
  await page.click('[data-testid="configure-source"]');
  await page.fill('[name="model_name"]', 'gpt-4');
  await page.click('button[type="submit"]');
  
  // Execute workflow
  await page.click('[data-testid="execute-workflow"]');
  await page.fill('[name="user_input"]', 'What is AI?');
  await page.click('button[type="submit"]');
  
  // Verify result
  await expect(page.locator('[data-testid="execution-result"]')).toBeVisible();
  await expect(page.locator('[data-testid="execution-result"]')).toContainText('AI is');
});
```

**Expected Result:**
- Workflow created visually
- Execution completes successfully
- Result displayed in UI

---

## 6. Performance tests

### 6.1 Load tests

#### TC-PERF-001: Concurrent workflow executions

```python
from locust import HttpUser, task, between

class WorkflowUser(HttpUser):
    wait_time = between(1, 3)
    
    @task
    def execute_workflow(self):
        payload = {
            "workflow": {
                "nodes": [
                    {"id": "input", "type": "input"},
                    {"id": "llm", "type": "llm", "metadata": {"source": "src_llm_1"}}
                ],
                "edges": [{"from": "input", "to": "llm"}],
                "queues": [],
                "sources": [{"id": "src_llm_1", "kind": "llm", "config": {"model_name": "gpt-4"}}],
                "start_node": "input"
            },
            "initial_state": {"user_input": "Hello"}
        }
        
        self.client.post("/workflows/execute", json=payload)
```

**Test Parameters:**
- Users: 100 concurrent
- Ramp-up: 10 users/second
- Duration: 5 minutes

**Expected Result:**
- 95th percentile response time < 2 seconds
- Error rate < 1%
- Throughput > 50 requests/second

---

#### TC-PERF-002: Rate limiter stress test

```python
import asyncio
from agentflow_core.runtime.rate_limiter import RateLimiter

async def test_rate_limiter_stress():
    """Test rate limiter under high load."""
    
    limiter = RateLimiter(max_messages_per_second=100)
    
    async def make_request():
        return limiter.check_limit()
    
    # Generate 1000 concurrent requests
    tasks = [make_request() for _ in range(1000)]
    results = await asyncio.gather(*tasks)
    
    allowed = sum(results)
    blocked = len(results) - allowed
    
    # Verify rate limit enforced
    assert allowed <= 100
    assert blocked >= 900
```

**Expected Result:**
- Rate limiter blocks excess requests
- No crashes under load

---

## 7. Security tests

### 7.1 Authentication tests

#### TC-SEC-001: API key authentication

```python
def test_api_key_required():
    """Test API key is required for protected endpoints."""
    
    # Act
    response = client.post("/workflows")
    
    # Assert
    assert response.status_code == 401
    assert "API key required" in response.json()["detail"]
```

**Expected Result:**
- HTTP 401 Unauthorized
- Error message indicates missing API key

---

#### TC-SEC-002: Invalid API key rejected

```python
def test_invalid_api_key():
    """Test invalid API key is rejected."""
    
    # Act
    response = client.post(
        "/workflows",
        headers={"X-API-Key": "invalid-key"}
    )
    
    # Assert
    assert response.status_code == 401
    assert "Invalid API key" in response.json()["detail"]
```

**Expected Result:**
- HTTP 401 Unauthorized
- Error indicates invalid key

---

### 7.2 Input validation tests

#### TC-SEC-003: SQL injection prevention

```python
def test_sql_injection_prevention():
    """Test DB node prevents SQL injection."""
    
    # Arrange
    malicious_query = "SELECT * FROM users; DROP TABLE users;--"
    
    spec = WorkflowSpecModel(
        nodes=[
            NodeModel(id="db", type="db", metadata={
                "source": "src_db_1",
                "query": malicious_query
            })
        ],
        edges=[],
        queues=[],
        sources=[SourceModel(id="src_db_1", kind="db", config={})],
        start_node="db"
    )
    
    # Act & Assert
    with pytest.raises(ValueError, match="Invalid SQL"):
        run_workflow(spec, GraphState())
```

**Expected Result:**
- SQL injection attempt blocked
- Error raised before execution

---

#### TC-SEC-004: XSS prevention

```python
def test_xss_prevention():
    """Test API sanitizes user input."""
    
    # Arrange
    payload = {
        "user_input": "<script>alert('XSS')</script>"
    }
    
    # Act
    response = client.post(
        "/workflows/execute",
        json=payload,
        headers={"X-API-Key": "test-key"}
    )
    
    # Assert
    assert response.status_code == 400
    assert "Invalid input" in response.json()["detail"]
```

**Expected Result:**
- HTTP 400 Bad Request
- Malicious input rejected

---

## 8. Test data

### 8.1 Sample workflows

#### Workflow 1: Basic text generation

```json
{
  "nodes": [
    {"id": "input", "type": "input"},
    {"id": "llm", "type": "llm", "metadata": {"source": "src_llm_1"}}
  ],
  "edges": [{"from": "input", "to": "llm"}],
  "queues": [],
  "sources": [
    {"id": "src_llm_1", "kind": "llm", "config": {"model_name": "gpt-4"}}
  ],
  "start_node": "input"
}
```

#### Workflow 2: Router with branching

```json
{
  "nodes": [
    {"id": "input", "type": "input"},
    {"id": "router", "type": "router", "metadata": {"source": "src_llm_1"}},
    {"id": "llm", "type": "llm", "metadata": {"source": "src_llm_1"}},
    {"id": "image", "type": "image", "metadata": {"source": "src_img_1"}}
  ],
  "edges": [
    {"from": "input", "to": "router"},
    {"from": "router", "to": "llm", "condition": "intent == 'text'"},
    {"from": "router", "to": "image", "condition": "intent == 'image'"}
  ],
  "queues": [],
  "sources": [
    {"id": "src_llm_1", "kind": "llm", "config": {"model_name": "gpt-4"}},
    {"id": "src_img_1", "kind": "image", "config": {"model_name": "dall-e-3"}}
  ],
  "start_node": "input"
}
```

### 8.2 Test users

| User ID | Role | API Key |
|---------|------|---------|
| user_test_1 | admin | test-key-admin |
| user_test_2 | developer | test-key-dev |
| user_test_3 | viewer | test-key-viewer |

---

**Document Approval**

| Role | Name | Date | Signature |
|------|------|------|-----------|
| QA Lead | _______________ | _______________ | _______________ |
| Backend Engineer | _______________ | _______________ | _______________ |
| DevOps Engineer | _______________ | _______________ | _______________ |
