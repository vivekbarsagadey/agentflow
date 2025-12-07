# Database Schema

# AgentFlow Database Schema v1.0

**Version:** 1.0.0  
**Date:** December 7, 2025  
**Database:** PostgreSQL 14+  
**Status:** Approved

---

## Table of Contents

1. [Overview](#1-overview)
2. [Entity-relationship diagram](#2-entity-relationship-diagram)
3. [Table definitions](#3-table-definitions)
4. [Indexes and constraints](#4-indexes-and-constraints)
5. [Data types](#5-data-types)
6. [Migrations](#6-migrations)
7. [Sample data](#7-sample-data)

---

## 1. Overview

### 1.1 Database purpose

The AgentFlow database stores:

- **Workflows** - Saved workflow specifications
- **Executions** - Workflow execution history and results
- **Sources** - Source configurations (LLM, DB, API, Image)
- **Users** - User accounts and authentication
- **API Keys** - API authentication keys
- **Audit Logs** - System activity logs

### 1.2 Design principles

| Principle | Description |
|-----------|-------------|
| **Normalization** | 3NF (Third Normal Form) |
| **Soft Deletes** | All tables support soft deletion |
| **Timestamps** | created_at, updated_at, deleted_at |
| **UUIDs** | Primary keys use UUID v4 |
| **Audit Trail** | created_by, updated_by, deleted_by |
| **Multi-Tenancy** | All tables include tenant_id |

### 1.3 Naming conventions

| Convention | Example |
|------------|---------|
| **Tables** | Plural, snake_case (e.g., `workflows`, `executions`) |
| **Columns** | snake_case (e.g., `workflow_spec`, `created_at`) |
| **Primary Keys** | `id` (UUID) |
| **Foreign Keys** | `{table}_id` (e.g., `workflow_id`, `user_id`) |
| **Indexes** | `idx_{table}_{column(s)}` |
| **Constraints** | `fk_{table}_{column}`, `chk_{table}_{column}` |

---

## 2. Entity-relationship diagram

```
┌─────────────┐          ┌─────────────┐          ┌─────────────┐
│   users     │          │  workflows  │          │   sources   │
├─────────────┤          ├─────────────┤          ├─────────────┤
│ id (PK)     │          │ id (PK)     │          │ id (PK)     │
│ email       │──┐       │ name        │          │ kind        │
│ name        │  │   ┌──│ user_id (FK)│          │ config      │
│ password    │  │   │   │ spec (JSON) │          │ tenant_id   │
│ tenant_id   │  │   │   │ tenant_id   │          │ created_at  │
│ created_at  │  │   │   │ created_at  │          │ updated_at  │
└─────────────┘  │   │   └─────────────┘          └─────────────┘
                 │   │          │
                 │   │          │
                 │   │          │
                 └───┼──────────┘
                     │
                     │
                     ▼
              ┌──────────────┐
              │  executions  │
              ├──────────────┤
              │ id (PK)      │
              │ workflow_id  │
              │ user_id (FK) │
              │ status       │
              │ initial_state│
              │ final_state  │
              │ metrics      │
              │ started_at   │
              │ completed_at │
              └──────────────┘
                     │
                     │
                     ▼
              ┌──────────────┐
              │ api_keys     │
              ├──────────────┤
              │ id (PK)      │
              │ user_id (FK) │
              │ key_hash     │
              │ name         │
              │ permissions  │
              │ expires_at   │
              │ created_at   │
              └──────────────┘
```

---

## 3. Table definitions

### 3.1 users table

Stores user account information.

```sql
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) NOT NULL UNIQUE,
    name VARCHAR(255) NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    tenant_id UUID NOT NULL,
    status VARCHAR(50) NOT NULL DEFAULT 'active',
    
    -- Audit fields
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    deleted_at TIMESTAMPTZ NULL,
    created_by UUID NULL,
    updated_by UUID NULL,
    deleted_by UUID NULL,
    
    CONSTRAINT chk_users_status CHECK (status IN ('active', 'inactive', 'deleted'))
);

CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_tenant_id ON users(tenant_id);
CREATE INDEX idx_users_status ON users(status);
```

**Columns:**

| Column | Type | Nullable | Description |
|--------|------|----------|-------------|
| `id` | UUID | No | Primary key |
| `email` | VARCHAR(255) | No | User email (unique) |
| `name` | VARCHAR(255) | No | Full name |
| `password_hash` | VARCHAR(255) | No | Hashed password |
| `tenant_id` | UUID | No | Tenant identifier |
| `status` | VARCHAR(50) | No | Account status |
| `created_at` | TIMESTAMPTZ | No | Creation timestamp |
| `updated_at` | TIMESTAMPTZ | No | Last update timestamp |
| `deleted_at` | TIMESTAMPTZ | Yes | Soft delete timestamp |
| `created_by` | UUID | Yes | User who created |
| `updated_by` | UUID | Yes | User who last updated |
| `deleted_by` | UUID | Yes | User who deleted |

---

### 3.2 workflows table

Stores saved workflow specifications.

```sql
CREATE TABLE workflows (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL,
    description TEXT NULL,
    spec JSONB NOT NULL,
    user_id UUID NOT NULL,
    tenant_id UUID NOT NULL,
    status VARCHAR(50) NOT NULL DEFAULT 'draft',
    version INTEGER NOT NULL DEFAULT 1,
    
    -- Audit fields
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    deleted_at TIMESTAMPTZ NULL,
    created_by UUID NULL,
    updated_by UUID NULL,
    deleted_by UUID NULL,
    
    CONSTRAINT fk_workflows_user_id FOREIGN KEY (user_id) 
        REFERENCES users(id) ON DELETE CASCADE,
    CONSTRAINT chk_workflows_status CHECK (status IN ('draft', 'published', 'archived', 'deleted'))
);

CREATE INDEX idx_workflows_user_id ON workflows(user_id);
CREATE INDEX idx_workflows_tenant_id ON workflows(tenant_id);
CREATE INDEX idx_workflows_status ON workflows(status);
CREATE INDEX idx_workflows_created_at ON workflows(created_at DESC);
CREATE INDEX idx_workflows_spec_gin ON workflows USING GIN (spec);
```

**Columns:**

| Column | Type | Nullable | Description |
|--------|------|----------|-------------|
| `id` | UUID | No | Primary key |
| `name` | VARCHAR(255) | No | Workflow name |
| `description` | TEXT | Yes | Description |
| `spec` | JSONB | No | Workflow specification (JSON) |
| `user_id` | UUID | No | Owner user ID |
| `tenant_id` | UUID | No | Tenant identifier |
| `status` | VARCHAR(50) | No | Workflow status |
| `version` | INTEGER | No | Version number |
| `created_at` | TIMESTAMPTZ | No | Creation timestamp |
| `updated_at` | TIMESTAMPTZ | No | Last update timestamp |
| `deleted_at` | TIMESTAMPTZ | Yes | Soft delete timestamp |

---

### 3.3 executions table

Stores workflow execution history and results.

```sql
CREATE TABLE executions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    workflow_id UUID NOT NULL,
    user_id UUID NOT NULL,
    tenant_id UUID NOT NULL,
    status VARCHAR(50) NOT NULL DEFAULT 'pending',
    
    -- Execution data
    initial_state JSONB NOT NULL,
    final_state JSONB NULL,
    error_message TEXT NULL,
    
    -- Metrics
    metrics JSONB NULL,
    tokens_used INTEGER NULL DEFAULT 0,
    cost DECIMAL(10, 4) NULL DEFAULT 0,
    execution_time DECIMAL(10, 3) NULL,
    
    -- Timestamps
    started_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    completed_at TIMESTAMPTZ NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    
    CONSTRAINT fk_executions_workflow_id FOREIGN KEY (workflow_id) 
        REFERENCES workflows(id) ON DELETE CASCADE,
    CONSTRAINT fk_executions_user_id FOREIGN KEY (user_id) 
        REFERENCES users(id) ON DELETE CASCADE,
    CONSTRAINT chk_executions_status CHECK (status IN ('pending', 'running', 'completed', 'failed', 'cancelled'))
);

CREATE INDEX idx_executions_workflow_id ON executions(workflow_id);
CREATE INDEX idx_executions_user_id ON executions(user_id);
CREATE INDEX idx_executions_tenant_id ON executions(tenant_id);
CREATE INDEX idx_executions_status ON executions(status);
CREATE INDEX idx_executions_started_at ON executions(started_at DESC);
CREATE INDEX idx_executions_completed_at ON executions(completed_at DESC NULLS LAST);
```

**Columns:**

| Column | Type | Nullable | Description |
|--------|------|----------|-------------|
| `id` | UUID | No | Primary key |
| `workflow_id` | UUID | No | Workflow reference |
| `user_id` | UUID | No | User who executed |
| `tenant_id` | UUID | No | Tenant identifier |
| `status` | VARCHAR(50) | No | Execution status |
| `initial_state` | JSONB | No | Input state |
| `final_state` | JSONB | Yes | Output state |
| `error_message` | TEXT | Yes | Error message (if failed) |
| `metrics` | JSONB | Yes | Execution metrics |
| `tokens_used` | INTEGER | Yes | Total tokens consumed |
| `cost` | DECIMAL(10, 4) | Yes | Execution cost (USD) |
| `execution_time` | DECIMAL(10, 3) | Yes | Duration (seconds) |
| `started_at` | TIMESTAMPTZ | No | Start timestamp |
| `completed_at` | TIMESTAMPTZ | Yes | Completion timestamp |

---

### 3.4 sources table

Stores source configurations (LLM, DB, API, Image).

```sql
CREATE TABLE sources (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL,
    kind VARCHAR(50) NOT NULL,
    config JSONB NOT NULL,
    user_id UUID NOT NULL,
    tenant_id UUID NOT NULL,
    status VARCHAR(50) NOT NULL DEFAULT 'active',
    
    -- Audit fields
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    deleted_at TIMESTAMPTZ NULL,
    created_by UUID NULL,
    updated_by UUID NULL,
    deleted_by UUID NULL,
    
    CONSTRAINT fk_sources_user_id FOREIGN KEY (user_id) 
        REFERENCES users(id) ON DELETE CASCADE,
    CONSTRAINT chk_sources_kind CHECK (kind IN ('llm', 'image', 'db', 'api')),
    CONSTRAINT chk_sources_status CHECK (status IN ('active', 'inactive', 'deleted'))
);

CREATE INDEX idx_sources_user_id ON sources(user_id);
CREATE INDEX idx_sources_tenant_id ON sources(tenant_id);
CREATE INDEX idx_sources_kind ON sources(kind);
CREATE INDEX idx_sources_status ON sources(status);
CREATE INDEX idx_sources_config_gin ON sources USING GIN (config);
```

**Columns:**

| Column | Type | Nullable | Description |
|--------|------|----------|-------------|
| `id` | UUID | No | Primary key |
| `name` | VARCHAR(255) | No | Source name |
| `kind` | VARCHAR(50) | No | Source type (llm/image/db/api) |
| `config` | JSONB | No | Source configuration (JSON) |
| `user_id` | UUID | No | Owner user ID |
| `tenant_id` | UUID | No | Tenant identifier |
| `status` | VARCHAR(50) | No | Source status |
| `created_at` | TIMESTAMPTZ | No | Creation timestamp |
| `updated_at` | TIMESTAMPTZ | No | Last update timestamp |
| `deleted_at` | TIMESTAMPTZ | Yes | Soft delete timestamp |

---

### 3.5 api_keys table

Stores API authentication keys.

```sql
CREATE TABLE api_keys (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL,
    tenant_id UUID NOT NULL,
    name VARCHAR(255) NOT NULL,
    key_hash VARCHAR(255) NOT NULL UNIQUE,
    permissions JSONB NULL,
    status VARCHAR(50) NOT NULL DEFAULT 'active',
    last_used_at TIMESTAMPTZ NULL,
    expires_at TIMESTAMPTZ NULL,
    
    -- Audit fields
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    deleted_at TIMESTAMPTZ NULL,
    created_by UUID NULL,
    deleted_by UUID NULL,
    
    CONSTRAINT fk_api_keys_user_id FOREIGN KEY (user_id) 
        REFERENCES users(id) ON DELETE CASCADE,
    CONSTRAINT chk_api_keys_status CHECK (status IN ('active', 'revoked', 'expired'))
);

CREATE INDEX idx_api_keys_user_id ON api_keys(user_id);
CREATE INDEX idx_api_keys_tenant_id ON api_keys(tenant_id);
CREATE INDEX idx_api_keys_key_hash ON api_keys(key_hash);
CREATE INDEX idx_api_keys_status ON api_keys(status);
CREATE INDEX idx_api_keys_expires_at ON api_keys(expires_at);
```

**Columns:**

| Column | Type | Nullable | Description |
|--------|------|----------|-------------|
| `id` | UUID | No | Primary key |
| `user_id` | UUID | No | Owner user ID |
| `tenant_id` | UUID | No | Tenant identifier |
| `name` | VARCHAR(255) | No | Key name/description |
| `key_hash` | VARCHAR(255) | No | Hashed API key (unique) |
| `permissions` | JSONB | Yes | Permissions (JSON) |
| `status` | VARCHAR(50) | No | Key status |
| `last_used_at` | TIMESTAMPTZ | Yes | Last usage timestamp |
| `expires_at` | TIMESTAMPTZ | Yes | Expiration timestamp |
| `created_at` | TIMESTAMPTZ | No | Creation timestamp |
| `updated_at` | TIMESTAMPTZ | No | Last update timestamp |

---

### 3.6 audit_logs table

Stores system activity logs.

```sql
CREATE TABLE audit_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NULL,
    tenant_id UUID NOT NULL,
    action VARCHAR(100) NOT NULL,
    entity_type VARCHAR(100) NOT NULL,
    entity_id UUID NULL,
    old_value JSONB NULL,
    new_value JSONB NULL,
    ip_address INET NULL,
    user_agent TEXT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    
    CONSTRAINT fk_audit_logs_user_id FOREIGN KEY (user_id) 
        REFERENCES users(id) ON DELETE SET NULL
);

CREATE INDEX idx_audit_logs_user_id ON audit_logs(user_id);
CREATE INDEX idx_audit_logs_tenant_id ON audit_logs(tenant_id);
CREATE INDEX idx_audit_logs_action ON audit_logs(action);
CREATE INDEX idx_audit_logs_entity_type ON audit_logs(entity_type);
CREATE INDEX idx_audit_logs_entity_id ON audit_logs(entity_id);
CREATE INDEX idx_audit_logs_created_at ON audit_logs(created_at DESC);
```

**Columns:**

| Column | Type | Nullable | Description |
|--------|------|----------|-------------|
| `id` | UUID | No | Primary key |
| `user_id` | UUID | Yes | User who performed action |
| `tenant_id` | UUID | No | Tenant identifier |
| `action` | VARCHAR(100) | No | Action performed (e.g., 'create', 'update', 'delete') |
| `entity_type` | VARCHAR(100) | No | Entity type (e.g., 'workflow', 'source') |
| `entity_id` | UUID | Yes | Entity identifier |
| `old_value` | JSONB | Yes | Previous value (for updates) |
| `new_value` | JSONB | Yes | New value (for creates/updates) |
| `ip_address` | INET | Yes | Client IP address |
| `user_agent` | TEXT | Yes | Client user agent |
| `created_at` | TIMESTAMPTZ | No | Action timestamp |

---

## 4. Indexes and constraints

### 4.1 Primary key indexes

All tables have a primary key index on the `id` column (UUID).

### 4.2 Foreign key constraints

| Table | Column | References |
|-------|--------|-----------|
| `workflows` | `user_id` | `users(id)` |
| `executions` | `workflow_id` | `workflows(id)` |
| `executions` | `user_id` | `users(id)` |
| `sources` | `user_id` | `users(id)` |
| `api_keys` | `user_id` | `users(id)` |
| `audit_logs` | `user_id` | `users(id)` |

### 4.3 Unique constraints

| Table | Column(s) | Description |
|-------|----------|-------------|
| `users` | `email` | Email must be unique |
| `api_keys` | `key_hash` | API key hash must be unique |

### 4.4 Check constraints

| Table | Column | Constraint |
|-------|--------|-----------|
| `users` | `status` | Must be 'active', 'inactive', or 'deleted' |
| `workflows` | `status` | Must be 'draft', 'published', 'archived', or 'deleted' |
| `executions` | `status` | Must be 'pending', 'running', 'completed', 'failed', or 'cancelled' |
| `sources` | `kind` | Must be 'llm', 'image', 'db', or 'api' |
| `sources` | `status` | Must be 'active', 'inactive', or 'deleted' |
| `api_keys` | `status` | Must be 'active', 'revoked', or 'expired' |

### 4.5 GIN indexes (JSON columns)

| Table | Column | Purpose |
|-------|--------|---------|
| `workflows` | `spec` | Fast JSON queries on workflow specs |
| `sources` | `config` | Fast JSON queries on source configs |

---

## 5. Data types

### 5.1 Standard types

| Type | Usage |
|------|-------|
| `UUID` | Primary keys, foreign keys |
| `VARCHAR(n)` | Short text fields (email, name, status) |
| `TEXT` | Long text fields (description, error messages) |
| `JSONB` | Structured data (workflow specs, metrics, configs) |
| `INTEGER` | Numeric values (version, tokens_used) |
| `DECIMAL(10, 4)` | Currency values (cost) |
| `DECIMAL(10, 3)` | Durations (execution_time) |
| `TIMESTAMPTZ` | Timestamps (created_at, updated_at) |
| `INET` | IP addresses (ip_address) |

### 5.2 JSONB structure examples

**workflows.spec:**
```json
{
  "nodes": [
    {"id": "input", "type": "input", "metadata": null},
    {"id": "llm", "type": "llm", "metadata": {"source": "openai"}}
  ],
  "edges": [
    {"from": "input", "to": "llm"}
  ],
  "queues": [],
  "sources": [
    {"id": "openai", "kind": "llm", "config": {"model_name": "gpt-4"}}
  ],
  "start_node": "input"
}
```

**sources.config:**
```json
{
  "model_name": "gpt-4",
  "api_key_env": "OPENAI_API_KEY",
  "temperature": 0.7,
  "max_tokens": 2000
}
```

**executions.metrics:**
```json
{
  "execution_time": 2.5,
  "tokens_used": 150,
  "cost": 0.0075,
  "node_execution_times": {
    "input": 0.001,
    "llm": 2.498
  }
}
```

**api_keys.permissions:**
```json
{
  "workflows": ["read", "write", "execute"],
  "sources": ["read", "write"],
  "executions": ["read"]
}
```

---

## 6. Migrations

### 6.1 Migration strategy

AgentFlow uses **Alembic** for database migrations.

```bash
# Create a new migration
alembic revision --autogenerate -m "add_workflows_table"

# Apply migrations
alembic upgrade head

# Rollback last migration
alembic downgrade -1

# Show current version
alembic current

# Show migration history
alembic history
```

### 6.2 Initial migration

**File:** `migrations/versions/001_initial_schema.py`

```python
"""Initial schema

Revision ID: 001
Revises: 
Create Date: 2025-12-07 10:00:00.000000
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID, JSONB, INET

revision = '001'
down_revision = None
branch_labels = None
depends_on = None

def upgrade():
    # Create users table
    op.create_table(
        'users',
        sa.Column('id', UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('email', sa.String(255), nullable=False, unique=True),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('password_hash', sa.String(255), nullable=False),
        sa.Column('tenant_id', UUID(as_uuid=True), nullable=False),
        sa.Column('status', sa.String(50), nullable=False, server_default='active'),
        sa.Column('created_at', sa.TIMESTAMP(timezone=True), nullable=False, server_default=sa.text('NOW()')),
        sa.Column('updated_at', sa.TIMESTAMP(timezone=True), nullable=False, server_default=sa.text('NOW()')),
        sa.Column('deleted_at', sa.TIMESTAMP(timezone=True), nullable=True),
        sa.Column('created_by', UUID(as_uuid=True), nullable=True),
        sa.Column('updated_by', UUID(as_uuid=True), nullable=True),
        sa.Column('deleted_by', UUID(as_uuid=True), nullable=True),
        sa.CheckConstraint("status IN ('active', 'inactive', 'deleted')", name='chk_users_status')
    )
    
    # Create workflows table
    op.create_table(
        'workflows',
        sa.Column('id', UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('description', sa.Text, nullable=True),
        sa.Column('spec', JSONB, nullable=False),
        sa.Column('user_id', UUID(as_uuid=True), nullable=False),
        sa.Column('tenant_id', UUID(as_uuid=True), nullable=False),
        sa.Column('status', sa.String(50), nullable=False, server_default='draft'),
        sa.Column('version', sa.Integer, nullable=False, server_default='1'),
        sa.Column('created_at', sa.TIMESTAMP(timezone=True), nullable=False, server_default=sa.text('NOW()')),
        sa.Column('updated_at', sa.TIMESTAMP(timezone=True), nullable=False, server_default=sa.text('NOW()')),
        sa.Column('deleted_at', sa.TIMESTAMP(timezone=True), nullable=True),
        sa.Column('created_by', UUID(as_uuid=True), nullable=True),
        sa.Column('updated_by', UUID(as_uuid=True), nullable=True),
        sa.Column('deleted_by', UUID(as_uuid=True), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], name='fk_workflows_user_id', ondelete='CASCADE'),
        sa.CheckConstraint("status IN ('draft', 'published', 'archived', 'deleted')", name='chk_workflows_status')
    )
    
    # Additional tables (executions, sources, api_keys, audit_logs)...

def downgrade():
    op.drop_table('workflows')
    op.drop_table('users')
    # Drop additional tables...
```

---

## 7. Sample data

### 7.1 Sample users

```sql
INSERT INTO users (id, email, name, password_hash, tenant_id, status)
VALUES 
    ('550e8400-e29b-41d4-a716-446655440000', 'john@example.com', 'John Doe', '$2b$12$...', '123e4567-e89b-12d3-a456-426614174000', 'active'),
    ('550e8400-e29b-41d4-a716-446655440001', 'jane@example.com', 'Jane Smith', '$2b$12$...', '123e4567-e89b-12d3-a456-426614174000', 'active');
```

### 7.2 Sample workflows

```sql
INSERT INTO workflows (id, name, description, spec, user_id, tenant_id, status)
VALUES (
    '660e8400-e29b-41d4-a716-446655440000',
    'Customer Support Bot',
    'Handles customer inquiries with AI',
    '{
        "nodes": [
            {"id": "input", "type": "input"},
            {"id": "router", "type": "router"},
            {"id": "llm", "type": "llm", "metadata": {"source": "openai"}}
        ],
        "edges": [
            {"from": "input", "to": "router"},
            {"from": "router", "to": "llm"}
        ],
        "queues": [],
        "sources": [
            {"id": "openai", "kind": "llm", "config": {"model_name": "gpt-4"}}
        ],
        "start_node": "input"
    }'::jsonb,
    '550e8400-e29b-41d4-a716-446655440000',
    '123e4567-e89b-12d3-a456-426614174000',
    'published'
);
```

### 7.3 Sample sources

```sql
INSERT INTO sources (id, name, kind, config, user_id, tenant_id, status)
VALUES 
    (
        '770e8400-e29b-41d4-a716-446655440000',
        'OpenAI GPT-4',
        'llm',
        '{"model_name": "gpt-4", "api_key_env": "OPENAI_API_KEY", "temperature": 0.7}'::jsonb,
        '550e8400-e29b-41d4-a716-446655440000',
        '123e4567-e89b-12d3-a456-426614174000',
        'active'
    ),
    (
        '770e8400-e29b-41d4-a716-446655440001',
        'DALL-E 3',
        'image',
        '{"model_name": "dall-e-3", "api_key_env": "OPENAI_API_KEY", "size": "1024x1024"}'::jsonb,
        '550e8400-e29b-41d4-a716-446655440000',
        '123e4567-e89b-12d3-a456-426614174000',
        'active'
    );
```

### 7.4 Sample executions

```sql
INSERT INTO executions (id, workflow_id, user_id, tenant_id, status, initial_state, final_state, metrics, tokens_used, cost, execution_time, started_at, completed_at)
VALUES (
    '880e8400-e29b-41d4-a716-446655440000',
    '660e8400-e29b-41d4-a716-446655440000',
    '550e8400-e29b-41d4-a716-446655440000',
    '123e4567-e89b-12d3-a456-426614174000',
    'completed',
    '{"user_input": "What is your return policy?"}'::jsonb,
    '{"user_input": "What is your return policy?", "text_result": "Our return policy allows..."}'::jsonb,
    '{"execution_time": 2.5, "tokens_used": 150}'::jsonb,
    150,
    0.0075,
    2.5,
    NOW() - INTERVAL '1 hour',
    NOW() - INTERVAL '1 hour' + INTERVAL '2.5 seconds'
);
```

### 7.5 Sample API keys

```sql
INSERT INTO api_keys (id, user_id, tenant_id, name, key_hash, permissions, status, expires_at)
VALUES (
    '990e8400-e29b-41d4-a716-446655440000',
    '550e8400-e29b-41d4-a716-446655440000',
    '123e4567-e89b-12d3-a456-426614174000',
    'Production API Key',
    '$2b$12$...',  -- Hashed version of sk_live_abc123...
    '{"workflows": ["read", "write", "execute"], "sources": ["read", "write"]}'::jsonb,
    'active',
    NOW() + INTERVAL '1 year'
);
```

---

**Document Approval**

| Role | Name | Date | Signature |
|------|------|------|-----------|
| Database Architect | _______________ | _______________ | _______________ |
| Backend Engineer | _______________ | _______________ | _______________ |
| DBA | _______________ | _______________ | _______________ |
