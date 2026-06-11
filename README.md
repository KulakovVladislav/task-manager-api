# Task Manager API

[![CI Status](https://img.shields.io/github/actions/workflow/status/KulakovVladislav/task-manager-api/ci.yml?branch=main)](https://github.com/KulakovVladislav/task-manager-api/actions)

A production-style Task Manager REST API built with FastAPI, PostgreSQL, Redis, Nginx, Docker, Alembic, JWT
authentication, and a fully isolated automated testing environment.
The project demonstrates backend engineering practices including authentication, multi-user data isolation, caching,
soft deletion, database migrations, reverse proxying, request tracing, and containerized infrastructure.

---

## Overview

Task Manager API allows users to register, authenticate, and manage personal tasks via secure REST endpoints.

Key design principles:

- Strict user-level data isolation
- Stateless authentication via JWT
- Reverse-proxy-only public access (Nginx)
- Redis-backed caching layer
- Observability via request correlation IDs and latency headers

The system runs fully inside Docker Compose. Only Nginx is exposed publicly (port 8080). The FastAPI service is private
within the internal Docker network.

---

## Core Features

### Authentication & Authorization

- User registration with unique username/email constraints
- Login with email + password
- JWT access tokens (Bearer authentication)
- Password hashing via bcrypt (Passlib)
- Strong password policy enforcement:
    - minimum length (8 characters)
    - uppercase letter
    - digit
    - special character
- Dummy password verification to mitigate user enumeration timing attacks

#### JWT Blacklist (Logout Security Model)

The system implements server-side token invalidation:

- Each JWT contains a `jti` (JWT ID)
- On logout, the `jti` is stored in the Redis blacklist
- Redis key TTL = remaining token lifetime
- Blacklisted tokens are rejected on every authenticated request

This ensures logout is immediate and enforceable server-side, not just client-side token deletion.

---

### Task Management

- Create / read / update / delete tasks
- Soft delete (logical removal only)
- Bulk delete all user tasks
- Task filtering (completed, priority)
- Sorting (id, priority)
- Pagination (limit, offset)
- Strict per-user task isolation

---

### Soft Delete

Tasks are not physically removed from the database:

```text
is_deleted = true
deleted_at = UTC timestamp
```

Soft-deleted tasks are excluded from:

- listing
- retrieval
- updates
- re-deletion

---

### Redis Caching

`GET /tasks` responses are cached in Redis.

Cache key format:

```text
tasks:user:{user_id}:comp:{completed}:prio:{priority}:lim:{limit}:off:{offset}:sb:{sort_by}:ord:{order}
```

Cache invalidation triggers:

- task creation
- task update
- task completion
- single delete
- bulk delete
- logout (optional full-user cache purge scenario ready)

TTL:

```text
TASKS_CACHE_TTL=60
```

---

## Tech Stack

### Backend

- Python (v3.14-slim)
- FastAPI (v0.136.3)
- SQLAlchemy (v2.0.50)
- Pydantic (v2.13.4)
- pydantic-settings (v2.14.1)
- PostgreSQL (v15-alpine)
- psycopg2-binary (v2.9.12)
- Alembic (v1.18.4)

### Security

- JWT (`python-jose` v3.5.0)
- bcrypt (v4.0.1) / Passlib (v1.7.4)
- OAuth2 Bearer flow
- Redis-based JWT blacklist

### Caching

- Redis (v7-alpine)
- `redis-py` (v8.0.0)
- `fakeredis` (v2.36.0) for isolation testing

### Infrastructure

- Docker / Docker Compose
- Nginx reverse proxy
- Gunicorn (v26.0.0) + Uvicorn workers (v0.49.0)

### Testing

- Pytest (v9.0.3)
- FastAPI TestClient
- Dedicated PostgreSQL test container
- `tmpfs` isolated database for speed
- Dependency overrides (DB + Redis)

---

## Architecture

```text
       Client
         │
         ▼ [Port 8080]
┌──────────────────────────────────────────────┐
│             Nginx (Reverse Proxy)            │
│  - Rate Limiting     - Request Buffering     │
│  - Request Tracing   - Static File Serving   │
└──────────────────────────────────────────────┘
         │
         ▼ [Port 8000 - Internal Network Only]
┌──────────────────────────────────────────────┐
│         FastAPI Application Service          │
│       (Gunicorn + Uvicorn Workers)           │
└──────────────────────┬───────────────────────┘
                       │
         ┌─────────────┴─────────────┐
         ▼                           ▼
┌──────────────────┐       ┌──────────────────┐
│    PostgreSQL    │       │      Redis       │
│  (Persisted DB)  │       │ (Cache & Token   │
└──────────────────┘       │    Blacklist)    │
                           └──────────────────┘
```

---

## Project Structure

```text
My_first_project/
├── alembic/                          # Database schema migration workspace (SQLAlchemy)
│   ├── env.py                        # Migration environment config; orchestrates target metadata and DB connections
│   ├── script.py.mako                # Mako template file for generating deterministic migration scripts
│   └── versions/                     # Linear history of schema states (initial tables, constraints, soft-delete fields)
├── app/                              # Core application container
│   ├── api/                          # Route delivery layer (HTTP Endpoints)
│   │   ├── status.py                 # System operation routes: health probes, diagnostics, and metadata
│   │   ├── tasks.py                  # Task routing context: handles CRUD, querying, pagination, and caching pipelines
│   │   └── users.py                  # User management routing: registration, login exchange, and secure logout
│   ├── core/                         # Low-level systems and structural middlewares
│   │   ├── context.py                # Asynchronous thread-safe context contextvars management (X-Request-ID tracking)
│   │   ├── exceptions.py             # Custom domain exceptions and centralized JSON error-handling responders
│   │   ├── logging.py                # Logging system configuration handling request-scoped tracing context formatting
│   │   ├── middleware.py             # Profiling and error capture layers injecting latency metrics and safety boundaries
│   │   └── redis.py                  # Thread-safe LRU-cached instance initializer for the connection pool
│   ├── database/                     # Persistence schema boundaries
│   │   ├── base.py                   # Global declarative base class configuration for SQLAlchemy models
│   │   ├── db.py                     # PostgreSQL engine initialization and atomic session scope managers
│   │   └── models.py                 # Relational model definitions mapping core domain constraints and entity shapes
│   ├── services/                     # Application Business Logic Layer
│   │   ├── cache_service.py          # Redis memory space management: serialization, key creation, and pattern scans
│   │   ├── task_service.py           # Atomic database interactions checking cross-user safety rules and logical drops
│   │   └── user_service.py           # Identity checks, verification steps against shadow hashes, and access validation
│   ├── config.py                     # Settings parsing checking configurations from .env using Pydantic Settings models
│   ├── dependencies.py               # Dependency Injection graph resolving access privileges and tracking active scopes
│   ├── main.py                       # Main application runtime file putting together middleware sequences and route nodes
│   ├── schemas.py                    # Data transfer definitions (DTOs) with checking logic for user password constraints
│   └── security.py                   # Cryptographic engine processing security keys, token parsing, and secure signing
├── tests/                            # Automated quality suite using Pytest
│   ├── conftest.py                   # Shared configuration setting up isolated db spaces on memory and temporary caching setups
│   ├── test_api.py                   # Tests checking route boundary inputs and error triggers on wrong requests
│   ├── test_integration.py           # Integration scenarios validating data separation rules and multi-stage actions
│   ├── test_services.py              # Unit tests auditing state reactions inside individual logical workers
│   └── test_users.py                 # Tests measuring token lifecycle actions, tracking user entries and logout steps
├── alembic.ini                       # Central instruction set directing paths and processing behaviors for migrations
├── docker-compose.yml                # Configuration file mapping dependencies and ports across runtime systems
├── docker-compose.test.yml           # Isolated platform spinning up temporary testing engines inside memory-backed tables
├── Dockerfile                        # Multi-stage blueprint reducing image sizes and securing run routines under user separation
├── entrypoint.sh                     # Automation file guaranteeing schema modernizations are applied before system initialization
├── nginx.conf                        # Web configuration enforcing speed blocks, data pass-through paths, and proxy tracking
└── requirements.txt                  # List of explicit modules and frameworks setting up the application runtime
```

---

## Environment Variables

Key production variables:

```env
DATABASE_URL=postgresql://user:password@db:5432/dbname
SECRET_KEY=your-super-secret-jwt-key-here
ACCESS_TOKEN_EXPIRE_MINUTES=30
REDIS_URL=redis://redis:6379/0
TASKS_CACHE_TTL=60
```

Docker requirement:

- `localhost` is invalid inside containers;
- Use internal network service names (`db`, `redis`).

---

## Running

```bash
docker compose up --build
```

---

## Public Entry Points

| Endpoint          | Description                                       | Access Level           |
|-------------------|---------------------------------------------------|------------------------|
| `/docs`           | OpenAPI / Swagger Interactive Documentation       | Public                 |
| `/system/ping`    | Core service healthcheck probe (returns `"pong"`) | Public                 |
| `/system/info`    | Application metadata summary                      | Public                 |
| `/system/health`  | Diagnostic state probe                            | Public                 |
| `/system/db-info` | Targets operational DB coordinates                | Authenticated          |
| `/tasks`          | Main Tasks collection operations root             | Authenticated          |
| `/users`          | Authentication, registration, and session nodes   | Public / Authenticated |

---

## Startup Flow

PostgreSQL (Healthcheck) → Redis (Started) → FastAPI App Container → Run Alembic Migrations → Initialize Gunicorn Web
Server → Nginx Reverse Proxy Gateway

---

## Middleware & Observability

The application includes customized observability layers:

### Request Tracking

- `X-Request-ID` header:
    - Forwarded from incoming client parameters if supplied.
    - Auto-generated as a UUIDv4 fallback if missing.
    - Distributed tracing token bound via async context variables (`ContextVar`) to propagate across system log
      messages.

### Performance Tracking

- `X-Response-Time` header injects calculated execution latency with millisecond precision.
- Centralized structured logs capture HTTP method, route targets, response statuses, and associated execution times.

### Example headers

```http
X-Request-ID: 4f36f8c2-6e2f-4b2a-9b22-2f3c9a1a9d6b
X-Response-Time: 3.42ms
```

---

## API Endpoints

### Authentication (`/users` Prefix)

| Method | Endpoint          | Description                                             |
|--------|-------------------|---------------------------------------------------------|
| POST   | `/users/register` | Provisions a new unique user profile                    |
| POST   | `/users/login`    | Validates credentials, issues JWT access token          |
| POST   | `/users/logout`   | Revokes active token via server-side Redis invalidation |
| GET    | `/users/me`       | Retrieves authenticated identity schema mapping         |

---

### Tasks (`/tasks` Prefix)

| Method | Endpoint               | Description                                                   |
|--------|------------------------|---------------------------------------------------------------|
| GET    | `/tasks`               | Lists task entities (supports filtering, sorting, pagination) |
| POST   | `/tasks`               | Contextualizes and stores a new user task                     |
| GET    | `/tasks/{id}`          | Retrieves a specific task (enforces boundary checks)          |
| PUT    | `/tasks/{id}`          | Updates properties of an active task                          |
| PUT    | `/tasks/{id}/complete` | Flips completion state safely                                 |
| DELETE | `/tasks/{id}`          | Transitions task into hidden state (soft delete)              |
| DELETE | `/tasks`               | Mass invalidation / batch soft delete across user records     |
| GET    | `/tasks/count`         | Returns total number of active tasks for user                 |
| GET    | `/tasks/last`          | Retrieves the most recently created task entity               |

---

## Authentication Flow

1. **Register**: Post credentials to `/users/register`.
2. **Login**: Post credentials to `/users/login` → receive cryptographically signed JWT token.
3. **Authorize**: Provide token within subsequent request authorization headers as a `Bearer <Token>`.
4. **Logout**: Hit `/users/logout` → current token ID (`jti`) is recorded to the Redis storage blacklist to prevent
   reuse before expiration.

---

## Rate Limiting (Nginx)

The reverse proxy gateway implements separate rate limiting scopes using Leaky Bucket algorithms via
`$binary_remote_addr`:

- `/users/login`: Max rate of `3r/s` with a burst buffer allowance of 3 requests to mitigate brute-force vector risk.
- `/tasks`: Max rate of `10r/s` with a burst buffer of 10 requests to optimize user-level performance distribution.
- `/system`: Relaxed monitoring bounds at `20r/s` with a burst capacity of 15 requests.
- General fallback limit: `5r/s` with a burst buffer of 5 requests applies to all unspecified asset paths.

---

## Security Model

- **Stateful Token Revocation**: Uses an optimized in-memory key-value database (Redis) to build immediate server-side
  logout mechanics.
- **Cryptographic Foundations**: Strict password validation constraints combined with key derivation mechanisms
  leveraging `bcrypt` running at 12 work rounds.
- **Timing Attack Mitigation**: Intercepts user enumeration strategies via fake hash computation procedures if email
  records do not match database items.
- **Multi-tenant Isolation Audit**: Injects user identification keys explicitly during all database queries to prevent
  cross-tenant operations or horizontal privilege escalation.
- **Database Consistency Guarantees**: Implements underlying relational engine CHECK constraints validating priority
  integers (`BETWEEN 1 AND 5`), string sizes, and explicit soft-delete synchronization.
- **Infrastructure Security**: Eliminates privileged application execution vectors by shifting runtime operation
  profiles to an isolated system account (`appuser`) inside the application container.

---

## Database Model

The relational architecture centers on two tables optimized with performance indices:

- **Users**: Structured to hold primary key constraints (`id`), mandatory uniqueness validations (`username`, `email`),
  hashed password storage (`hashed_password`), and active account indicators (`is_active`).
- **Tasks**: User-scoped record elements using composite multi-column search structures (
  `ix_tasks_user_id_completed_priority`) to guarantee fast retrieval speeds under filtered and ordered lookups.

---

## Key Engineering Notes

- **Transactional Atomicity**: Scoped contexts ensure active transaction rollbacks occur immediately on interception of
  internal failure parameters, protecting persistence accuracy.
- **Cache Integrity Protection**: Distinct data caches isolate multi-user visibility planes, using localized entity
  identification patterns to prevent cross-account cache poisoning.
- **Network Boundaries**: Closes downstream network vector entries; Nginx serves as the sole gateway exposing system
  APIs to the internet.

---

## Load Test Results

Load tests were performed using [Locust](https://locust.io) against the full Docker Compose stack (Nginx → Gunicorn/2
workers → PostgreSQL + Redis) on `GET /tasks` with authenticated users.

| Concurrent Users | RPS  | Median Latency | 95th Percentile | Failure Rate |
|------------------|------|----------------|-----------------|--------------|
| 10               | 8.09 | 8 ms           | 210 ms          | 0.00%        |
| 20               | 8.90 | 7 ms           | 259 ms          | 0.00%        |
| 50               | 8.60 | 8 ms           | 259 ms          | 3.35%        |
At 50 concurrent users the failure rate of 3.35% was caused entirely by Nginx rate limiting (HTTP 429). The application layer returned no errors — all failures originated at the /tasks rate limit zone (10r/s, burst=10).

**Observations:**

- RPS plateaus at ~8–9 across all runs, consistent with 2 Gunicorn/Uvicorn workers configured in the Dockerfile.
- Median latency stays stable at 7–8 ms even under 50 concurrent users, demonstrating effective Redis cache hit
  performance.
- Failures at 50 users are caused by Nginx rate limiting (`tasks_limit: 10r/s, burst=10`): burst capacity is exhausted
  under sustained load, returning HTTP 429.
- 95th percentile jumps from 210 ms to 259 ms between 10 and 20 users and holds there, indicating the latency ceiling is
  set by worker queue depth rather than database or cache.

---

## Author

Vladislav

Backend Engineering • Distributed Systems • Security-Oriented API Design
