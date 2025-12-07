---
goal: Phase 3 - Backend Scalability & Observability Implementation Plan
version: 1.0
date_created: 2025-12-07
last_updated: 2025-12-07
owner: AgentFlow Backend Engineering Team
status: 'Planned'
tags: ['backend', 'scalability', 'observability', 'monitoring', 'caching', 'phase-3']
---

# Phase 3: Backend Scalability & Observability Implementation Plan

![Status: Planned](https://img.shields.io/badge/status-Planned-blue)

This plan details the implementation of scalability, performance optimization, monitoring, and observability features for AgentFlow Core backend, including Redis caching, background job processing, Prometheus metrics, distributed tracing, and additional LLM provider integrations.

## 1. Requirements & Constraints

### Requirements

- **REQ-001**: Execution History - Store all workflow executions with full state history for auditing
- **REQ-002**: Redis Caching - Cache frequently accessed data (sources, compiled graphs) for performance
- **REQ-003**: Background Jobs - Long-running workflow executions must run in background using Celery
- **REQ-004**: Horizontal Scaling - Support multiple API instances with shared state in Redis
- **REQ-005**: Prometheus Metrics - Export metrics for monitoring (request count, duration, errors, tokens)
- **REQ-006**: Distributed Tracing - Trace requests across services using OpenTelemetry
- **REQ-007**: Performance Profiling - Profile API endpoints to identify bottlenecks
- **REQ-008**: Health Dashboard - Real-time system health monitoring dashboard
- **REQ-009**: Multi-Provider Support - Support Anthropic Claude, Google Gemini, Azure OpenAI
- **REQ-010**: MySQL Support - Support MySQL as alternative to PostgreSQL
- **REQ-011**: HTTP API Node - Full-featured HTTP API node for workflow integration
- **REQ-012**: Response Caching - Cache API responses with configurable TTL
- **REQ-013**: Audit Logging - Log all user actions for compliance
- **REQ-014**: Workflow Optimization - Optimize execution with parallel node execution where possible

### Performance Requirements

- **PERF-001**: API Latency - P95 latency <500ms for API endpoints
- **PERF-002**: Workflow Execution - Support 100+ concurrent workflow executions
- **PERF-003**: Cache Hit Rate - >80% cache hit rate for sources and compiled graphs
- **PERF-004**: Throughput - >50 requests/second with 3 API instances
- **PERF-005**: Database Queries - P95 query time <100ms

### Observability Requirements

- **OBS-001**: Metrics Export - Export all metrics to Prometheus every 15 seconds
- **OBS-002**: Trace Sampling - 10% trace sampling in production, 100% in development
- **OBS-003**: Log Aggregation - All logs aggregated in structured JSON format
- **OBS-004**: Alert Thresholds - Alerts for error rate >5%, latency P95 >1s, CPU >80%

### Constraints

- **CON-001**: Redis Memory - Limit Redis memory usage to 4GB with eviction policy
- **CON-002**: Celery Workers - Deploy at least 2 worker instances for redundancy
- **CON-003**: Prometheus Storage - Retain metrics for 30 days
- **CON-004**: Backward Compatibility - All Phase 1 & 2 APIs must continue to work
- **CON-005**: Python 3.11+ - Maintain Python version requirement

### Guidelines

- **GUD-001**: Cache Invalidation - Implement proper cache invalidation on updates
- **GUD-002**: Graceful Degradation - System should degrade gracefully if Redis/Celery unavailable
- **GUD-003**: Metrics Naming - Use Prometheus naming conventions (lowercase, underscores)
- **GUD-004**: Trace Context - Propagate trace context across all service calls
- **GUD-005**: Zero Downtime - All deployments must be zero-downtime

### Patterns to Follow

- **PAT-001**: Cache-Aside Pattern - Load from cache, fetch from DB on miss, update cache
- **PAT-002**: Circuit Breaker - Protect external service calls with circuit breaker
- **PAT-003**: Bulkhead Pattern - Isolate thread pools for different operations
- **PAT-004**: Retry with Backoff - Exponential backoff for transient failures
- **PAT-005**: Fan-out/Fan-in - Parallel node execution with result aggregation

---

## 2. Implementation Steps

### Implementation Phase 3.1: Execution History Storage & API

**GOAL-001**: Store complete execution history and provide query endpoints

| Task | Description | Completed | Date |
|------|-------------|-----------|------|
| TASK-001 | Extend execution model: Add `node_executions` JSONB field to store per-node execution data | | |
| TASK-002 | Add `execution_metadata` JSONB field: Store custom metadata, tags, labels | | |
| TASK-003 | Implement `save_node_execution(execution_id, node_id, input_state, output_state, duration, tokens, cost)` in execution repository | | |
| TASK-004 | Update workflow executor to call `save_node_execution()` after each node completes | | |
| TASK-005 | Implement `GET /workflows/{id}/executions` endpoint - List execution history for workflow with pagination | | |
| TASK-006 | Implement `GET /executions/{id}` endpoint - Get detailed execution with per-node breakdown | | |
| TASK-007 | Add execution statistics endpoint: `GET /workflows/{id}/stats` - Returns total executions, success rate, avg duration, total tokens, total cost | | |
| TASK-008 | Add execution filtering: Filter by status (RUNNING, COMPLETED, FAILED), date range | | |
| TASK-009 | Add execution search: Search by metadata, tags, input content | | |
| TASK-010 | Implement execution retention policy: Auto-delete executions older than 90 days (configurable) | | |
| TASK-011 | Add database indexes: executions(status), executions(started_at), executions(workflow_id, started_at) | | |
| TASK-012 | Write unit tests for execution repository functions | | |
| TASK-013 | Write API integration tests for execution endpoints | | |
| TASK-014 | Add OpenAPI documentation with examples | | |

**Acceptance Criteria:**
- ✅ Per-node execution data stored in database
- ✅ Execution history queryable by workflow
- ✅ Execution statistics computed correctly
- ✅ Filtering and search work correctly
- ✅ Retention policy deletes old executions
- ✅ Integration tests pass
- ✅ OpenAPI docs complete

---

### Implementation Phase 3.2: Redis Caching Layer

**GOAL-002**: Implement Redis caching for sources, compiled graphs, and validation results

| Task | Description | Completed | Date |
|------|-------------|-----------|------|
| TASK-015 | Create `backend/agentflow_core/cache/__init__.py` | | |
| TASK-016 | Create `backend/agentflow_core/cache/redis_cache.py` with factory function `create_redis_cache(redis_client)` | | |
| TASK-017 | Implement `get(key) -> Any` - Get value from cache, return None if not found | | |
| TASK-018 | Implement `set(key, value, ttl) -> bool` - Set value with TTL in seconds | | |
| TASK-019 | Implement `delete(key) -> bool` - Delete value from cache | | |
| TASK-020 | Implement `delete_pattern(pattern) -> int` - Delete all keys matching pattern | | |
| TASK-021 | Implement cache key generators: `source_cache_key(tenant_id, source_id)`, `workflow_cache_key(tenant_id, workflow_id)`, `validation_cache_key(workflow_hash)` | | |
| TASK-022 | Update source repository: Cache sources after load (TTL: 5 minutes) | | |
| TASK-023 | Update source repository: Invalidate cache on create/update/delete | | |
| TASK-024 | Update workflow validator: Cache validation results by workflow spec hash (TTL: 5 minutes) | | |
| TASK-025 | Update graph builder: Cache compiled graphs by workflow spec hash (TTL: 10 minutes) | | |
| TASK-026 | Implement cache warming: Pre-load frequently used sources on startup | | |
| TASK-027 | Add cache metrics: Hit rate, miss rate, size, evictions | | |
| TASK-028 | Configure Redis eviction policy: allkeys-lru (evict least recently used) | | |
| TASK-029 | Set Redis maxmemory: 4GB limit | | |
| TASK-030 | Write unit tests with fakeredis | | |
| TASK-031 | Write integration tests with real Redis | | |
| TASK-032 | Measure cache hit rate: Verify >80% hit rate for sources | | |

**Acceptance Criteria:**
- ✅ Redis cache layer implemented
- ✅ Sources cached with TTL
- ✅ Cache invalidation on updates
- ✅ Validation results cached
- ✅ Compiled graphs cached
- ✅ Cache hit rate >80%
- ✅ Metrics track cache performance
- ✅ Unit and integration tests pass

---

### Implementation Phase 3.3: Response Caching

**GOAL-003**: Cache API responses for read-heavy endpoints

| Task | Description | Completed | Date |
|------|-------------|-----------|------|
| TASK-033 | Create `backend/agentflow_core/api/middleware/cache_middleware.py` | | |
| TASK-034 | Implement FastAPI middleware: `ResponseCacheMiddleware` | | |
| TASK-035 | Cache `GET /workflows` responses (TTL: 60 seconds, key: tenant_id + query params) | | |
| TASK-036 | Cache `GET /workflows/{id}` responses (TTL: 300 seconds, key: tenant_id + workflow_id) | | |
| TASK-037 | Cache `GET /sources` responses (TTL: 300 seconds) | | |
| TASK-038 | Cache `GET /sources/{id}` responses (TTL: 300 seconds) | | |
| TASK-039 | Cache `POST /workflows/validate` responses (TTL: 300 seconds, key: hash(spec)) | | |
| TASK-040 | Implement cache key generation from request: Method + path + query params + body hash | | |
| TASK-041 | Add cache control headers: `Cache-Control`, `ETag`, `Last-Modified` | | |
| TASK-042 | Implement cache invalidation: Invalidate on PUT, POST, DELETE to same resource | | |
| TASK-043 | Add bypass mechanism: `Cache-Control: no-cache` header bypasses cache | | |
| TASK-044 | Add cache hit/miss logging | | |
| TASK-045 | Write tests: Verify cache hit on repeated requests | | |
| TASK-046 | Write tests: Verify cache invalidation on update | | |

**Acceptance Criteria:**
- ✅ Response caching middleware implemented
- ✅ GET endpoints cached with appropriate TTLs
- ✅ Cache invalidation works on mutations
- ✅ Cache control headers set correctly
- ✅ Tests verify caching behavior
- ✅ Cache hit rate >70% for GET requests

---

### Implementation Phase 3.4: Background Job Processing with Celery

**GOAL-004**: Implement background workflow execution using Celery

| Task | Description | Completed | Date |
|------|-------------|-----------|------|
| TASK-047 | Install Celery: `pip install celery[redis]` | | |
| TASK-048 | Create `backend/agentflow_core/workers/__init__.py` | | |
| TASK-049 | Create `backend/agentflow_core/workers/celery_app.py` - Initialize Celery app with Redis broker | | |
| TASK-050 | Configure Celery: Broker URL, result backend, task serializer (JSON), timezone | | |
| TASK-051 | Create Celery task: `@celery_app.task execute_workflow_async(workflow_id, initial_state, execution_id)` | | |
| TASK-052 | Implement task: Load workflow from database, execute, save results to execution record | | |
| TASK-053 | Add task retry logic: Retry on transient failures (max 3 retries, exponential backoff) | | |
| TASK-054 | Add task timeout: Configurable timeout (default 300 seconds) | | |
| TASK-055 | Implement `POST /workflows/execute/async` endpoint - Queue workflow execution, return job_id | | |
| TASK-056 | Implement `GET /jobs/{job_id}` endpoint - Query job status (PENDING, RUNNING, COMPLETED, FAILED) | | |
| TASK-057 | Implement `GET /jobs/{job_id}/result` endpoint - Get job result when complete | | |
| TASK-058 | Add job cancellation: `DELETE /jobs/{job_id}` - Cancel running job | | |
| TASK-059 | Configure Celery worker: Number of worker processes, concurrency, prefetch multiplier | | |
| TASK-060 | Create worker startup script: `scripts/start_celery_worker.sh` | | |
| TASK-061 | Add Celery monitoring: Flower web UI for worker monitoring | | |
| TASK-062 | Add worker health checks: Celery inspect ping | | |
| TASK-063 | Write tests: Queue job, wait for completion, verify result | | |
| TASK-064 | Write tests: Job cancellation | | |

**Acceptance Criteria:**
- ✅ Celery configured with Redis broker
- ✅ Async workflow execution task implemented
- ✅ API endpoints for job management
- ✅ Job status queryable
- ✅ Job cancellation works
- ✅ Worker monitoring with Flower
- ✅ Tests pass
- ✅ Workers scale independently from API

---

### Implementation Phase 3.5: Horizontal Scaling Support

**GOAL-005**: Enable multiple API instances with shared state

| Task | Description | Completed | Date |
|------|-------------|-----------|------|
| TASK-065 | Verify API is stateless: No in-memory state, all state in Redis/PostgreSQL | | |
| TASK-066 | Move runtime registry to Redis: Store sources in Redis instead of memory | | |
| TASK-067 | Implement distributed locks with Redis: Use for critical sections (e.g., workflow updates) | | |
| TASK-068 | Configure session affinity: Not required (API is stateless) | | |
| TASK-069 | Add instance ID to logs: Identify which instance handled request | | |
| TASK-070 | Test load balancing: Deploy 3 API instances behind load balancer | | |
| TASK-071 | Verify rate limiting: Distributed rate limits work across instances | | |
| TASK-072 | Verify cache coherence: Cache updates visible across instances | | |
| TASK-073 | Add health check endpoint: `GET /health` returns instance health | | |
| TASK-074 | Add readiness endpoint: `GET /ready` checks database and Redis connectivity | | |
| TASK-075 | Document deployment: Multi-instance setup guide | | |

**Acceptance Criteria:**
- ✅ API instances are fully stateless
- ✅ 3 instances run concurrently without conflicts
- ✅ Rate limiting distributed correctly
- ✅ Cache coherent across instances
- ✅ Health checks work correctly
- ✅ Documentation complete

---

### Implementation Phase 3.6: Workflow Execution Optimization

**GOAL-006**: Optimize workflow execution with parallel node execution

| Task | Description | Completed | Date |
|------|-------------|-----------|------|
| TASK-076 | Analyze workflow graph: Identify independent nodes that can run in parallel | | |
| TASK-077 | Implement parallel execution: Use asyncio.gather() for independent nodes | | |
| TASK-078 | Update graph builder: Mark edges as parallel-safe or sequential | | |
| TASK-079 | Implement execution planner: Create execution plan with parallel stages | | |
| TASK-080 | Update executor: Execute stages in parallel where possible | | |
| TASK-081 | Add execution metrics: Track parallel execution time savings | | |
| TASK-082 | Optimize LLM calls: Batch multiple prompts into single request (where supported) | | |
| TASK-083 | Optimize database queries: Use connection pooling, query batching | | |
| TASK-084 | Lazy load sources: Load sources only when needed, not upfront | | |
| TASK-085 | Implement result streaming: Stream results as nodes complete (for async execution) | | |
| TASK-086 | Add circuit breaker: Stop calling failing services temporarily | | |
| TASK-087 | Write benchmarks: Measure execution time before and after optimization | | |
| TASK-088 | Target: 50% reduction in execution time for workflows with parallel nodes | | |

**Acceptance Criteria:**
- ✅ Independent nodes execute in parallel
- ✅ Execution plan generated correctly
- ✅ 50% time reduction for parallel workflows
- ✅ LLM batch requests work
- ✅ Circuit breaker protects failing services
- ✅ Benchmarks show performance improvement

---

### Implementation Phase 3.7: Prometheus Metrics Export

**GOAL-007**: Export comprehensive metrics to Prometheus

| Task | Description | Completed | Date |
|------|-------------|-----------|------|
| TASK-089 | Install Prometheus client: `pip install prometheus-client` | | |
| TASK-090 | Create `backend/agentflow_core/monitoring/__init__.py` | | |
| TASK-091 | Create `backend/agentflow_core/monitoring/metrics.py` | | |
| TASK-092 | Define Counter: `http_requests_total` (labels: method, endpoint, status_code) | | |
| TASK-093 | Define Histogram: `http_request_duration_seconds` (labels: method, endpoint) | | |
| TASK-094 | Define Counter: `workflow_executions_total` (labels: workflow_id, status) | | |
| TASK-095 | Define Histogram: `workflow_execution_duration_seconds` (labels: workflow_id) | | |
| TASK-096 | Define Counter: `llm_tokens_total` (labels: source_id, model) | | |
| TASK-097 | Define Counter: `errors_total` (labels: error_type, endpoint) | | |
| TASK-098 | Define Gauge: `active_executions` (current number of running workflows) | | |
| TASK-099 | Define Gauge: `database_connections_active` | | |
| TASK-100 | Define Counter: `cache_hits_total` and `cache_misses_total` | | |
| TASK-101 | Add metrics middleware to FastAPI: Track request count and duration | | |
| TASK-102 | Update executor: Increment workflow metrics | | |
| TASK-103 | Update LLM nodes: Increment token metrics | | |
| TASK-104 | Update cache: Increment hit/miss metrics | | |
| TASK-105 | Implement metrics endpoint: `GET /metrics` (Prometheus text format) | | |
| TASK-106 | Configure Prometheus scrape: Add endpoint to prometheus.yml | | |
| TASK-107 | Create Grafana dashboard: Import dashboard JSON | | |
| TASK-108 | Write tests: Verify metrics increment correctly | | |

**Acceptance Criteria:**
- ✅ All key metrics defined
- ✅ Metrics updated during execution
- ✅ /metrics endpoint exports Prometheus format
- ✅ Prometheus scrapes successfully
- ✅ Grafana dashboard displays metrics
- ✅ Tests verify metrics accuracy

---

### Implementation Phase 3.8: Distributed Tracing with OpenTelemetry

**GOAL-008**: Implement distributed tracing for request tracking

| Task | Description | Completed | Date |
|------|-------------|-----------|------|
| TASK-109 | Install OpenTelemetry: `pip install opentelemetry-api opentelemetry-sdk opentelemetry-instrumentation-fastapi opentelemetry-exporter-jaeger` | | |
| TASK-110 | Create `backend/agentflow_core/monitoring/tracing.py` | | |
| TASK-111 | Initialize OpenTelemetry tracer in FastAPI app | | |
| TASK-112 | Configure Jaeger exporter: Set Jaeger endpoint from environment | | |
| TASK-113 | Configure sampling: 10% sampling in production, 100% in development | | |
| TASK-114 | Auto-instrument FastAPI: Use opentelemetry-instrumentation-fastapi | | |
| TASK-115 | Add custom spans: Workflow execution, node execution, LLM calls, database queries | | |
| TASK-116 | Add span attributes: workflow_id, node_id, tenant_id, source_id | | |
| TASK-117 | Propagate trace context: Add trace_id to logs for correlation | | |
| TASK-118 | Add span events: Mark key events (validation start, node complete, etc.) | | |
| TASK-119 | Configure trace baggage: Pass metadata across service boundaries | | |
| TASK-120 | Test tracing: Execute workflow and verify trace in Jaeger UI | | |
| TASK-121 | Document tracing setup: Deployment and configuration guide | | |

**Acceptance Criteria:**
- ✅ OpenTelemetry configured
- ✅ Jaeger exporter working
- ✅ FastAPI auto-instrumented
- ✅ Custom spans for key operations
- ✅ Trace context propagated
- ✅ Traces visible in Jaeger UI
- ✅ Documentation complete

---

### Implementation Phase 3.9: Performance Profiling

**GOAL-009**: Profile API performance and identify bottlenecks

| Task | Description | Completed | Date |
|------|-------------|-----------|------|
| TASK-122 | Install profiling tools: `pip install py-spy memory-profiler` | | |
| TASK-123 | Create `scripts/profile_api.py` - Script to profile API endpoints | | |
| TASK-124 | Add profiling endpoint: `POST /debug/profile` (dev/staging only) - Profile single request | | |
| TASK-125 | Profile workflow execution: Use py-spy to generate flamegraph | | |
| TASK-126 | Profile database queries: Log slow queries (>100ms) | | |
| TASK-127 | Profile LLM calls: Measure time to first token, total latency | | |
| TASK-128 | Profile memory usage: Use memory_profiler to find memory leaks | | |
| TASK-129 | Analyze results: Identify top 5 bottlenecks | | |
| TASK-130 | Document findings: Create performance optimization guide | | |
| TASK-131 | Implement fixes for top bottlenecks | | |
| TASK-132 | Re-profile after fixes: Verify improvements | | |

**Acceptance Criteria:**
- ✅ Profiling tools installed
- ✅ API endpoints profiled
- ✅ Flamegraphs generated
- ✅ Slow queries identified
- ✅ Top bottlenecks documented
- ✅ Performance improvements implemented
- ✅ Optimization guide complete

---

### Implementation Phase 3.10: Health Dashboard

**GOAL-010**: Real-time system health monitoring dashboard

| Task | Description | Completed | Date |
|------|-------------|-----------|------|
| TASK-133 | Create health metrics aggregation service | | |
| TASK-134 | Implement `GET /admin/health/overview` - System health summary | | |
| TASK-135 | Return metrics: API response times (P50, P95, P99), error rates, active executions, database status, Redis status, Celery workers status | | |
| TASK-136 | Implement `GET /admin/health/api` - API health details | | |
| TASK-137 | Implement `GET /admin/health/database` - Database connection pool status | | |
| TASK-138 | Implement `GET /admin/health/redis` - Redis memory usage, hit rate | | |
| TASK-139 | Implement `GET /admin/health/workers` - Celery worker status | | |
| TASK-140 | Add historical data: Store health snapshots every 15 seconds for last 1 hour | | |
| TASK-141 | Create simple HTML dashboard: `GET /admin/dashboard` (uses health endpoints) | | |
| TASK-142 | Add auto-refresh: Dashboard updates every 5 seconds | | |
| TASK-143 | Add status indicators: Green (healthy), yellow (degraded), red (critical) | | |
| TASK-144 | Add alerts section: Show active alerts (high error rate, slow response time, etc.) | | |
| TASK-145 | Protect dashboard: Require admin authentication | | |
| TASK-146 | Write tests: Verify health endpoints return correct data | | |

**Acceptance Criteria:**
- ✅ Health metrics endpoints implemented
- ✅ Dashboard displays real-time data
- ✅ Status indicators work correctly
- ✅ Historical data tracked
- ✅ Dashboard protected by authentication
- ✅ Tests pass

---

### Implementation Phase 3.11: Additional LLM Provider - Anthropic Claude

**GOAL-011**: Add support for Anthropic Claude models

| Task | Description | Completed | Date |
|------|-------------|-----------|------|
| TASK-147 | Install Anthropic SDK: `pip install anthropic` | | |
| TASK-148 | Create `backend/agentflow_core/sources/llm_anthropic.py` | | |
| TASK-149 | Implement factory function: `create_anthropic_source(config)` | | |
| TASK-150 | Implement `call_llm(prompt, model, temperature, max_tokens) -> str` | | |
| TASK-151 | Support models: claude-3-opus, claude-3-sonnet, claude-3-haiku | | |
| TASK-152 | Implement token counting: Use Anthropic's token counting API | | |
| TASK-153 | Implement streaming support (optional for future) | | |
| TASK-154 | Add error handling: Rate limits, invalid API key, context length exceeded | | |
| TASK-155 | Add retry logic: Exponential backoff on rate limits | | |
| TASK-156 | Update source registry: Register Anthropic as "llm_anthropic" | | |
| TASK-157 | Update LLM node: Support Anthropic sources | | |
| TASK-158 | Add configuration example in documentation | | |
| TASK-159 | Write unit tests with mocked Anthropic responses | | |
| TASK-160 | Write integration test with real Anthropic API | | |

**Acceptance Criteria:**
- ✅ Anthropic SDK integrated
- ✅ Claude models supported
- ✅ Token counting works
- ✅ Error handling for rate limits
- ✅ Retry logic implemented
- ✅ Unit and integration tests pass
- ✅ Documentation includes Anthropic example

---

### Implementation Phase 3.12: Additional LLM Provider - Google Gemini

**GOAL-012**: Add support for Google Gemini models

| Task | Description | Completed | Date |
|------|-------------|-----------|------|
| TASK-161 | Install Google AI SDK: `pip install google-generativeai` | | |
| TASK-162 | Create `backend/agentflow_core/sources/llm_google.py` | | |
| TASK-163 | Implement factory function: `create_google_source(config)` | | |
| TASK-164 | Implement `call_llm(prompt, model, temperature, max_tokens) -> str` | | |
| TASK-165 | Support models: gemini-pro, gemini-pro-vision | | |
| TASK-166 | Implement token counting: Use Google's count_tokens API | | |
| TASK-167 | Add error handling: Rate limits, invalid API key, safety filters | | |
| TASK-168 | Add retry logic | | |
| TASK-169 | Update source registry: Register Google as "llm_google" | | |
| TASK-170 | Update LLM node: Support Google sources | | |
| TASK-171 | Add configuration example | | |
| TASK-172 | Write unit tests | | |
| TASK-173 | Write integration test with real Google API | | |

**Acceptance Criteria:**
- ✅ Google SDK integrated
- ✅ Gemini models supported
- ✅ Token counting works
- ✅ Error handling complete
- ✅ Unit and integration tests pass
- ✅ Documentation complete

---

### Implementation Phase 3.13: Additional LLM Provider - Azure OpenAI

**GOAL-013**: Add support for Azure OpenAI Service

| Task | Description | Completed | Date |
|------|-------------|-----------|------|
| TASK-174 | Install Azure SDK: `pip install openai` (same SDK, different endpoint) | | |
| TASK-175 | Create `backend/agentflow_core/sources/llm_azure_openai.py` | | |
| TASK-176 | Implement factory function: `create_azure_openai_source(config)` | | |
| TASK-177 | Configure Azure endpoint: Use azure_endpoint and api_version from config | | |
| TASK-178 | Implement `call_llm(prompt, deployment_name, temperature, max_tokens) -> str` | | |
| TASK-179 | Support Azure deployments: Custom deployment names | | |
| TASK-180 | Implement token counting: Same as OpenAI | | |
| TASK-181 | Add error handling: Azure-specific errors | | |
| TASK-182 | Add retry logic | | |
| TASK-183 | Update source registry: Register Azure as "llm_azure_openai" | | |
| TASK-184 | Update LLM node: Support Azure sources | | |
| TASK-185 | Add configuration example | | |
| TASK-186 | Write unit tests | | |
| TASK-187 | Write integration test with real Azure OpenAI | | |

**Acceptance Criteria:**
- ✅ Azure OpenAI integrated
- ✅ Custom deployments supported
- ✅ Token counting works
- ✅ Error handling complete
- ✅ Unit and integration tests pass
- ✅ Documentation complete

---

### Implementation Phase 3.14: MySQL Database Source

**GOAL-014**: Add MySQL support as alternative to PostgreSQL

| Task | Description | Completed | Date |
|------|-------------|-----------|------|
| TASK-188 | Install MySQL driver: `pip install aiomysql` | | |
| TASK-189 | Create `backend/agentflow_core/sources/db_mysql.py` | | |
| TASK-190 | Implement factory function: `create_mysql_source(config)` | | |
| TASK-191 | Implement connection pooling | | |
| TASK-192 | Implement `execute_query(query, params) -> List[Dict]` | | |
| TASK-193 | Enforce read-only: Block INSERT, UPDATE, DELETE, DROP, CREATE | | |
| TASK-194 | Add query timeout (default 30s) | | |
| TASK-195 | Add SSL connection support | | |
| TASK-196 | Add error handling: Connection errors, timeout, syntax errors | | |
| TASK-197 | Update source registry: Register MySQL as "db_mysql" | | |
| TASK-198 | Update DB node: Support MySQL sources | | |
| TASK-199 | Add configuration example | | |
| TASK-200 | Write unit tests with MySQL test container | | |
| TASK-201 | Write integration test with real MySQL instance | | |

**Acceptance Criteria:**
- ✅ MySQL driver integrated
- ✅ Connection pooling works
- ✅ Read-only enforced
- ✅ Error handling complete
- ✅ Unit and integration tests pass
- ✅ Documentation complete

---

### Implementation Phase 3.15: HTTP API Node Enhancement

**GOAL-015**: Enhance HTTP API node with advanced features

| Task | Description | Completed | Date |
|------|-------------|-----------|------|
| TASK-202 | Create `backend/agentflow_core/nodes/api_node.py` (full implementation) | | |
| TASK-203 | Support all HTTP methods: GET, POST, PUT, PATCH, DELETE, HEAD, OPTIONS | | |
| TASK-204 | Implement request body templating: Variable substitution from state using Jinja2 | | |
| TASK-205 | Implement response parsing: JSON, XML, HTML, text, binary | | |
| TASK-206 | Add JSONPath extraction: Extract specific fields from JSON responses | | |
| TASK-207 | Add response validation: Validate against JSON schema | | |
| TASK-208 | Implement pagination support: Follow Link headers, page number pagination | | |
| TASK-209 | Add authentication: API key, Bearer token, Basic auth, OAuth2 | | |
| TASK-210 | Add custom headers: User-Agent, Accept, Content-Type | | |
| TASK-211 | Add request signing: HMAC, AWS Signature v4 | | |
| TASK-212 | Add circuit breaker: Stop calling failing APIs temporarily | | |
| TASK-213 | Add rate limiting: Respect Retry-After headers | | |
| TASK-214 | Add response caching: Cache responses with TTL | | |
| TASK-215 | Write comprehensive unit tests | | |
| TASK-216 | Write integration tests with httpbin.org | | |

**Acceptance Criteria:**
- ✅ All HTTP methods supported
- ✅ Request templating works
- ✅ Response parsing for all formats
- ✅ JSONPath extraction works
- ✅ Response validation works
- ✅ Pagination support
- ✅ All auth methods work
- ✅ Circuit breaker protects failing APIs
- ✅ Tests pass

---

### Implementation Phase 3.16: Audit Logging

**GOAL-016**: Implement comprehensive audit logging for compliance

| Task | Description | Completed | Date |
|------|-------------|-----------|------|
| TASK-217 | Create `backend/agentflow_core/db/models/audit_log.py` - AuditLog model | | |
| TASK-218 | Add fields: id, tenant_id, user_id, action, resource_type, resource_id, changes (JSONB), ip_address, user_agent, timestamp | | |
| TASK-219 | Create Alembic migration for audit_log table | | |
| TASK-220 | Add indexes: audit_logs(tenant_id), audit_logs(user_id), audit_logs(timestamp), audit_logs(resource_type, resource_id) | | |
| TASK-221 | Create `backend/agentflow_core/audit/__init__.py` | | |
| TASK-222 | Create `backend/agentflow_core/audit/logger.py` with factory function | | |
| TASK-223 | Implement `log_action(action, resource_type, resource_id, changes, user_id, ip, user_agent)` | | |
| TASK-224 | Define auditable actions: workflow.created, workflow.updated, workflow.deleted, workflow.executed, source.created, source.updated, source.deleted | | |
| TASK-225 | Add audit logging to all CRUD operations | | |
| TASK-226 | Add audit logging to workflow execution | | |
| TASK-227 | Implement `GET /admin/audit-logs` endpoint - Query audit logs with filters | | |
| TASK-228 | Add filtering: By user, action, resource, date range | | |
| TASK-229 | Add pagination and sorting | | |
| TASK-230 | Protect audit logs: Cannot be modified or deleted (append-only) | | |
| TASK-231 | Add retention policy: Archive logs older than 1 year | | |
| TASK-232 | Write tests: Verify all actions logged | | |
| TASK-233 | Document audit logging in compliance guide | | |

**Acceptance Criteria:**
- ✅ Audit log model created
- ✅ All actions logged
- ✅ Audit logs immutable
- ✅ Query endpoint works
- ✅ Filtering and pagination work
- ✅ Retention policy configured
- ✅ Tests pass
- ✅ Documentation complete

---

### Implementation Phase 3.17: Integration Testing & Performance Validation

**GOAL-017**: Comprehensive testing and performance validation

| Task | Description | Completed | Date |
|------|-------------|-----------|------|
| TASK-234 | Create test environment: PostgreSQL, Redis, Celery workers | | |
| TASK-235 | Write integration test: Execution history - Execute workflow, query history, verify per-node data | | |
| TASK-236 | Write integration test: Redis caching - Verify cache hits, invalidation | | |
| TASK-237 | Write integration test: Response caching - Verify GET responses cached | | |
| TASK-238 | Write integration test: Background jobs - Queue job, wait for completion, query result | | |
| TASK-239 | Write integration test: Horizontal scaling - Deploy 3 instances, distribute load, verify consistency | | |
| TASK-240 | Write integration test: Parallel execution - Verify independent nodes run in parallel | | |
| TASK-241 | Write integration test: Anthropic Claude - Call Claude model and verify response | | |
| TASK-242 | Write integration test: Google Gemini - Call Gemini model and verify response | | |
| TASK-243 | Write integration test: Azure OpenAI - Call Azure deployment and verify response | | |
| TASK-244 | Write integration test: MySQL - Query MySQL database and verify results | | |
| TASK-245 | Write integration test: HTTP API node - Call external API with various auth methods | | |
| TASK-246 | Write integration test: Audit logging - Verify all actions logged | | |
| TASK-247 | Write load test: 100 concurrent workflow executions (target: >50 req/s) | | |
| TASK-248 | Write load test: Cache performance - Verify >80% hit rate under load | | |
| TASK-249 | Measure metrics: Verify Prometheus metrics exported correctly | | |
| TASK-250 | Measure traces: Verify traces in Jaeger | | |
| TASK-251 | Profile performance: Run profiler and verify no major bottlenecks | | |
| TASK-252 | Validate latency: P95 latency <500ms for API endpoints | | |
| TASK-253 | Run all tests and verify >80% coverage | | |

**Acceptance Criteria:**
- ✅ All integration tests pass
- ✅ Load tests meet performance targets (>50 req/s)
- ✅ Cache hit rate >80%
- ✅ P95 latency <500ms
- ✅ Prometheus metrics exported correctly
- ✅ Traces visible in Jaeger
- ✅ No performance bottlenecks
- ✅ Test coverage >80%

---

## 3. Dependencies

### Internal Dependencies

- **DEP-001**: Phase 1 Backend MVP - Core functionality
- **DEP-002**: Phase 2 Production Readiness - Database persistence, rate limiting
- **DEP-003**: Workflow Executor - Extended for parallel execution
- **DEP-004**: Source Registry - Extended with new providers
- **DEP-005**: API Endpoints - Extended with execution history

### External Dependencies

- **DEP-006**: Redis 7+ - Caching and job queue
- **DEP-007**: Celery 5.3+ - Background job processing
- **DEP-008**: Flower 2.0+ - Celery monitoring
- **DEP-009**: Prometheus - Metrics storage and visualization
- **DEP-010**: Grafana - Dashboard for metrics
- **DEP-011**: Jaeger - Distributed tracing backend
- **DEP-012**: OpenTelemetry SDK - Tracing instrumentation
- **DEP-013**: Anthropic SDK - Claude API client
- **DEP-014**: Google AI SDK - Gemini API client
- **DEP-015**: aiomysql - MySQL async driver
- **DEP-016**: py-spy - Performance profiling
- **DEP-017**: memory-profiler - Memory profiling

### Environment Variables

```bash
# Redis
REDIS_URL="redis://localhost:6379"
REDIS_MAX_MEMORY="4gb"

# Celery
CELERY_BROKER_URL="redis://localhost:6379/1"
CELERY_RESULT_BACKEND="redis://localhost:6379/2"

# Prometheus
PROMETHEUS_MULTIPROC_DIR="/tmp/prometheus"

# Jaeger
JAEGER_ENDPOINT="http://localhost:14268/api/traces"
JAEGER_SAMPLING_RATE="0.1"

# LLM Providers
ANTHROPIC_API_KEY="sk-ant-..."
GOOGLE_API_KEY="AIza..."
AZURE_OPENAI_ENDPOINT="https://....openai.azure.com/"
AZURE_OPENAI_API_KEY="..."

# MySQL
MYSQL_CONNECTION_STRING="mysql://user:pass@localhost:3306/dbname"

# Performance
ENABLE_PARALLEL_EXECUTION="true"
MAX_PARALLEL_NODES="5"

# Caching
CACHE_SOURCES_TTL="300"
CACHE_WORKFLOWS_TTL="600"
CACHE_VALIDATION_TTL="300"
CACHE_RESPONSES_TTL="60"
```

---

## 4. Files

### New Files

1. **backend/agentflow_core/cache/** - Caching layer
   - `__init__.py`
   - `redis_cache.py` - Redis cache implementation

2. **backend/agentflow_core/workers/** - Background workers
   - `__init__.py`
   - `celery_app.py` - Celery application
   - `tasks.py` - Celery tasks (async execution)

3. **backend/agentflow_core/monitoring/** - Observability
   - `__init__.py`
   - `metrics.py` - Prometheus metrics
   - `tracing.py` - OpenTelemetry tracing

4. **backend/agentflow_core/audit/** - Audit logging
   - `__init__.py`
   - `logger.py` - Audit log implementation

5. **backend/agentflow_core/sources/** - New providers
   - `llm_anthropic.py` - Anthropic Claude
   - `llm_google.py` - Google Gemini
   - `llm_azure_openai.py` - Azure OpenAI
   - `db_mysql.py` - MySQL database

6. **backend/agentflow_core/nodes/api_node.py** - Enhanced HTTP API node

7. **backend/agentflow_core/api/middleware/cache_middleware.py** - Response caching

8. **backend/agentflow_core/db/models/audit_log.py** - Audit log model

9. **scripts/start_celery_worker.sh** - Worker startup script

10. **scripts/profile_api.py** - Performance profiling script

11. **dashboards/grafana_dashboard.json** - Grafana dashboard definition

### Modified Files

1. **backend/agentflow_core/api/main.py** - Add middleware, tracing, metrics
2. **backend/agentflow_core/runtime/executor.py** - Parallel execution, metrics
3. **backend/agentflow_core/runtime/builder.py** - Parallel edge marking
4. **backend/agentflow_core/runtime/registry.py** - Redis-backed registry
5. **backend/agentflow_core/db/repositories/execution_repository.py** - Per-node execution tracking
6. **backend/agentflow_core/api/routes/workflows.py** - Execution history endpoints
7. **backend/requirements.txt** - Add new dependencies
8. **backend/pyproject.toml** - Update version

---

## 5. Testing Strategy

### Unit Tests (Coverage Target: 80%+)

- **test_redis_cache.py** - Cache operations with fakeredis
- **test_celery_tasks.py** - Background task execution
- **test_metrics.py** - Prometheus metrics updates
- **test_tracing.py** - Trace creation and propagation
- **test_anthropic_source.py** - Anthropic API calls (mocked)
- **test_google_source.py** - Google API calls (mocked)
- **test_azure_openai_source.py** - Azure API calls (mocked)
- **test_mysql_source.py** - MySQL queries (test container)
- **test_api_node.py** - HTTP API node (mocked)
- **test_audit_logger.py** - Audit log creation

### Integration Tests

- **test_execution_history_integration.py** - Full execution with history tracking
- **test_caching_integration.py** - Cache hit/miss/invalidation
- **test_celery_integration.py** - Queue and execute background jobs
- **test_scaling_integration.py** - Multi-instance deployment
- **test_parallel_execution_integration.py** - Parallel node execution
- **test_llm_providers_integration.py** - All LLM providers with real APIs
- **test_mysql_integration.py** - MySQL queries with real database
- **test_audit_logging_integration.py** - Verify all actions logged

### Performance Tests

- **test_load_concurrent_executions.py** - 100+ concurrent executions
- **test_cache_performance.py** - Cache hit rate under load
- **test_api_latency.py** - P95 latency measurement
- **test_throughput.py** - Requests per second with 3 instances

### Test Commands

```bash
# Run all tests
pytest tests/ --cov=agentflow_core --cov-report=html --cov-report=term

# Run integration tests
pytest tests/integration/ -v

# Run performance tests
pytest tests/performance/ -v --timeout=300

# Run specific provider tests
pytest tests/integration/test_llm_providers_integration.py -v

# Load test
locust -f tests/performance/locustfile.py --host=http://localhost:8000
```

---

## 6. Success Criteria

Phase 3 is complete when all of the following are met:

### Execution History

✅ **Criterion 1**: Per-node execution data stored in database  
✅ **Criterion 2**: Execution history queryable by workflow with pagination  
✅ **Criterion 3**: Execution statistics computed correctly (success rate, avg duration, tokens, cost)  
✅ **Criterion 4**: Retention policy deletes executions older than 90 days

### Caching

✅ **Criterion 5**: Redis caching implemented for sources, graphs, validation results  
✅ **Criterion 6**: Cache hit rate >80% for sources  
✅ **Criterion 7**: Cache invalidation works on updates  
✅ **Criterion 8**: Response caching works for GET endpoints with >70% hit rate

### Background Jobs

✅ **Criterion 9**: Celery configured with Redis broker  
✅ **Criterion 10**: Async workflow execution works  
✅ **Criterion 11**: Job status queryable  
✅ **Criterion 12**: Workers scale independently from API

### Scalability

✅ **Criterion 13**: API is fully stateless (3 instances run without conflicts)  
✅ **Criterion 14**: Distributed rate limiting works across instances  
✅ **Criterion 15**: Cache coherent across instances  
✅ **Criterion 16**: Throughput >50 req/s with 3 instances

### Performance Optimization

✅ **Criterion 17**: Independent nodes execute in parallel  
✅ **Criterion 18**: 50% execution time reduction for workflows with parallel nodes  
✅ **Criterion 19**: P95 API latency <500ms  
✅ **Criterion 20**: Circuit breaker protects failing services

### Observability

✅ **Criterion 21**: Prometheus metrics exported correctly  
✅ **Criterion 22**: Grafana dashboard displays all key metrics  
✅ **Criterion 23**: Distributed tracing works (traces visible in Jaeger)  
✅ **Criterion 24**: Health dashboard displays real-time system status

### Additional Providers

✅ **Criterion 25**: Anthropic Claude integration works  
✅ **Criterion 26**: Google Gemini integration works  
✅ **Criterion 27**: Azure OpenAI integration works  
✅ **Criterion 28**: MySQL database source works

### Additional Features

✅ **Criterion 29**: HTTP API node supports all HTTP methods and auth  
✅ **Criterion 30**: Audit logging tracks all actions  
✅ **Criterion 31**: Performance profiling identifies bottlenecks

### Testing & Documentation

✅ **Criterion 32**: All integration tests pass  
✅ **Criterion 33**: Load tests meet performance targets  
✅ **Criterion 34**: Test coverage >80%  
✅ **Criterion 35**: Documentation complete for all new features

---

## 7. Risks & Mitigation

### Risk 1: Redis Memory Exhaustion

**Impact:** High - Caching stops working, potential data loss  
**Probability:** Medium  
**Mitigation:**
- Set maxmemory limit (4GB)
- Configure allkeys-lru eviction policy
- Monitor Redis memory usage with alerts
- Implement cache size limits per tenant
- Document cache tuning guidelines

### Risk 2: Celery Worker Failures

**Impact:** High - Background jobs stop processing  
**Probability:** Medium  
**Mitigation:**
- Deploy at least 2 worker instances
- Configure worker auto-restart
- Monitor worker health with Flower
- Implement job retry logic
- Alert on worker unavailability

### Risk 3: Parallel Execution Race Conditions

**Impact:** High - Inconsistent state, incorrect results  
**Probability:** Medium  
**Mitigation:**
- Careful graph analysis for parallel safety
- Use immutable state between nodes
- Test thoroughly with parallel workflows
- Add execution locks for shared resources
- Document parallel execution limitations

### Risk 4: Metrics Overhead

**Impact:** Medium - Metrics collection slows down API  
**Probability:** Low  
**Mitigation:**
- Use efficient Prometheus client
- Batch metric updates
- Use sampling for high-volume metrics
- Monitor metrics collection overhead
- Optimize hot paths

### Risk 5: Tracing Performance Impact

**Impact:** Medium - Tracing adds latency  
**Probability:** Low  
**Mitigation:**
- Use 10% sampling in production
- Optimize span creation overhead
- Use async trace export
- Monitor trace export backlog
- Tune sampling rate based on load

### Risk 6: Multi-Provider API Key Management

**Impact:** High - Credentials exposed or misconfigured  
**Probability:** Medium  
**Mitigation:**
- Use environment variables only
- Never log API keys
- Validate API keys on startup
- Rotate keys regularly
- Use secrets manager in production

### Risk 7: Cache Coherence Issues

**Impact:** Medium - Stale data served from cache  
**Probability:** Medium  
**Mitigation:**
- Implement cache invalidation on all updates
- Use short TTLs (5-10 minutes)
- Add cache version tags
- Test cache invalidation thoroughly
- Document cache behavior

---

## 8. Related Documents

- [Backend Features Master Document](./BACKEND-FEATURES.md)
- [Phase 1: Backend MVP Plan](./phase-1-backend-mvp-plan.md)
- [Phase 2: Production Readiness Plan](./phase-2-backend-production-plan.md)
- [Phase 4: Enterprise Features Plan](./phase-4-backend-enterprise-plan.md) - Next phase
- [Backend README](./README.md)
- [API Documentation](../../../shared/docs/API_Spec.md)

---

**Document Version:** 1.0  
**Last Updated:** December 7, 2025  
**Maintained By:** AgentFlow Backend Engineering Team  
**Estimated Duration:** 11 weeks  
**Total Tasks:** 253 tasks across 17 goals  
**Status:** Ready for Implementation 🚀
