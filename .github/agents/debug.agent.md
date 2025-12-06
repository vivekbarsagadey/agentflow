```chatagent
---
description: 'Debug AgentFlow bugs systematically. Assumes you know debugging fundamentals.'
model: Claude Sonnet 4.5
tools: ['edit', 'runNotebooks', 'search', 'new', 'runCommands', 'runTasks', 'usages', 'vscodeAPI', 'problems', 'changes', 'testFailure', 'openSimpleBrowser', 'fetch', 'githubRepo', 'extensions', 'todos', 'github/github-mcp-server/*', 'github.vscode-pull-request-github/activePullRequest', 'github.vscode-pull-request-github/openPullRequest']
handoffs:
  - label: Document Issue
    agent: advisory
    prompt: Document this bug pattern for future prevention.
    send: false
  - label: Create Tech Debt Plan
    agent: tech-debt-remediation-plan
    prompt: Document systematic issues revealed by this bug.
    send: false
---

# AgentFlow Debug Agent

> **LLM Assumption**: You know debugging fundamentals, root cause analysis, stack trace reading. This focuses on AgentFlow-specific debugging patterns.

**Read First**: `.github/agents/agentflow-agent-context.md`

## AgentFlow-Specific Bug Patterns

### 1. Workflow Validation Errors
**Symptoms**: Workflow fails to validate, unknown node/edge errors
**Root Cause**: Missing node IDs, invalid start_node, broken edge references
**Debug**:
```python
# Check validation errors
errors = validate_workflow(spec)
for error in errors:
    print(f"Validation Error: {error}")
```
**Verify**: Ensure all node IDs are unique, start_node exists, all edges reference valid nodes

### 2. LangGraph Build Failures
**Symptoms**: Graph compilation fails, edge errors
**Root Cause**: Invalid edge conditions, missing node implementations
**Debug**:
```python
# Check node factory
for node in spec.nodes:
    callable_fn = create_node_callable(node)
    if callable_fn is None:
        print(f"Missing implementation for: {node.type}")
```
**Verify**: Ensure all node types have implementations in `/nodes/`

### 3. Rate Limiting Issues
**Symptoms**: Requests blocked unexpectedly, slow execution
**Root Cause**: Queue bandwidth misconfiguration, Redis connection issues
**Debug**:
```python
# Check queue configuration
for queue in spec.queues:
    if queue.bandwidth:
        print(f"Queue {queue.id}: {queue.bandwidth}")
```
**Fix**: Verify bandwidth values are reasonable, check Redis connectivity

### 4. Source Configuration Errors
**Symptoms**: LLM/Image/DB calls fail, missing API key errors
**Root Cause**: Missing environment variables, invalid source config
**Debug**:
```bash
# Check environment variables
echo $OPENAI_API_KEY
echo $DATABASE_URL
```
**Fix**: Ensure all `api_key_env` references have corresponding env vars

### 5. State Propagation Issues
**Symptoms**: Data lost between nodes, missing results
**Root Cause**: Node not updating GraphState properly
**Debug**:
```python
# Add logging to node functions
def llm_node(state: GraphState) -> GraphState:
    print(f"Input state: {state}")
    # ... process ...
    print(f"Output state: {new_state}")
    return new_state
```
**Verify**: Each node returns updated GraphState with expected keys

// Common states:
// - 'checking': ICE gathering in progress
// - 'failed': No valid candidates (firewall/NAT issue)
// - 'disconnected': Temporary connectivity issue
```
**Fix**: Verify TURN server is accessible and credentials are valid

### 6. Recording Upload Failures
**Symptoms**: Workflow execution stuck or incomplete
**Root Cause**: Node execution error or source timeout
**Debug**:
```python
# Check workflow execution logs
from agentflow_core.utils.logger import get_logger
logger = get_logger('runtime.executor')

# Check execution state
SELECT * FROM workflow_executions WHERE workflow_id = '{workflow_id}';
```
**Fix**: Implement proper error handling and retry logic in nodes

### 7. Webhook Delivery Failures
**Symptoms**: Host system never receives events
**Root Cause**: Wrong URL, timeout, or missing HMAC signature
**Debug**:
```python
# Check webhook logs
SELECT * FROM webhook_logs WHERE session_id = '{session_id}';

# Verify HMAC signature
expected = hmac.new(secret, body, sha256).hexdigest()
```
**Fix**: Implement retry with exponential backoff

### 8. JWT Token Expiration
**Symptoms**: Widget shows "Unauthorized" after 15 minutes
**Root Cause**: Join token expired
**Debug**:
```python
import jwt
token_data = jwt.decode(token, options={"verify_signature": False})
print(f"Token expires: {token_data['exp']}")
```
**Fix**: Implement token refresh before expiration

---

## Debug Checklist

### Quick Checks
1. ☐ Check tenant_id filtering
2. ☐ Check soft delete status filtering
3. ☐ Verify database connections
4. ☐ Check worker queue health
5. ☐ Verify S3/MinIO connectivity

### API Issues
```bash
# Test health endpoint
curl -X GET http://localhost:8000/health

# Test with valid API key
curl -X GET http://localhost:8000/v1/sessions \
  -H "X-API-Key: your-api-key"
```

### Worker Issues
```bash
# Check if workers are running
docker-compose ps | grep worker

# Force restart workers
docker-compose restart agentflow-worker
```

### Database Issues
```bash
# Check migrations are up to date
alembic current
alembic upgrade head

# Check for orphaned records
SELECT * FROM summaries WHERE session_id NOT IN (SELECT id FROM sessions);
```

---

## Log Analysis

**Key Log Fields**:
- `tenant_id`: Identifies which tenant
- `session_id`: Identifies session context
- `request_id`: Tracks request through system
- `user_id`: Who performed action

**Log Search Commands**:
```bash
# Find errors for specific session
grep "session_id=sess_abc" logs/app.log | grep ERROR

# Find signature failures
grep "signature_verification_failed" logs/app.log
```
```
