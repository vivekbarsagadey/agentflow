# AgentFlow Core

**Multi-Agent Workflow Orchestration Engine**

AgentFlow Core is a Python-based workflow orchestration engine built on FastAPI and LangGraph. It provides JSON-driven workflow specification, multi-agent execution, and a REST API.

## Features

- ✅ **JSON-driven Workflows**: Define workflows using WorkflowSpec JSON format
- ✅ **LangGraph Runtime**: Execute workflows using LangGraph StateGraph
- ✅ **6 Node Types**: Input, Router, LLM, Image, DB, Aggregator
- ✅ **Source Adapters**: Gemini AI, PostgreSQL, HTTP APIs
- ✅ **Validation Engine**: Comprehensive workflow validation
- ✅ **REST API**: FastAPI endpoints for validation and execution
- ✅ **Structured Logging**: Production-ready logging with structlog

## Quick Start

### Prerequisites

- Python 3.11+

### Installation

```bash
cd backend/agentflow_core
pip install -e .
```

### Configuration

Copy the example environment file:
```bash
cp .env.example .env
```

Edit `.env` and add your Gemini API key:
```
GEMINI_API_KEY=your-gemini-api-key-here
```

### Running the Server

```bash
uvicorn agentflow_core.main:app --reload
```

The API will be available at `http://localhost:8000`

### API Documentation

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Project Structure

```
agentflow_core/
├── api/
│   ├── main.py              # FastAPI application
│   ├── models/
│   │   └── workflow_model.py # Pydantic models
│   └── routes/
│       ├── health.py        # Health check endpoints
│       ├── workflows.py     # Workflow validation & execution
│       └── sources.py       # Source management
├── nodes/
│   ├── base_node.py         # Node interface
│   ├── input_node.py        # Input node
│   ├── router_node.py       # Router node
│   ├── llm_node.py          # LLM node (Gemini)
│   ├── image_node.py        # Image node (Imagen)
│   ├── db_node.py           # Database node
│   └── aggregator_node.py   # Aggregator node
├── runtime/
│   ├── builder.py           # WorkflowSpec → LangGraph
│   ├── executor.py          # Workflow execution
│   ├── validator.py         # Workflow validation
│   ├── registry.py          # Source registry
│   ├── rate_limiter.py      # Rate limiting
│   └── state.py             # GraphState definition
├── sources/
│   ├── llm_gemini.py        # Gemini AI adapter
│   ├── image_gemini.py      # Imagen adapter
│   ├── db_postgres.py       # PostgreSQL adapter
│   └── api_http.py          # HTTP API adapter
├── schemas/
│   ├── workflow_schema.json # JSON schema for WorkflowSpec
│   ├── node_schema.json     # JSON schema for nodes
│   └── queue_schema.json    # JSON schema for queues
└── utils/
    ├── logger.py            # Structured logging
    ├── id_generator.py      # ID generation
    └── error_handler.py     # Error handling
```

## Usage Examples

### Validate a Workflow

```python
from agentflow_core.runtime.validator import validate_workflow
from agentflow_core.api.models.workflow_model import WorkflowSpecModel

# Parse workflow from JSON
workflow = WorkflowSpecModel.model_validate(workflow_json)

# Validate
errors = validate_workflow(workflow)
if not errors:
    print("Workflow is valid!")
```

### Execute a Workflow

```python
from agentflow_core.runtime.builder import build_graph_from_json
from agentflow_core.runtime.executor import run_workflow

# Build LangGraph from WorkflowSpec
graph = build_graph_from_json(workflow)

# Execute with initial state
initial_state = {"user_input": "Tell me a joke"}
result = run_workflow(graph, initial_state)

print(result["final_output"])
```

### API Usage

```bash
# Validate a workflow
curl -X POST http://localhost:8000/workflows/validate \
  -H "Content-Type: application/json" \
  -d @workflow.json

# Execute a workflow
curl -X POST http://localhost:8000/workflows/execute \
  -H "Content-Type: application/json" \
  -d '{"workflow": {...}, "initial_state": {"user_input": "Hello"}}'
```

## Development

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=agentflow_core --cov-report=html

# Run specific test file
pytest tests/test_validator.py -v
```

### Code Quality

```bash
# Format code
black agentflow_core tests

# Lint code
ruff check agentflow_core tests

# Type checking
mypy agentflow_core
```

## License

MIT License - see LICENSE file for details.
