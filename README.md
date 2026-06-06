# Task Manager API

A production-style **Task Manager REST API** built with **FastAPI**, **PostgreSQL**, **Redis**, **Nginx**, **Docker**, **Alembic**, **JWT authentication**, and an isolated automated testing environment.

The project demonstrates a backend architecture with authentication, user-specific task isolation, caching, soft deletion, database migrations, reverse proxy protection, request rate limiting, middleware-based profiling, and Dockerized runtime infrastructure.

---

## Overview

**Task Manager API** allows users to register, log in, and manage their own tasks through protected API endpoints.

Each authenticated user can only access their own tasks. The application uses JWT bearer tokens for authorization, PostgreSQL for persistent storage, Redis for caching task list queries, and Nginx as the only public HTTP entrypoint.

The application is designed to run inside Docker Compose, where the FastAPI application is kept private inside the Docker network and exposed only through the Nginx gateway on port `8080`.

---

## Core Features

### Authentication & Authorization

- User registration with unique username and email validation
- Login with email and password
- JWT access token generation
- Protected routes using `Authorization: Bearer <token>`
- Password hashing with bcrypt through Passlib
- Strong password validation:
  - minimum length
  - uppercase letter required
  - digit required
  - special character required
- Dummy password hash verification for non-existing users to reduce timing-based user enumeration risk

---

### Task Management

- Create tasks
- Get task list
- Get task by ID
- Get latest task
- Get task count
- Update task
- Mark task as completed
- Delete one task
- Bulk delete all current user tasks
- Filter tasks by:
  - completion status
  - priority
- Sort tasks by:
  - `id`
  - `priority`
- Sort order:
  - ascending
  - descending
- Pagination with `limit` and `offset`
- User-level task isolation

---

### Soft Delete

Tasks are not physically removed from the database when deleted.

Instead, the application marks them as deleted using:

```text
is_deleted = true
deleted_at = current UTC datetime
```

Soft-deleted tasks are hidden from normal API responses and cannot be updated, fetched, or deleted again through the public API.

---

### Redis Caching

The `GET /tasks` endpoint uses Redis caching.

Cache keys are based on:

- user ID
- completion filter
- priority filter
- limit
- offset
- sort field
- sort order

Example cache key structure:

```text
tasks:user:{user_id}:comp:{completed}:prio:{priority}:lim:{limit}:off:{offset}:sb:{sort_by}:ord:{order}
```

The cache is automatically invalidated when the authenticated user changes task data through:

- task creation
- task update
- task completion
- single task delete
- bulk task delete

Default cache TTL:

```text
TASKS_CACHE_TTL=60
```

---

## Tech Stack

### Backend

- Python
- FastAPI
- Pydantic
- Pydantic Settings
- SQLAlchemy ORM
- PostgreSQL
- Alembic

### Security

- JWT
- python-jose
- Passlib
- bcrypt
- OAuth2 Bearer token flow

### Caching

- Redis
- redis-py
- fakeredis for tests

### Infrastructure

- Docker
- Docker Compose
- Nginx
- Gunicorn
- Uvicorn workers

### Testing

- Pytest
- FastAPI TestClient
- fakeredis
- Dedicated PostgreSQL test container
- Docker Compose test environment
- tmpfs-based database storage for test isolation

---

## Architecture

```text
              Client / Browser / API Consumer
                         |
                         |
                  http://localhost:8080
                         |
                         v
              +----------------------+
              |        Nginx         |
              |----------------------|
              | Reverse Proxy        |
              | Rate Limiting        |
              | Header Forwarding    |
              | Request Buffering    |
              | Response Buffering   |
              +----------------------+
                         |
                         |
              Internal Docker Network
                         |
                         v
              +----------------------+
              |      FastAPI App     |
              |----------------------|
              | Gunicorn Master      |
              | Uvicorn Workers      |
              | Internal Port 8000   |
              +----------------------+
                    |             |
                    |             |
                    v             v
          +----------------+   +----------------+
          |   PostgreSQL   |   |     Redis      |
          | Persistent DB  |   | Task Caching   |
          +----------------+   +----------------+
```

---

## Project Structure

```text
My_first_project
├── app
│   ├── api
│   │   ├── status.py          # System and health endpoints
│   │   ├── tasks.py           # Task API routes
│   │   └── users.py           # User registration, login, profile routes
│   ├── core
│   │   ├── exceptions.py      # Domain exceptions and exception handlers
│   │   ├── logging.py         # Profiler logger setup
│   │   ├── middleware.py      # Profiling and unexpected error middleware
│   │   └── redis.py           # Redis client factory
│   ├── database
│   │   ├── base.py            # SQLAlchemy declarative base
│   │   ├── db.py              # Engine, session factory, DB dependency
│   │   └── models.py          # User and Task models
│   ├── services
│   │   ├── cache_service.py   # Cache key, read, write, invalidation logic
│   │   ├── task_service.py    # Task business logic
│   │   └── user_service.py    # User business logic and auth helpers
│   ├── config.py              # Environment-based application settings
│   ├── dependencies.py        # Shared FastAPI dependencies
│   ├── main.py                # FastAPI app creation and router registration
│   ├── schemas.py             # Pydantic request and response schemas
│   └── security.py            # Password hashing and JWT logic
├── alembic
│   ├── env.py                 # Alembic environment configuration
│   └── versions               # Database migration files
├── tests
│   ├── conftest.py            # Test fixtures and dependency overrides
│   ├── test_api.py            # Basic API tests
│   ├── test_integration.py    # Integration and security behavior tests
│   ├── test_services.py       # Service and caching tests
│   └── test_users.py          # User auth and validation tests
├── Dockerfile                 # Multi-stage application image
├── docker-compose.yml         # Main Docker infrastructure
├── docker-compose.test.yml    # Isolated test infrastructure
├── entrypoint.sh              # Runs migrations before app startup
├── nginx.conf                 # Reverse proxy and rate limit config
├── requirements.txt           # Python dependencies
└── README.md
```

---

## Environment Variables

Create a `.env` file in the project root.

Example:

```env
DB_HOST=db
DB_PORT=5432

APP_TITLE=Task Manager API

DATABASE_URL=postgresql://vladislav:your_secret_key_here@db:5432/my_first_project_db
TEST_DATABASE_URL=postgresql://test_user:test_password123!@test_db:5432/test_postgres

SECRET_KEY=replace_this_with_a_secure_secret_key
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

REDIS_URL=redis://redis:6379/0
TASKS_CACHE_TTL=60
```

Important Docker note:

When running inside Docker Compose, database and Redis hosts must use Docker service names, not `localhost`.

Correct Docker values:

```text
DB_HOST=db
REDIS_URL=redis://redis:6379/0
```

---

## Running with Docker

Start the full infrastructure:

```bash
docker compose up --build
```

This starts:

- FastAPI application container
- PostgreSQL database
- Redis cache
- Nginx reverse proxy

---

## Public Entrypoints

| Purpose | URL |
|---|---|
| API Gateway | `http://localhost:8080` |
| Swagger UI | `http://localhost:8080/docs` |
| OpenAPI JSON | `http://localhost:8080/openapi.json` |
| System Ping | `http://localhost:8080/system/ping` |
| Main API Routes | `http://localhost:8080/tasks`, `http://localhost:8080/users`, `http://localhost:8080/system` |

The FastAPI application runs internally on port `8000`, but that port is not published to the host by `docker-compose.yml`.

This means the public API should be accessed through:

```text
http://localhost:8080
```

Not through:

```text
http://localhost:8000
```

---

## Startup Flow

```text
docker compose up --build
        |
        v
PostgreSQL healthcheck
        |
        v
Redis container starts
        |
        v
FastAPI app container starts
        |
        v
entrypoint.sh executes alembic upgrade head
        |
        v
Gunicorn starts on internal port 8000
        |
        v
Uvicorn worker processes serve FastAPI
        |
        v
Nginx exposes public port 8080
        |
        v
Requests are proxied to FastAPI through the internal Docker network
```

---

## Running Locally Without Docker

For local development, install dependencies and run Uvicorn directly.

### 1. Clone the repository

```bash
git clone <repository-url>
cd My_first_project
```

### 2. Create a virtual environment

```bash
python -m venv .venv
```

### 3. Activate the virtual environment

Linux/macOS:

```bash
source .venv/bin/activate
```

Windows:

```bash
.venv\Scripts\activate
```

### 4. Install dependencies

```bash
pip install -r requirements.txt
```

### 5. Configure `.env`

For local execution, `DATABASE_URL` and `REDIS_URL` should point to services reachable from your machine.

Example:

```env
DATABASE_URL=postgresql://vladislav:your_secret_key_here@localhost:5433/my_first_project_db
REDIS_URL=redis://localhost:6379/0
```

### 6. Run migrations

```bash
alembic upgrade head
```

### 7. Start the application

```bash
python -m uvicorn app.main:app --reload --port 8000
```

Local documentation:

```text
http://127.0.0.1:8000/docs
```

---

## Running Tests

Run the test suite in the isolated Docker test environment:

```bash
docker compose -f docker-compose.test.yml -p task_manager_test run --rm test-runner
```

The test environment uses:

- separate PostgreSQL container
- separate Docker Compose project name
- tmpfs storage for database files
- fakeredis instead of real Redis inside application tests
- dependency overrides for database and cache clients
- automatic schema creation and teardown per test function

---

## Test Coverage Highlights

The tests verify:

- user registration
- duplicate username handling
- invalid email validation
- weak password validation
- login with valid credentials
- login with invalid credentials
- JWT-protected routes
- task creation
- task validation
- task pagination
- task filtering
- task sorting
- user-to-user task isolation
- soft delete behavior
- deleted task visibility rules
- deleted task update prevention
- deleted task double-delete prevention
- domain exception handling
- middleware response time header
- transaction rollback on unexpected exceptions
- Redis cache usage
- Redis cache invalidation
- dummy password verification for missing users

---

## API Endpoints

### System

| Method | Endpoint | Auth Required | Description |
|---|---|---:|---|
| GET | `/system/` | No | Basic root system response |
| GET | `/system/ping` | No | Healthcheck endpoint |
| GET | `/system/info` | No | Application status and title |
| GET | `/system/db-info` | No | Database host and port info |
| GET | `/system/hello` | No | Simple test endpoint |

---

### Users

| Method | Endpoint | Auth Required | Description |
|---|---|---:|---|
| POST | `/users/register` | No | Register a new user |
| POST | `/users/login` | No | Log in and receive JWT access token |
| GET | `/users/me` | Yes | Return current authenticated user |

---

### Tasks

| Method | Endpoint | Auth Required | Description |
|---|---|---:|---|
| GET | `/tasks` | Yes | Get current user's tasks with filtering, sorting, pagination, and Redis caching |
| POST | `/tasks` | Yes | Create a task |
| GET | `/tasks/count` | Yes | Get current user's active task count |
| GET | `/tasks/last` | Yes | Get current user's latest active task |
| GET | `/tasks/{task_id}` | Yes | Get a single task by ID |
| PUT | `/tasks/{task_id}` | Yes | Update task title, description, and priority |
| PUT | `/tasks/{task_id}/complete` | Yes | Mark task as completed |
| DELETE | `/tasks/{task_id}` | Yes | Soft-delete a single task |
| DELETE | `/tasks` | Yes | Soft-delete all current user's active tasks |

---

## Task Query Parameters

`GET /tasks` supports the following query parameters:

| Parameter | Type | Default | Rules |
|---|---|---:|---|
| `completed` | boolean | `null` | Optional completion filter |
| `priority` | integer | `null` | Optional priority filter |
| `limit` | integer | `10` | Maximum `100` |
| `offset` | integer | `0` | Minimum `0` |
| `sort_by` | string | `id` | Allowed: `id`, `priority` |
| `order` | string | `asc` | Allowed: `asc`, `desc` |

Example:

```bash
curl "http://localhost:8080/tasks?completed=false&priority=3&limit=10&offset=0&sort_by=priority&order=desc" \
  -H "Authorization: Bearer <access_token>"
```

---

## Authentication Flow

### 1. Register

```bash
curl -X POST "http://localhost:8080/users/register" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "vladislav",
    "email": "vladislav@example.com",
    "password": "Strong_password_123@"
  }'
```

Example response:

```json
{
  "id": 1,
  "username": "vladislav",
  "email": "vladislav@example.com",
  "is_active": true
}
```

---

### 2. Login

```bash
curl -X POST "http://localhost:8080/users/login" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "vladislav@example.com",
    "password": "Strong_password_123@"
  }'
```

Example response:

```json
{
  "access_token": "<jwt_token>",
  "token_type": "bearer",
  "expires_in": 30
}
```

---

### 3. Use Protected Endpoints

```bash
curl "http://localhost:8080/users/me" \
  -H "Authorization: Bearer <access_token>"
```

---

## Task Examples

### Create Task

```bash
curl -X POST "http://localhost:8080/tasks" \
  -H "Authorization: Bearer <access_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Learn FastAPI",
    "description": "Build a clean backend project",
    "priority": 3
  }'
```

---

### Get Tasks

```bash
curl "http://localhost:8080/tasks" \
  -H "Authorization: Bearer <access_token>"
```

---

### Get Filtered Tasks

```bash
curl "http://localhost:8080/tasks?completed=false&priority=3" \
  -H "Authorization: Bearer <access_token>"
```

---

### Update Task

```bash
curl -X PUT "http://localhost:8080/tasks/1" \
  -H "Authorization: Bearer <access_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Learn FastAPI deeply",
    "description": "Study routing, dependencies, middleware, auth, and testing",
    "priority": 5
  }'
```

---

### Complete Task

```bash
curl -X PUT "http://localhost:8080/tasks/1/complete" \
  -H "Authorization: Bearer <access_token>"
```

---

### Delete Task

```bash
curl -X DELETE "http://localhost:8080/tasks/1" \
  -H "Authorization: Bearer <access_token>"
```

---

### Delete All Current User Tasks

```bash
curl -X DELETE "http://localhost:8080/tasks" \
  -H "Authorization: Bearer <access_token>"
```

Example response:

```json
{
  "deleted_count": 5
}
```

---

## Nginx Gateway

Nginx is used as the public API gateway.

It provides:

- single public entrypoint
- reverse proxying to the internal FastAPI container
- request rate limiting
- proxy headers
- request buffering
- response buffering

Configured forwarded headers:

```text
Host
X-Real-IP
X-Forwarded-For
X-Forwarded-Proto
```

---

## Rate Limiting

Rate limiting is enforced at the Nginx layer.

| Location | Rate Limit | Burst | Over-limit Response |
|---|---:|---:|---|
| `/users/login` | 3 requests / second | 3 | `429 Too Many Requests` |
| `/tasks` | 10 requests / second | 10 | `429 Too Many Requests` |
| `/system` | 20 requests / second | 15 | `429 Too Many Requests` |
| `/` | 5 requests / second | 5 | `429 Too Many Requests` |

---

## Middleware

The application includes custom middleware for:

- measuring request processing time
- logging method, path, status code, and latency
- adding the `X-Response-Time` response header
- catching unexpected exceptions
- returning a safe `500 Internal Server Error` JSON response

Example response header:

```text
X-Response-Time: 3.42ms
```

---

## Database Schema

### Users Table

| Column | Type | Description |
|---|---|---|
| `id` | integer | Primary key |
| `username` | string | Unique username |
| `email` | string | Unique email |
| `hashed_password` | string | Hashed user password |
| `is_active` | boolean | User activity flag |

---

### Tasks Table

| Column | Type | Description |
|---|---|---|
| `id` | integer | Primary key |
| `title` | string | Task title |
| `description` | string | Task description |
| `completed` | boolean | Completion status |
| `user_id` | integer | Owner user ID |
| `priority` | integer | Priority from 1 to 5 |
| `is_deleted` | boolean | Soft delete flag |
| `deleted_at` | datetime | Soft delete timestamp |

The tasks table also contains a composite index:

```text
ix_tasks_user_id_completed_priority
```

Indexed columns:

```text
user_id, completed, priority
```

This improves common user-scoped filtering patterns.

---

## Database Migrations

Alembic is used for schema migrations.

Apply migrations manually:

```bash
alembic upgrade head
```

Create a new migration:

```bash
alembic revision --autogenerate -m "migration_message"
```

On Docker startup, migrations are applied automatically by `entrypoint.sh`:

```sh
alembic upgrade head
```

---

## Docker Image

The Dockerfile uses a multi-stage build:

### Builder stage

- creates a virtual environment
- installs Python dependencies
- copies project files

### Runner stage

- copies the prepared virtual environment
- copies only runtime project files
- creates a non-root `appuser`
- runs the app under the non-root user
- starts through `entrypoint.sh`

Application startup command:

```bash
gunicorn app.main:app \
  --bind 0.0.0.0:8000 \
  --workers 2 \
  --worker-class uvicorn.workers.UvicornWorker \
  --log-level info \
  --access-logfile - \
  --error-logfile -
```

---

## Docker Compose Services

| Service | Description |
|---|---|
| `app` | FastAPI application running through Gunicorn and Uvicorn workers |
| `db` | PostgreSQL database |
| `redis` | Redis cache |
| `nginx` | Public reverse proxy and API gateway |

---

## Security Notes

The project includes several backend security practices:

- password hashing with bcrypt
- JWT-based authentication
- protected task routes
- user-specific data isolation
- soft deletion instead of direct destructive removal
- Nginx rate limiting
- FastAPI app hidden behind internal Docker network
- non-root Docker runtime user
- safe JSON responses for unexpected server errors
- environment-based secret configuration
- strong password validation
- unique username and email constraints
- cache isolation by user ID

---

## Validation Rules

### User Registration

```json
{
  "username": "required string",
  "email": "valid email",
  "password": "required strong password"
}
```

Password requirements:

```text
minimum 8 characters
at least one uppercase letter
at least one digit
at least one special symbol
maximum 64 characters
```

---

### Task Creation / Update

```json
{
  "title": "required non-empty string",
  "description": "required non-empty string",
  "priority": 1
}
```

Priority rules:

```text
minimum: 1
maximum: 5
default: 1
```

---

## Important Implementation Details

- SQLAlchemy is used in synchronous ORM mode with `create_engine` and `Session`.
- Database sessions commit after successful request handling and rollback on exceptions.
- Redis is accessed through `redis.from_url`.
- Tests override database and Redis dependencies.
- Soft-deleted tasks remain in the database but are excluded from active task queries.
- `/tasks/count` counts only active, non-deleted tasks.
- `/tasks/last` returns the latest active, non-deleted task.
- `GET /tasks/{task_id}` returns `404` when another user tries to access a task they do not own.
- Task cache is invalidated per user, not globally.
- Nginx is the only public HTTP entrypoint in the Docker setup.

---

## Author

**Vladislav**  
Backend API Development • Infrastructure • Dockerized Services • Authentication • Testing