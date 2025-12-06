agentflow/
│
├── backend/                          # AgentFlow Core (Python + LangGraph)
│   ├── agentflow_core/
│   │   ├── __init__.py
│   │   ├── runtime/                  # LangGraph runtime + workflow engine
│   │   │   ├── builder.py            # build_graph_from_json()
│   │   │   ├── executor.py           # run_workflow(), tracing
│   │   │   ├── validator.py          # schema + logical validation
│   │   │   ├── rate_limiter.py       # queue & bandwidth logic
│   │   │   ├── state.py              # GraphState definitions
│   │   │   └── registry.py           # node types, sources, queues registries
│   │   │
│   │   ├── nodes/                    # Implementations for node types
│   │   │   ├── base_node.py
│   │   │   ├── llm_node.py
│   │   │   ├── image_node.py
│   │   │   ├── db_node.py
│   │   │   ├── router_node.py
│   │   │   └── aggregator_node.py
│   │   │
│   │   ├── sources/                  # External service abstraction layer
│   │   │   ├── llm_openai.py
│   │   │   ├── image_openai.py
│   │   │   ├── db_postgres.py
│   │   │   └── api_http.py
│   │   │
│   │   ├── schemas/                  # JSON schemas for validation
│   │   │   ├── workflow_schema.json
│   │   │   ├── node_schema.json
│   │   │   └── queue_schema.json
│   │   │
│   │   ├── api/                      # FastAPI service
│   │   │   ├── __init__.py
│   │   │   ├── main.py               # FastAPI app instance
│   │   │   ├── routes/
│   │   │   │   ├── workflows.py      # validate, execute, save workflows
│   │   │   │   ├── sources.py        # manage sources
│   │   │   │   └── health.py
│   │   │   └── models/
│   │   │       └── workflow_model.py # Pydantic models for request/response
│   │   │
│   │   └── utils/
│   │       ├── logger.py
│   │       ├── error_handler.py
│   │       └── id_generator.py
│   │
│   ├── tests/                        # Unit tests for backend
│   │   ├── test_builder.py
│   │   ├── test_validator.py
│   │   ├── test_executor.py
│   │   └── test_api.py
│   │
│   ├── requirements.txt
│   ├── pyproject.toml                # if using poetry
│   └── README.md
│
│
├── frontend/                         # AgentFlow Studio (Next.js)
│   ├── agentflow-studio/
│   │   ├── app/
│   │   │   ├── layout.tsx
│   │   │   ├── page.tsx              # Dashboard
│   │   │   ├── designer/             # Workflow designer UI
│   │   │   │   ├── page.tsx
│   │   │   │   └── components.json   # Designer config (optional)
│   │   │   │
│   │   │   ├── sources/
│   │   │   │   └── page.tsx          # Source manager UI
│   │   │   │
│   │   │   ├── api/
│   │   │   │   ├── workflows/
│   │   │   │   │   └── route.ts      # Proxy to backend validate/save
│   │   │   │   └── execute/
│   │   │   │       └── route.ts      # Test run proxy
│   │   │   │
│   │   │   └── settings/
│   │   │       └── page.tsx
│   │   │
│   │   ├── components/
│   │   │   ├── WorkflowCanvas.tsx
│   │   │   ├── NodePalette.tsx
│   │   │   ├── QueueEditor.tsx
│   │   │   ├── SourceEditor.tsx
│   │   │   ├── PropertiesPanel.tsx
│   │   │   └── JsonPreview.tsx
│   │   │
│   │   ├── lib/
│   │   │   ├── types.ts              # WorkflowSpec TS types
│   │   │   ├── schema.ts             # JSON schema for FE validation
│   │   │   └── mappers.ts            # Canvas → JSON converter
│   │   │
│   │   ├── public/
│   │   ├── styles/
│   │   ├── package.json
│   │   └── README.md
│
│
├── shared/                           # Shared documents & assets
│   ├── examples/
│   │   ├── workflow_basic.json
│   │   └── workflow_extended.json
│   │
│   ├── docs/
│   │   ├── SRS_AgentFlow.docx
│   │   ├── HLD.md
│   │   ├── LLD.md
│   │   └── API_Spec.md
│   │
│   ├── diagrams/
│   │   ├── architecture.png
│   │   ├── workflow_engine.png
│   │   └── designer_ui.png
│   │
│   └── assets/
│       ├── logo/
│       └── branding/
│
│
├── scripts/
│   ├── build_backend.sh
│   ├── start_backend.sh
│   ├── start_frontend.sh
│   └── deploy.sh
│
├── .gitignore
├── README.md
└── LICENSE
