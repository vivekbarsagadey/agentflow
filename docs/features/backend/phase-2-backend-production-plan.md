---
goal: Phase 2 - Backend Production Readiness Implementation Plan
version: 1.0
date_created: 2025-12-07
last_updated: 2025-12-07
owner: AgentFlow Backend Engineering Team
status: 'Planned'
tags: ['backend', 'production', 'database', 'rate-limiting', 'crud', 'phase-2']
---

# Phase 2: Backend Production Readiness Implementation Plan

![Status: Planned](https://img.shields.io/badge/status-Planned-blue)

This plan details the implementation of production-ready features for AgentFlow Core backend, including database persistence, workflow CRUD APIs, rate limiting, tenant isolation, and operational readiness features.

## 1. Requirements & Constraints

### Requirements

- **REQ-001**: Database Persistence - All workflows and sources must be stored in PostgreSQL with full CRUD support
- **REQ-002**: Rate Limiting - Queue-based rate limiting with Redis backend for distributed systems
- **REQ-003**: Tenant Isolation - All database queries must filter by `tenant_id` for multi-tenancy
- **REQ-004**: Soft Delete - Delete operations must be soft deletes (mark as deleted, preserve data)
- **REQ-005**: Alembic Migrations - All schema changes must be version-controlled with Alembic
- **REQ-006**: Connection Pooling - Database connections must use connection pooling for performance
- **REQ-007**: HTTP API Source - Support calling external REST APIs from workflows
- **REQ-008**: Execution Timeouts - Prevent runaway workflows with configurable timeouts
- **REQ-009**: Error Tracking - Integrate error tracking service (Sentry or equivalent)
- **REQ-010**: API Documentation - All new endpoints must have OpenAPI documentation

### Security Requirements

- **SEC-001**: Credentials Security - Never store credentials directly; use environment variable references only
- **SEC-002**: SQL Injection Prevention - All database queries must use parameterized statements
- **SEC-003**: Tenant Data Isolation - Enforce tenant boundaries at database query level
- **SEC-004**: API Key Validation - All endpoints must validate API key before processing

### Constraints

- **CON-001**: PostgreSQL 14+ - Minimum database version for JSONB support
- **CON-002**: Redis 7+ - Required for distributed rate limiting
- **CON-003**: Backward Compatibility - Phase 1 APIs must continue to work unchanged
- **CON-004**: Zero Downtime - Database migrations must support zero-downtime deployments
- **CON-005**: Python 3.11+ - Maintain Python version requirement

### Guidelines

- **GUD-001**: Follow FastAPI best practices for async endpoints
- **GUD-002**: Use Pydantic models for all request/response validation
- **GUD-003**: Use functional programming approach (avoid classes where possible)
- **GUD-004**: Write comprehensive tests (80%+ coverage target)
- **GUD-005**: Document all public APIs with docstrings and OpenAPI schemas

### Patterns to Follow

- **PAT-001**: Repository Pattern - Separate database access logic from business logic
- **PAT-002**: Service Layer Pattern - Business logic in service functions
- **PAT-003**: Dependency Injection - Use FastAPI's Depends() for dependencies
- **PAT-004**: Factory Functions - Use factory functions for creating service instances
- **PAT-005**: Token Bucket Algorithm - Use for rate limiting implementation

---

## 2. Implementation Steps

### Implementation Phase 2.1: Database Schema & Migrations

**GOAL-001**: Set up PostgreSQL schema and Alembic migration framework for workflows, sources, and executions

| Task | Description | Completed | Date |
|------|-------------|-----------|------|
| TASK-001 | Install Alembic and SQLAlchemy dependencies (`pip install alembic sqlalchemy psycopg2-binary`) | | |
| TASK-002 | Initialize Alembic in project root: `alembic init migrations` | | |
| TASK-003 | Configure Alembic `env.py` to use async SQLAlchemy engine and read DATABASE_URL from environment | | |
| TASK-004 | Create `backend/agentflow_core/db/__init__.py` for database utilities | | |
| TASK-005 | Create `backend/agentflow_core/db/base.py` with SQLAlchemy declarative base and database session factory | | |
| TASK-006 | Create `backend/agentflow_core/db/models/__init__.py` for database models | | |
| TASK-007 | Create `backend/agentflow_core/db/models/workflow.py` - Workflow model with id, tenant_id, name, description, spec (JSONB), created_at, updated_at, deleted_at, created_by, updated_by, deleted_by, status | | |
| TASK-008 | Create `backend/agentflow_core/db/models/source.py` - Source model with id, tenant_id, kind, config (JSONB), created_at, updated_at, deleted_at, status | | |
| TASK-009 | Create `backend/agentflow_core/db/models/execution.py` - Execution model with id, workflow_id, tenant_id, initial_state (JSONB), final_state (JSONB), status, started_at, completed_at, duration_seconds, tokens_used, cost, error_message | | |
| TASK-010 | Add indexes: workflows(tenant_id), workflows(status), sources(tenant_id), sources(kind), executions(workflow_id), executions(tenant_id), executions(status) | | |
| TASK-011 | Generate initial migration: `alembic revision --autogenerate -m "initial_schema"` | | |
| TASK-012 | Review and test migration: `alembic upgrade head` (apply migrations) | | |
| TASK-013 | Create `alembic downgrade -1` rollback test to verify migration reversibility | | |
| TASK-014 | Add database connection utility functions in `db/base.py`: `get_db_session()`, `create_tables()`, `drop_tables()` | | |
| TASK-015 | Create database initialization script `scripts/init_db.py` that runs migrations | | |
| TASK-016 | Update FastAPI app startup to check database connectivity and log status | | |

**Acceptance Criteria:**
- ✅ Alembic configured and migrations directory created
- ✅ All three models (Workflow, Source, Execution) defined with proper fields and indexes
- ✅ Initial migration generates successfully
- ✅ Migration can be applied: `alembic upgrade head`
- ✅ Migration can be rolled back: `alembic downgrade -1`
- ✅ Database session factory provides async sessions
- ✅ Database connectivity checked on app startup

---

### Implementation Phase 2.2: Workflow CRUD Repository

**GOAL-002**: Implement database repository layer for workflow persistence with tenant isolation

| Task | Description | Completed | Date |
|------|-------------|-----------|------|
| TASK-017 | Create `backend/agentflow_core/db/repositories/__init__.py` | | |
| TASK-018 | Create `backend/agentflow_core/db/repositories/workflow_repository.py` with factory function `create_workflow_repository(db: Session, tenant_id: str)` | | |
| TASK-019 | Implement `create_workflow(name, description, spec) -> Workflow` - Generate ID (`wf_` prefix), set tenant_id, save to database | | |
| TASK-020 | Implement `get_workflow_by_id(workflow_id) -> Workflow | None` - Query by ID and tenant_id | | |
| TASK-021 | Implement `list_workflows(skip, limit, status) -> List[Workflow]` - Paginated list filtered by tenant_id | | |
| TASK-022 | Implement `update_workflow(workflow_id, name, description, spec, updated_by) -> Workflow` - Update workflow, set updated_at | | |
| TASK-023 | Implement `delete_workflow(workflow_id, deleted_by) -> bool` - Soft delete (set deleted_at, status='DELETED') | | |
| TASK-024 | Implement `count_workflows(status) -> int` - Count workflows for pagination | | |
| TASK-025 | Add validation: Cannot delete workflow if active executions exist | | |
| TASK-026 | Add error handling: Raise 404 if workflow not found, 403 if wrong tenant | | |
| TASK-027 | Write unit tests for all repository functions (test with in-memory SQLite) | | |
| TASK-028 | Test tenant isolation: Verify tenant A cannot access tenant B workflows | | |

**Acceptance Criteria:**
- ✅ All CRUD operations implemented (create, read, update, delete)
- ✅ Tenant isolation enforced in all queries
- ✅ Soft delete implemented (deleted_at field)
- ✅ Pagination works correctly (skip/limit)
- ✅ Error handling for not found and wrong tenant
- ✅ Unit tests pass with >80% coverage
- ✅ Cannot delete workflows with active executions

---

### Implementation Phase 2.3: Source CRUD Repository

**GOAL-003**: Implement database repository layer for source configuration persistence

| Task | Description | Completed | Date |
|------|-------------|-----------|------|
| TASK-029 | Create `backend/agentflow_core/db/repositories/source_repository.py` with factory function `create_source_repository(db: Session, tenant_id: str)` | | |
| TASK-030 | Implement `create_source(kind, config) -> Source` - Generate ID (`src_` prefix), validate kind, save to database | | |
| TASK-031 | Implement `get_source_by_id(source_id) -> Source | None` - Query by ID and tenant_id | | |
| TASK-032 | Implement `list_sources(skip, limit, kind) -> List[Source]` - Paginated list filtered by tenant_id and optionally by kind | | |
| TASK-033 | Implement `update_source(source_id, config, updated_by) -> Source` - Update source config | | |
| TASK-034 | Implement `delete_source(source_id, deleted_by) -> bool` - Soft delete | | |
| TASK-035 | Implement `count_sources(kind) -> int` - Count sources for pagination | | |
| TASK-036 | Add validation: Cannot delete source if referenced by any active workflows | | |
| TASK-037 | Add validation: Source config must not contain hardcoded credentials (only env var references) | | |
| TASK-038 | Implement `is_source_in_use(source_id) -> bool` - Check if source used in workflows | | |
| TASK-039 | Write unit tests for all repository functions | | |
| TASK-040 | Test credential validation: Reject configs with hardcoded API keys | | |

**Acceptance Criteria:**
- ✅ All CRUD operations implemented
- ✅ Tenant isolation enforced
- ✅ Source kind validation (llm, image, db, api)
- ✅ Cannot delete sources in use by workflows
- ✅ Credentials stored as env var references only
- ✅ Unit tests pass with >80% coverage

---

### Implementation Phase 2.4: Execution History Repository

**GOAL-004**: Implement repository for storing and querying workflow execution history

| Task | Description | Completed | Date |
|------|-------------|-----------|------|
| TASK-041 | Create `backend/agentflow_core/db/repositories/execution_repository.py` with factory function | | |
| TASK-042 | Implement `create_execution(workflow_id, initial_state) -> Execution` - Generate ID (`exec_` prefix), set started_at, status='RUNNING' | | |
| TASK-043 | Implement `get_execution_by_id(execution_id) -> Execution | None` - Query by ID and tenant_id | | |
| TASK-044 | Implement `list_executions_by_workflow(workflow_id, skip, limit) -> List[Execution]` - Get execution history for workflow | | |
| TASK-045 | Implement `list_all_executions(skip, limit, status) -> List[Execution]` - List all executions for tenant | | |
| TASK-046 | Implement `update_execution_status(execution_id, status, final_state, error_message) -> Execution` - Update execution result | | |
| TASK-047 | Implement `complete_execution(execution_id, final_state, tokens_used, cost) -> Execution` - Mark execution complete, set completed_at, calculate duration | | |
| TASK-048 | Implement `fail_execution(execution_id, error_message) -> Execution` - Mark execution failed | | |
| TASK-049 | Implement `count_executions(workflow_id, status) -> int` - Count for pagination | | |
| TASK-050 | Add query: Get execution statistics (total, succeeded, failed, avg duration) for workflow | | |
| TASK-051 | Write unit tests for all repository functions | | |
| TASK-052 | Test execution lifecycle: RUNNING → COMPLETED/FAILED | | |

**Acceptance Criteria:**
- ✅ Execution lifecycle tracked (RUNNING, COMPLETED, FAILED)
- ✅ Duration calculated automatically
- ✅ Final state and error messages stored
- ✅ Execution history queryable by workflow
- ✅ Execution statistics computed correctly
- ✅ Unit tests pass with >80% coverage

---

### Implementation Phase 2.5: Workflow CRUD API Endpoints

**GOAL-005**: Implement REST API endpoints for workflow CRUD operations

| Task | Description | Completed | Date |
|------|-------------|-----------|------|
| TASK-053 | Update `api/routes/workflows.py` to include database dependency injection | | |
| TASK-054 | Implement `POST /workflows` - Create workflow endpoint (validates spec, saves to database, returns workflow ID) | | |
| TASK-055 | Implement `GET /workflows` - List workflows endpoint (pagination with skip/limit, filter by status) | | |
| TASK-056 | Implement `GET /workflows/{id}` - Get workflow by ID endpoint | | |
| TASK-057 | Implement `PUT /workflows/{id}` - Update workflow endpoint (validates new spec before updating) | | |
| TASK-058 | Implement `DELETE /workflows/{id}` - Delete workflow endpoint (soft delete) | | |
| TASK-059 | Add Pydantic request/response models: `CreateWorkflowRequest`, `UpdateWorkflowRequest`, `WorkflowResponse`, `WorkflowListResponse` | | |
| TASK-060 | Add pagination metadata to list response (total, skip, limit, has_more) | | |
| TASK-061 | Update `POST /workflows/execute` to optionally load workflow from database by ID instead of inline spec | | |
| TASK-062 | Add error handling: 404 for not found, 400 for validation errors, 403 for wrong tenant | | |
| TASK-063 | Add OpenAPI documentation for all endpoints with examples | | |
| TASK-064 | Write API integration tests using TestClient | | |

**Acceptance Criteria:**
- ✅ All CRUD endpoints implemented and documented
- ✅ Validation runs before create/update
- ✅ Pagination works correctly
- ✅ Execute can load workflow from database
- ✅ Error responses are consistent
- ✅ OpenAPI docs generated correctly
- ✅ Integration tests pass

---

### Implementation Phase 2.6: Source CRUD API Endpoints

**GOAL-006**: Implement REST API endpoints for source CRUD operations

| Task | Description | Completed | Date |
|------|-------------|-----------|------|
| TASK-065 | Update `api/routes/sources.py` to include database dependency injection | | |
| TASK-066 | Implement `POST /sources` - Create source endpoint (validates config, saves to database) | | |
| TASK-067 | Implement `GET /sources` - List sources endpoint (pagination, filter by kind) | | |
| TASK-068 | Implement `GET /sources/{id}` - Get source by ID endpoint | | |
| TASK-069 | Implement `PUT /sources/{id}` - Update source endpoint (validates config) | | |
| TASK-070 | Implement `DELETE /sources/{id}` - Delete source endpoint (soft delete, checks if in use) | | |
| TASK-071 | Add Pydantic models: `CreateSourceRequest`, `UpdateSourceRequest`, `SourceResponse`, `SourceListResponse` | | |
| TASK-072 | Add validation: Reject delete if source is referenced by workflows | | |
| TASK-073 | Add validation: Ensure config contains only env var references for credentials | | |
| TASK-074 | Add OpenAPI documentation with examples for each source kind (llm, image, db, api) | | |
| TASK-075 | Write API integration tests | | |
| TASK-076 | Test error case: Cannot delete source in use | | |

**Acceptance Criteria:**
- ✅ All source CRUD endpoints implemented
- ✅ Cannot delete sources in use
- ✅ Credential validation enforced
- ✅ OpenAPI docs include examples for each kind
- ✅ Integration tests pass
- ✅ Error handling consistent

---

### Implementation Phase 2.7: Rate Limiting with Redis

**GOAL-007**: Implement queue-based rate limiting using Redis with token bucket algorithm

| Task | Description | Completed | Date |
|------|-------------|-----------|------|
| TASK-077 | Install Redis dependencies: `pip install redis aioredis` | | |
| TASK-078 | Create `backend/agentflow_core/runtime/rate_limiter.py` with factory function `create_rate_limiter(redis_client, queue_config)` | | |
| TASK-079 | Implement token bucket algorithm: `check_rate_limit(queue_id) -> bool` - Returns True if request allowed | | |
| TASK-080 | Implement `max_messages_per_second` limit using sliding window counter in Redis | | |
| TASK-081 | Implement `max_requests_per_minute` limit using sliding window counter | | |
| TASK-082 | Implement `max_tokens_per_minute` limit (for LLM tokens) using sliding window counter | | |
| TASK-083 | Create Redis key structure: `rate_limit:{queue_id}:{metric}:{window}` | | |
| TASK-084 | Set TTL on Redis keys to prevent memory leak | | |
| TASK-085 | Implement `increment_counter(queue_id, metric, amount)` - Increment counter after request | | |
| TASK-086 | Implement `get_current_usage(queue_id, metric) -> int` - Get current usage for observability | | |
| TASK-087 | Add backpressure handling: Return 429 Too Many Requests when limit exceeded | | |
| TASK-088 | Integrate rate limiter into workflow executor: Check limits before executing node | | |
| TASK-089 | Add configuration: Load Redis URL from environment variable | | |
| TASK-090 | Write unit tests using fakeredis for rate limiting logic | | |
| TASK-091 | Write integration tests with real Redis instance | | |
| TASK-092 | Test distributed rate limiting: Multiple API instances share limits | | |

**Acceptance Criteria:**
- ✅ Token bucket algorithm implemented correctly
- ✅ All three limit types enforced (messages/sec, requests/min, tokens/min)
- ✅ Rate limits work with distributed Redis backend
- ✅ 429 error returned when limit exceeded
- ✅ Redis keys have TTL to prevent memory leak
- ✅ Unit tests pass with >80% coverage
- ✅ Integration tests with real Redis pass

---

### Implementation Phase 2.8: HTTP API Source Adapter

**GOAL-008**: Implement HTTP API source adapter for calling external REST APIs

| Task | Description | Completed | Date |
|------|-------------|-----------|------|
| TASK-093 | Install httpx: `pip install httpx` | | |
| TASK-094 | Create `backend/agentflow_core/sources/api_http.py` with factory function `create_http_source(config)` | | |
| TASK-095 | Implement `call_api(method, endpoint, headers, body) -> dict` - Make HTTP request | | |
| TASK-096 | Support HTTP methods: GET, POST, PUT, DELETE, PATCH | | |
| TASK-097 | Implement authentication methods: API key (header), Bearer token, Basic auth | | |
| TASK-098 | Implement request body templating: Substitute variables from state | | |
| TASK-099 | Implement response parsing: JSON, text, binary | | |
| TASK-100 | Add retry logic with exponential backoff (max 3 retries) | | |
| TASK-101 | Add timeout configuration (default 30s) | | |
| TASK-102 | Handle HTTP errors: 4xx client errors, 5xx server errors | | |
| TASK-103 | Add request/response logging for debugging | | |
| TASK-104 | Update HTTP API node to use new source adapter | | |
| TASK-105 | Write unit tests with mocked httpx responses | | |
| TASK-106 | Write integration tests with real API endpoint (httpbin.org) | | |

**Acceptance Criteria:**
- ✅ All HTTP methods supported
- ✅ Multiple authentication methods work
- ✅ Variable substitution in requests
- ✅ Retry logic works on transient failures
- ✅ Timeout enforced
- ✅ Error handling for 4xx/5xx
- ✅ Unit tests pass
- ✅ Integration tests with real API pass

---

### Implementation Phase 2.9: Execution Timeout Manager

**GOAL-009**: Implement timeout management to prevent runaway workflow executions

| Task | Description | Completed | Date |
|------|-------------|-----------|------|
| TASK-107 | Create `backend/agentflow_core/runtime/timeout_manager.py` with factory function | | |
| TASK-108 | Implement `execute_with_timeout(workflow_fn, timeout_seconds) -> result` using asyncio.wait_for | | |
| TASK-109 | Add per-node timeout configuration in node metadata | | |
| TASK-110 | Add global workflow timeout configuration | | |
| TASK-111 | Implement timeout error handling: Raise TimeoutError with context (node ID, elapsed time) | | |
| TASK-112 | Update workflow executor to use timeout manager | | |
| TASK-113 | On timeout, save partial execution state to database | | |
| TASK-114 | Add timeout metrics: Track timeout frequency per workflow | | |
| TASK-115 | Write unit tests: Verify timeout triggers correctly | | |
| TASK-116 | Write integration test: Execute workflow that exceeds timeout | | |

**Acceptance Criteria:**
- ✅ Global workflow timeout enforced
- ✅ Per-node timeout configurable
- ✅ Timeout error includes context
- ✅ Partial state saved on timeout
- ✅ Metrics track timeout frequency
- ✅ Unit tests pass
- ✅ Integration test verifies timeout behavior

---

### Implementation Phase 2.10: Connection Pooling

**GOAL-010**: Implement database connection pooling for improved performance

| Task | Description | Completed | Date |
|------|-------------|-----------|------|
| TASK-117 | Configure SQLAlchemy connection pool in `db/base.py` | | |
| TASK-118 | Set pool_size=20, max_overflow=10, pool_timeout=30, pool_recycle=3600 | | |
| TASK-119 | Add connection health checks: Ping database before using connection | | |
| TASK-120 | Implement automatic reconnection on connection loss | | |
| TASK-121 | Add connection pool metrics: Active connections, pool size, overflow | | |
| TASK-122 | Log connection pool events: Connection created, connection recycled, pool overflow | | |
| TASK-123 | Add environment variables for pool configuration | | |
| TASK-124 | Write tests: Verify pool reuses connections | | |
| TASK-125 | Write load test: Verify pool handles concurrent requests | | |
| TASK-126 | Monitor for connection leaks in tests | | |

**Acceptance Criteria:**
- ✅ Connection pool configured with optimal settings
- ✅ Connections reused across requests
- ✅ Health checks prevent stale connections
- ✅ Automatic reconnection on failure
- ✅ Pool metrics available
- ✅ No connection leaks
- ✅ Load test passes (100+ concurrent requests)

---

### Implementation Phase 2.11: Tenant Isolation Enforcement

**GOAL-011**: Enforce tenant isolation at all database query levels

| Task | Description | Completed | Date |
|------|-------------|-----------|------|
| TASK-127 | Create `backend/agentflow_core/api/dependencies.py` for FastAPI dependencies | | |
| TASK-128 | Implement `get_current_tenant(api_key: str) -> Tenant` - Extract tenant from API key | | |
| TASK-129 | Update all API endpoints to inject tenant_id via Depends(get_current_tenant) | | |
| TASK-130 | Update all repository functions to require tenant_id parameter | | |
| TASK-131 | Add SQLAlchemy query event listener to auto-inject tenant filter (safety net) | | |
| TASK-132 | Create audit decorator `@enforce_tenant_isolation` for repository functions | | |
| TASK-133 | Add logging: Log all database queries with tenant_id | | |
| TASK-134 | Write security tests: Verify tenant A cannot access tenant B data | | |
| TASK-135 | Write test: Verify queries without tenant filter fail (if using event listener) | | |
| TASK-136 | Document tenant isolation in security guide | | |

**Acceptance Criteria:**
- ✅ All endpoints inject tenant_id
- ✅ All repository queries filter by tenant_id
- ✅ SQLAlchemy event listener enforces tenant filter
- ✅ Cross-tenant access prevented
- ✅ Security tests pass
- ✅ Documentation complete

---

### Implementation Phase 2.12: Error Tracking Integration

**GOAL-012**: Integrate error tracking service (Sentry) for production error monitoring

| Task | Description | Completed | Date |
|------|-------------|-----------|------|
| TASK-137 | Install Sentry SDK: `pip install sentry-sdk[fastapi]` | | |
| TASK-138 | Create `backend/agentflow_core/utils/sentry.py` for Sentry configuration | | |
| TASK-139 | Initialize Sentry in FastAPI app startup with DSN from environment | | |
| TASK-140 | Configure Sentry options: Environment, release, traces_sample_rate | | |
| TASK-141 | Add custom context to errors: tenant_id, workflow_id, execution_id | | |
| TASK-142 | Configure error sampling: 100% for production, 0% for development | | |
| TASK-143 | Add breadcrumbs for key operations: Workflow execution started, node executed | | |
| TASK-144 | Filter sensitive data from error reports (API keys, credentials) | | |
| TASK-145 | Test error reporting: Trigger test error and verify in Sentry dashboard | | |
| TASK-146 | Add Sentry alerts: Notify on critical errors | | |
| TASK-147 | Document Sentry configuration in deployment guide | | |

**Acceptance Criteria:**
- ✅ Sentry SDK integrated into FastAPI app
- ✅ Errors reported to Sentry automatically
- ✅ Custom context included (tenant, workflow, execution)
- ✅ Sensitive data filtered from reports
- ✅ Breadcrumbs provide execution trace
- ✅ Test error appears in Sentry dashboard
- ✅ Documentation complete

---

### Implementation Phase 2.13: API Documentation Enhancement

**GOAL-013**: Enhance OpenAPI documentation with examples, descriptions, and response schemas

| Task | Description | Completed | Date |
|------|-------------|-----------|------|
| TASK-148 | Add detailed docstrings to all API endpoint functions | | |
| TASK-149 | Add Pydantic schema examples for all request models | | |
| TASK-150 | Add Pydantic schema examples for all response models | | |
| TASK-151 | Configure FastAPI OpenAPI metadata: Title, description, version, contact | | |
| TASK-152 | Add tags for endpoint grouping: Workflows, Sources, Executions | | |
| TASK-153 | Add response examples for success cases (200, 201) | | |
| TASK-154 | Add response examples for error cases (400, 404, 429, 500) | | |
| TASK-155 | Add authentication documentation in OpenAPI schema | | |
| TASK-156 | Test OpenAPI docs in Swagger UI: http://localhost:8000/docs | | |
| TASK-157 | Test ReDoc UI: http://localhost:8000/redoc | | |
| TASK-158 | Generate OpenAPI JSON schema: http://localhost:8000/openapi.json | | |
| TASK-159 | Add Markdown guide: "Getting Started with AgentFlow API" | | |

**Acceptance Criteria:**
- ✅ All endpoints have detailed descriptions
- ✅ All models have examples
- ✅ Error responses documented
- ✅ Authentication documented
- ✅ Swagger UI works correctly
- ✅ OpenAPI JSON generates without errors
- ✅ Getting started guide complete

---

### Implementation Phase 2.14: Integration Testing & Validation

**GOAL-014**: Comprehensive integration testing for all Phase 2 features

| Task | Description | Completed | Date |
|------|-------------|-----------|------|
| TASK-160 | Create test database setup: Create test PostgreSQL database and Redis instance | | |
| TASK-161 | Write integration test: Create workflow via API, retrieve it, update it, delete it | | |
| TASK-162 | Write integration test: Create source, use it in workflow, verify cannot delete while in use | | |
| TASK-163 | Write integration test: Execute workflow, verify execution history stored | | |
| TASK-164 | Write integration test: Rate limiting - Exceed limit and verify 429 response | | |
| TASK-165 | Write integration test: HTTP API node - Call external API and verify response | | |
| TASK-166 | Write integration test: Timeout - Workflow exceeds timeout and fails gracefully | | |
| TASK-167 | Write integration test: Tenant isolation - Verify tenant A cannot access tenant B data | | |
| TASK-168 | Write integration test: Connection pooling - 100 concurrent requests, verify pool works | | |
| TASK-169 | Write integration test: Alembic migrations - Apply and rollback migrations | | |
| TASK-170 | Write load test: 1000 workflow executions, measure throughput and latency | | |
| TASK-171 | Run all tests and verify >80% code coverage | | |

**Acceptance Criteria:**
- ✅ All integration tests pass
- ✅ Test coverage >80%
- ✅ Load test shows acceptable performance (>10 req/s)
- ✅ No test failures or flaky tests
- ✅ Test database cleanup works correctly

---

## 3. Dependencies

### Internal Dependencies

- **DEP-001**: Phase 1 Backend MVP - All Phase 1 features must be complete
- **DEP-002**: WorkflowSpec JSON Schema - Database stores workflow spec as JSONB
- **DEP-003**: Pydantic Models - Used for API request/response validation
- **DEP-004**: Workflow Validator - Used before creating/updating workflows
- **DEP-005**: Workflow Executor - Extended to track executions in database
- **DEP-006**: Runtime Registry - Extended to load sources from database

### External Dependencies

- **DEP-007**: PostgreSQL 14+ - Database for persistence
- **DEP-008**: Redis 7+ - Cache and rate limiting backend
- **DEP-009**: Alembic 1.12+ - Database migrations
- **DEP-010**: SQLAlchemy 2.0+ - ORM for database access
- **DEP-011**: psycopg2-binary 2.9+ - PostgreSQL driver
- **DEP-012**: httpx 0.24+ - Async HTTP client
- **DEP-013**: sentry-sdk 1.35+ - Error tracking
- **DEP-014**: aioredis 2.0+ - Async Redis client

### Environment Variables

```bash
# Database
DATABASE_URL="postgresql+asyncpg://user:password@localhost:5432/agentflow"

# Redis
REDIS_URL="redis://localhost:6379"

# Sentry
SENTRY_DSN="https://...@sentry.io/..."
SENTRY_ENVIRONMENT="production"

# Connection Pool
DB_POOL_SIZE="20"
DB_MAX_OVERFLOW="10"
DB_POOL_TIMEOUT="30"

# Rate Limiting (defaults)
RATE_LIMIT_MESSAGES_PER_SECOND="10"
RATE_LIMIT_REQUESTS_PER_MINUTE="100"
RATE_LIMIT_TOKENS_PER_MINUTE="10000"
```

---

## 4. Files

### New Files

1. **migrations/** - Alembic migration directory
   - `env.py` - Alembic environment configuration
   - `script.py.mako` - Migration template
   - `versions/` - Migration version files

2. **backend/agentflow_core/db/** - Database layer
   - `__init__.py`
   - `base.py` - SQLAlchemy base and session factory
   - `models/__init__.py`
   - `models/workflow.py` - Workflow database model
   - `models/source.py` - Source database model
   - `models/execution.py` - Execution database model
   - `repositories/__init__.py`
   - `repositories/workflow_repository.py` - Workflow CRUD operations
   - `repositories/source_repository.py` - Source CRUD operations
   - `repositories/execution_repository.py` - Execution tracking

3. **backend/agentflow_core/runtime/timeout_manager.py** - Timeout management

4. **backend/agentflow_core/utils/sentry.py** - Sentry error tracking configuration

5. **backend/agentflow_core/api/dependencies.py** - FastAPI dependency injection functions

6. **scripts/init_db.py** - Database initialization script

### Modified Files

1. **backend/agentflow_core/api/main.py** - Add database and Sentry initialization
2. **backend/agentflow_core/api/routes/workflows.py** - Add CRUD endpoints
3. **backend/agentflow_core/api/routes/sources.py** - Add CRUD endpoints
4. **backend/agentflow_core/runtime/executor.py** - Add execution tracking and timeout
5. **backend/agentflow_core/runtime/rate_limiter.py** - Implement with Redis
6. **backend/agentflow_core/sources/api_http.py** - Complete HTTP source implementation
7. **backend/requirements.txt** - Add new dependencies
8. **backend/pyproject.toml** - Update version and dependencies

---

## 5. Testing Strategy

### Unit Tests (Coverage Target: 80%+)

- **test_db_models.py** - Test SQLAlchemy model definitions
- **test_workflow_repository.py** - Test workflow CRUD operations (in-memory SQLite)
- **test_source_repository.py** - Test source CRUD operations
- **test_execution_repository.py** - Test execution tracking
- **test_rate_limiter.py** - Test rate limiting logic with fakeredis
- **test_timeout_manager.py** - Test timeout enforcement
- **test_http_source.py** - Test HTTP API source with mocked responses

### Integration Tests

- **test_workflow_crud_api.py** - Test workflow CRUD endpoints end-to-end
- **test_source_crud_api.py** - Test source CRUD endpoints
- **test_execution_api.py** - Test execution tracking via API
- **test_rate_limiting_integration.py** - Test rate limiting with real Redis
- **test_http_source_integration.py** - Test HTTP source with real API
- **test_tenant_isolation.py** - Test cross-tenant access prevention
- **test_migrations.py** - Test Alembic migration apply/rollback

### Load Tests

- **test_concurrent_executions.py** - 100+ concurrent workflow executions
- **test_connection_pool.py** - Verify connection pooling under load
- **test_rate_limiter_load.py** - Rate limiter under high request volume

### Test Commands

```bash
# Run all tests with coverage
pytest tests/ --cov=agentflow_core --cov-report=html --cov-report=term

# Run only unit tests
pytest tests/unit/

# Run only integration tests
pytest tests/integration/

# Run specific test file
pytest tests/integration/test_workflow_crud_api.py -v

# Run with database setup
docker-compose up -d postgres redis
pytest tests/integration/ --db-url="postgresql://test:test@localhost:5432/test_db"
docker-compose down
```

---

## 6. Success Criteria

Phase 2 is complete when all of the following are met:

### Database & Persistence

✅ **Criterion 1**: Alembic migrations configured and initial migration applied successfully  
✅ **Criterion 2**: All three database models (Workflow, Source, Execution) defined with indexes  
✅ **Criterion 3**: Migrations can be applied and rolled back without errors  
✅ **Criterion 4**: Database connection pooling configured with health checks

### Repositories

✅ **Criterion 5**: Workflow repository implements all CRUD operations with tenant isolation  
✅ **Criterion 6**: Source repository implements all CRUD operations with validation  
✅ **Criterion 7**: Execution repository tracks full execution lifecycle  
✅ **Criterion 8**: Repository unit tests pass with >80% coverage

### API Endpoints

✅ **Criterion 9**: Workflow CRUD endpoints (POST, GET, PUT, DELETE) implemented and documented  
✅ **Criterion 10**: Source CRUD endpoints implemented and documented  
✅ **Criterion 11**: Execute endpoint extended to load workflows from database  
✅ **Criterion 12**: All endpoints return consistent error responses (400, 404, 429, 500)

### Rate Limiting

✅ **Criterion 13**: Redis-backed rate limiting implemented with token bucket algorithm  
✅ **Criterion 14**: All three limit types enforced (messages/sec, requests/min, tokens/min)  
✅ **Criterion 15**: 429 Too Many Requests returned when limit exceeded  
✅ **Criterion 16**: Distributed rate limiting works across multiple API instances

### HTTP API Source

✅ **Criterion 17**: HTTP API source supports all HTTP methods (GET, POST, PUT, DELETE)  
✅ **Criterion 18**: Multiple authentication methods implemented (API key, Bearer, Basic)  
✅ **Criterion 19**: Retry logic with exponential backoff works correctly  
✅ **Criterion 20**: Timeout enforced on HTTP requests

### Operational Features

✅ **Criterion 21**: Execution timeout manager prevents runaway workflows  
✅ **Criterion 22**: Partial state saved when timeout occurs  
✅ **Criterion 23**: Sentry error tracking integrated and errors reported correctly  
✅ **Criterion 24**: Connection pool handles 100+ concurrent requests without leaks

### Security & Isolation

✅ **Criterion 25**: Tenant isolation enforced in all database queries  
✅ **Criterion 26**: Security test confirms cross-tenant access prevention  
✅ **Criterion 27**: Source credentials stored as env var references only  
✅ **Criterion 28**: Cannot delete source in use by workflows

### Documentation & Testing

✅ **Criterion 29**: OpenAPI documentation complete with examples for all endpoints  
✅ **Criterion 30**: Integration tests pass for all Phase 2 features  
✅ **Criterion 31**: Code coverage >80% for new code  
✅ **Criterion 32**: Load test shows >10 req/s throughput  
✅ **Criterion 33**: Getting started guide updated with new endpoints

---

## 7. Risks & Mitigation

### Risk 1: Database Migration Failures in Production

**Impact:** High - Could cause downtime or data loss  
**Probability:** Medium  
**Mitigation:**
- Test migrations thoroughly in staging environment
- Use Alembic's `--sql` flag to review SQL before applying
- Implement zero-downtime migration strategy (add before remove)
- Always create database backup before migration
- Have rollback plan ready

### Risk 2: Rate Limiting Redis Single Point of Failure

**Impact:** High - Rate limiting stops working if Redis unavailable  
**Probability:** Low  
**Mitigation:**
- Use Redis Sentinel for high availability
- Implement fallback: Allow requests if Redis unavailable (log warning)
- Monitor Redis health with alerts
- Consider Redis Cluster for production

### Risk 3: Connection Pool Exhaustion

**Impact:** Medium - API becomes unresponsive under high load  
**Probability:** Medium  
**Mitigation:**
- Configure appropriate pool size based on load testing
- Monitor active connections with metrics
- Implement connection timeout and health checks
- Alert on pool exhaustion events
- Document pool tuning guidelines

### Risk 4: Tenant Isolation Bypass Vulnerability

**Impact:** Critical - Data leakage between tenants  
**Probability:** Low  
**Mitigation:**
- Enforce tenant_id in all queries (no exceptions)
- Add SQLAlchemy event listener as safety net
- Conduct security audit of all queries
- Write comprehensive security tests
- Code review all database access code

### Risk 5: HTTP Source Credential Exposure

**Impact:** High - API keys exposed in logs or error messages  
**Probability:** Medium  
**Mitigation:**
- Never log request bodies or headers with auth
- Filter sensitive data from Sentry reports
- Validate config uses env var references only
- Encrypt config JSONB column at rest (future)
- Regular security audits

### Risk 6: Execution Timeout Edge Cases

**Impact:** Medium - Workflows fail unexpectedly or don't timeout  
**Probability:** Medium  
**Mitigation:**
- Test timeout with various workflow patterns
- Handle cleanup properly on timeout
- Save partial state for debugging
- Document timeout behavior clearly
- Allow timeout configuration per workflow

### Risk 7: Alembic Auto-Generate Mistakes

**Impact:** Medium - Migrations don't match models correctly  
**Probability:** Medium  
**Mitigation:**
- Always review auto-generated migrations
- Test migrations on copy of production data
- Keep models and migrations in sync
- Document manual migration tweaks
- Use migration naming conventions

---

## 8. Related Documents

- [Backend Features Master Document](./BACKEND-FEATURES.md)
- [Phase 1: Backend MVP Plan](./phase-1-backend-mvp-plan.md) - Prerequisite
- [Phase 3: Scalability & Observability Plan](./phase-3-backend-scale-plan.md) - Next phase
- [Backend README](./README.md)
- [API Documentation](../../../shared/docs/API_Spec.md)
- [Database Schema](../../06-DB-SCHEMA.md)

---

**Document Version:** 1.0  
**Last Updated:** December 7, 2025  
**Maintained By:** AgentFlow Backend Engineering Team  
**Estimated Duration:** 8 weeks  
**Total Tasks:** 171 tasks across 14 goals  
**Status:** Ready for Implementation 🚀
