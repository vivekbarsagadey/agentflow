# 📚 AgentFlow Documentation Hub

**Version:** 1.0  
**Last Updated:** December 7, 2025  
**Status:** Active Development

---

## Overview

Welcome to the AgentFlow documentation hub. This directory contains comprehensive documentation for the AgentFlow platform — a **JSON-driven workflow orchestration engine** built on LangGraph with a visual designer (AgentFlow Studio).

AgentFlow enables users to:
- Define **multi-agent workflows** using structured JSON specifications
- Configure **nodes**, **queues**, and **sources** (LLMs, image models, DBs, APIs)
- Execute workflows through a Python/LangGraph runtime
- Design, visualize, and manage workflows through a web-based UI

---

## 📑 Documentation Index

| # | Document | Description | Audience |
|---|----------|-------------|----------|
| 01 | [PRD](./01-PRD.md) | Product Requirements Document | Product, Engineering, Stakeholders |
| 02 | [SRS](./02-SRS.md) | Software Requirements Specification | Architects, Developers, QA |
| 03 | [HLD](./03-HLD.md) | High-Level Design | Architects, Tech Leads |
| 04 | [LLD](./04-LLD.md) | Low-Level Design | Backend & Frontend Engineers |
| 05 | [API-DOC](./05-API-DOC.md) | API Documentation | Backend, Frontend, Integration Teams |
| 06 | [DB-SCHEMA](./06-DB-SCHEMA.md) | Database Schema & Data Models | Backend Engineers, DBAs |
| 07 | [STATE-MACHINE](./07-STATE-MACHINE.md) | State Machine & Workflow States | Engineers, QA |
| 08 | [SEQUENCE-DIAGRAM](./08-SEQUENCE-DIAGRAM.md) | Sequence Diagrams | Engineers, Architects |
| 09 | [IMPLEMENTATION-GUIDE](./09-IMPLEMENTATION-GUIDE.md) | Implementation Guide | Developers |
| 10 | [TEST-CASES](./10-TEST-CASES.md) | Test Cases & QA Plan | QA Engineers, Developers |
| 11 | [RISK-MITIGATION](./11-RISK-MITIGATION.md) | Risk Assessment & Mitigation | Project Managers, Tech Leads |
| 12 | [PROJECT-PLAN](./12-PROJECT-PLAN.md) | Project Plan & Timeline | Project Managers, Stakeholders |

---

## 🏗️ Architecture at a Glance

```
┌─────────────────────────────────────────────────────────────────┐
│                     AgentFlow Studio                            │
│                  (Next.js Visual Designer)                      │
│                                                                 │
│   Drag & Drop UI  ───→  WorkflowSpec(JSON)  ───→  API Proxy    │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                     AgentFlow Core                              │
│                (FastAPI + Python + LangGraph)                   │
│                                                                 │
│   ┌───────────────┐     ┌───────────────────────────────┐      │
│   │  Validator    │ ──→ │  Runtime Graph Builder        │      │
│   └───────────────┘     └───────────────────────────────┘      │
│           │                         │                           │
│           ▼                         ▼                           │
│   ┌───────────────┐     ┌───────────────────────────────┐      │
│   │ Queue Manager │     │  Node Registry (LLM, DB, etc.)│      │
│   └───────────────┘     └───────────────────────────────┘      │
│           │                         │                           │
│           ▼                         ▼                           │
│   ┌─────────────────────────────────────────────────────┐      │
│   │        Executor (LangGraph runtime.invoke)          │      │
│   └─────────────────────────────────────────────────────┘      │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
                     Final State JSON Output
```

---

## 🛠️ Technology Stack

| Component | Technology |
|-----------|------------|
| **Backend API** | FastAPI (Python 3.11+) |
| **Runtime Engine** | LangGraph |
| **Database** | PostgreSQL (optional) |
| **Queue/Rate Limiting** | Redis |
| **Frontend Studio** | Next.js 16 + React 19 + TypeScript |
| **Canvas Library** | React Flow v12 |
| **UI Components** | ShadCN UI + TailwindCSS |
| **State Management** | Zustand |
| **LLM Integration** | OpenAI SDK |
| **Image Generation** | DALL·E / OpenAI |
| **Database Queries** | psycopg / SQLAlchemy |

---

## 📁 Project Structure

```
agentflow/
├── backend/                    # AgentFlow Core (Python/FastAPI)
│   └── agentflow_core/
│       ├── api/               # REST API layer
│       ├── runtime/           # LangGraph runtime engine
│       ├── nodes/             # Node implementations
│       ├── sources/           # External service adapters
│       ├── schemas/           # JSON Schema definitions
│       └── utils/             # Utilities
├── frontend/                   # AgentFlow Studio (Next.js)
│   └── agentflow-studio/
│       ├── app/               # Next.js App Router
│       ├── components/        # React components
│       └── lib/               # Utilities and types
├── docs/                       # Documentation (you are here)
├── shared/                     # Shared assets and examples
└── scripts/                    # Build and deployment scripts
```

---

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- Node.js 18+
- pnpm (recommended) or npm
- Redis (for rate limiting)
- PostgreSQL (optional, for workflow storage)

### Backend Setup

```bash
cd backend
pip install -r requirements.txt
uvicorn agentflow_core.api.main:app --reload
```

### Frontend Setup

```bash
cd frontend/agentflow-studio
pnpm install
pnpm dev
```

---

## 📖 Reading Order

For new team members, we recommend reading the documentation in this order:

1. **PRD** - Understand the product vision and goals
2. **SRS** - Learn the functional and non-functional requirements
3. **HLD** - Grasp the high-level architecture
4. **LLD** - Dive into implementation details
5. **API-DOC** - Understand the API contracts
6. **IMPLEMENTATION-GUIDE** - Get hands-on with development

---

## 🔄 Document Versioning

All documents follow semantic versioning:
- **Major**: Breaking changes to specifications
- **Minor**: New features or significant additions
- **Patch**: Clarifications and minor updates

---

## 👥 Contributors

- **Product Team**: PRD, User Stories
- **Architecture Team**: HLD, LLD, API Spec
- **Engineering Team**: Implementation Guide, Code
- **QA Team**: Test Cases, Quality Assurance
- **Project Management**: Project Plan, Risk Mitigation

---

## 📝 Feedback

For documentation feedback or suggestions, please:
1. Create an issue in the repository
2. Tag with `documentation` label
3. Reference the specific document and section

---

**Maintained by**: AgentFlow Engineering Team  
**Contact**: engineering@agentflow.ai
