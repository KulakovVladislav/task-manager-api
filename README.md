# Task Manager API

## Description

**Task Manager API** is a production-ready backend application built with **FastAPI**, focused on security, scalability, and high performance.

The application uses **Nginx** as a Reverse Proxy and API Gateway to protect the internal Docker network. Users can register, authenticate with JWT, and manage their own isolated tasks.

The system uses **PostgreSQL** for persistent storage, **Redis** for stateful caching, and **Alembic** for automated database migrations.

---

## Features

### User Authentication

- Secure user registration and login
- Password hashing with **bcrypt**
- Stateless authentication using **JWT access tokens**
- Protected user-specific routes

### Task Management

- Full CRUD operations for tasks
- Strict user-specific task isolation
- Filtering, sorting, and pagination
- Bulk deletion of tasks owned by the authenticated user

### Performance Optimization

- Redis-based caching for intensive read queries, especially `GET /tasks`
- Automatic cache invalidation on task mutations:
  - create
  - update
  - delete
  - bulk delete

### Infrastructure & Security

- **Single public entrypoint:** Nginx exposes the application through port `8080`
- **Network isolation:** the FastAPI container is not exposed directly to the host machine
- **Private upstream:** port `8000` is available only inside the internal Docker network
- **Rate limiting:** endpoint-specific traffic limits with immediate `429 Too Many Requests` responses
- **HTTP buffering:** request and response buffering protects the Python upstream from slow-client attacks
- **Header sanitization:** Nginx injects proxy headers such as:
  - `X-Real-IP`
  - `X-Forwarded-For`
  - `X-Forwarded-Proto`

### Database Lifecycle

- Automated database schema migrations on application startup using **Alembic**

### Resilient Runtime

- Production-grade execution with **Gunicorn**
- **Uvicorn ASGI workers** managed by the Gunicorn master process

### Testing

- Fully isolated Docker-based test environment
- Automated test suites with **Pytest**
- Ephemeral storage using `tmpfs`
- Redis mocking with **fakeredis**

---

## Tech Stack

### Core

- Python
- FastAPI
- Pydantic
- Pydantic Settings

### Database & Migrations

- PostgreSQL
- SQLAlchemy AsyncIO
- Alembic

### Caching

- Redis
- redis-py

### Security

- JWT
- python-jose
- Passlib
- bcrypt

### Proxy & Traffic Control

- Nginx

### Process Management

- Gunicorn
- Uvicorn

### Testing

- Pytest
- fakeredis
- AsyncHTTPClient

---

## Architecture

The project follows a strict layered backend architecture with an isolated container network.

```text
       [ Public Internet ]
               |
      (Port 8080: HTTP)
               v
     +-------------------+
     |   Nginx Gateway   |
     | Rate Limiting     |
     | Buffering         |
     | Header Injection  |
     +-------------------+
               |
    (Internal Docker Network)
               v
     +-------------------+
     |    FastAPI App    |
     |  Gunicorn Master  |
     | Uvicorn Workers   |
     | Port 8000         |
     | Internal Only     |
     +-------------------+
        |             |
        v             v
  +------------+  +-----------+
  | PostgreSQL |  |   Redis   |
  +------------+  +-----------+
```

---

## Directory Structure

```text
app/api        — HTTP endpoints, routers, and request/response schemas
app/services   — Core business logic and transaction management
app/database   — SQLAlchemy engine setup, declarative models, and session lifecycle
app/core       — Global infrastructure: Redis config, cache invalidation, middleware, and custom exceptions
alembic        — Database migration history and environment configuration
tests          — Isolated API integration and unit test suites
```

---

## Environment Variables

Create a `.env` file based on `.env.example`.

```env
DB_HOST=postgres
DB_PORT=5432

APP_TITLE=Task Manager API

DATABASE_URL=postgresql+asyncpg://postgres:securepassword@postgres:5432/taskmanager
TEST_DATABASE_URL=postgresql+asyncpg://postgres:securepassword@test_db:5432/taskmanager_test

SECRET_KEY=d3f4b... # Replace with a cryptographically secure 32-byte hex string
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

REDIS_URL=redis://redis:6379/0
TASKS_CACHE_TTL=60
```

> **Note:** When running inside Docker Compose, service hostnames such as `DB_HOST` and `REDIS_URL` must reference internal Docker service names, for example `postgres` and `redis`, instead of `localhost`.

---

## Run with Docker

To start the full production-ready infrastructure layer, including Nginx, FastAPI, PostgreSQL, and Redis, run:

```bash
docker compose up --build
```

### Network Entrypoints

| Purpose | URL |
|---|---|
| Public API Gateway | `http://localhost:8080` |
| Swagger Documentation | `http://localhost:8080/docs` |
| API Routes | `http://localhost:8080/api/...` |

### Security Constraint

Direct access to the FastAPI application through port `8000` is disabled from the host machine.

```text
http://localhost:8000
```

This address should fail because port `8000` is private and available only inside the internal Docker network.

---

## Startup Pipeline

```text
docker-compose boot
  -> PostgreSQL and Redis healthchecks pass
  -> entrypoint.sh executes: alembic upgrade head
  -> Gunicorn starts and binds to internal port 8000
  -> UvicornWorker processes are launched
  -> Nginx opens the public socket on host port 8080
  -> Nginx proxies requests to the internal FastAPI upstream
```

---

## Run Locally

For local development and debugging without the full Docker infrastructure, run the application directly.

### 1. Clone the repository

```bash
git clone <repository-url>
cd <repository-name>
```

### 2. Create and activate a virtual environment

```bash
python -m venv .venv
source .venv/bin/activate
```

For Windows:

```bash
.venv\Scripts\activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Start the application

```bash
python -m uvicorn app.main:app --reload --port 8000
```

### Local Documentation

```text
http://127.0.0.1:8000/docs
```

---

## Run Tests in Docker

Run the test suite inside an isolated Docker environment:

```bash
docker compose -f docker-compose.test.yml -p task_manager_test run --rm test-runner
```

---

## Test Isolation Matrix

| Component | Isolation Strategy |
|---|---|
| Database | Dedicated `test_db` PostgreSQL container |
| Storage | `tmpfs` RAM-based database files |
| Cache | `fakeredis` for Redis transaction mocking |
| Runtime | Separate Docker Compose test project |
| Persistence | Zero persistence after test execution |

---

## API Endpoints & Rate Limiting

Traffic limits are enforced by Nginx at the gateway layer.

| Endpoint Group | Prefix | Rate Limit per IP | Burst | Over-limit Action |
|---|---:|---:|---:|---|
| Authentication | `/users/login` | 3 requests / sec | 3 | `HTTP 429 Too Many Requests` |
| Task Operations | `/tasks` | 10 requests / sec | 10 | `HTTP 429 Too Many Requests` |
| System Operations | `/system` | 20 requests / sec | 15 | `HTTP 429 Too Many Requests` |
| Fallback / Core API | `/` | 5 requests / sec | 5 | `HTTP 429 Too Many Requests` |

---

## Endpoint Inventory

### System

| Method | Endpoint | Description |
|---|---|---|
| GET | `/system/ping` | Layer 7 healthcheck |
| GET | `/system/info` | Runtime diagnostics |
| GET | `/system/db-info` | Database connectivity trace |

### Users

| Method | Endpoint | Description |
|---|---|---|
| POST | `/users/register` | Create a new user profile |
| POST | `/users/login` | Generate an OAuth2-compatible access token |
| GET | `/users/me` | Extract current user claims context |

### Tasks

| Method | Endpoint | Description |
|---|---|---|
| GET | `/tasks` | Cached task list with filtering, sorting, and pagination |
| POST | `/tasks` | Create a new task and invalidate cache |
| GET | `/tasks/count` | Return task aggregation count |
| GET | `/tasks/last` | Fetch the latest user task |
| GET | `/tasks/{task_id}` | Retrieve an isolated task by ID |
| PUT | `/tasks/{task_id}` | Update task fields |
| PUT | `/tasks/{task_id}/complete` | Complete task with an atomic state transition |
| DELETE | `/tasks/{task_id}` | Delete a single task |
| DELETE | `/tasks` | Bulk delete all tasks owned by the authenticated user |

---

## Production Notes

### Fail-Fast Configuration

The application validates critical environment variables using **Pydantic Settings**. If required values such as `SECRET_KEY` or `DATABASE_URL` are missing or malformed, the application refuses to start.

### Upstream Protection

Nginx uses `proxy_request_buffering on;` to ensure that the ASGI application is not blocked by slow clients sending request payloads gradually.

### Response Buffering

Nginx uses `proxy_buffering on;` to let Nginx handle response delivery while Gunicorn workers are freed earlier to process new requests.

### Least Privilege Runtime

The application runs inside Docker containers under a custom non-root user account to reduce privilege escalation risks.

---

## Author

**Vladislav**  
Backend Infrastructure & API Engineering