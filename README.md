# Task Manager API

## Description

Task Manager API is a backend application built with **FastAPI**.

The project allows users to register, log in, receive a JWT access token, and manage their own tasks. Each user can only access, update, complete, and delete tasks that belong to them.

The application is containerized with Docker, uses PostgreSQL as the main database, Redis for caching, Alembic for database migrations, and includes an isolated Docker test environment.

---

## Features

- User registration
- User login
- Password hashing
- JWT access token authentication
- Current user retrieval
- Task creation
- User-specific task access
- Task retrieval by ID
- Task filtering
- Task sorting
- Task pagination
- Task update
- Task completion
- Single task deletion
- Bulk deletion of current user's tasks
- User-specific task isolation
- Redis caching for task list responses
- Cache invalidation after task changes
- Automatic Alembic migrations on startup
- Dockerized application runtime
- Production-style startup with Gunicorn and Uvicorn workers
- Isolated Docker test environment
- Automated testing with Pytest

---

## Tech Stack

- Python
- FastAPI
- PostgreSQL
- SQLAlchemy
- Alembic
- Redis
- Pydantic
- Pydantic Settings
- JWT authentication
- Passlib / bcrypt
- python-jose
- Docker
- Docker Compose
- Gunicorn
- UvicornWorker ASGI workers
- Pytest
- fakeredis

---

## Architecture

The project follows a layered backend structure:

```text
app/api        — HTTP endpoints and route handlers
app/services   — business logic
app/database   — SQLAlchemy engine, models, sessions, and Base
app/core       — Redis, cache helpers, middleware, logging, and exceptions
alembic        — database migrations
tests          — API, integration, and service tests
```

This structure separates HTTP logic, business logic, database configuration, infrastructure code, and tests.

---

## Environment Variables

Create a `.env` file based on `.env.example`.

Example:

```env
DB_HOST=localhost
DB_PORT=5433
APP_TITLE=Task Manager API
DATABASE_URL=postgresql://username:password@localhost:5433/database_name
TEST_DATABASE_URL=postgresql://username:password@localhost:5433/test_database_name
SECRET_KEY=replace-with-generated-secret
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REDIS_URL=redis://localhost:6379/0
TASKS_CACHE_TTL=60
```

For Docker Compose, environment variables are used by the application container, PostgreSQL container, and Redis container.

---

## Run with Docker

Start the application with Docker Compose:

```bash
docker compose up --build
```

The application container runs database migrations automatically before starting the web server.

Startup flow:

```text
entrypoint.sh
  -> alembic upgrade head
  -> gunicorn app.main:app with Uvicorn workers
```

The application server is started using:

```text
Gunicorn master process + Uvicorn workers
```

API documentation:

```text
http://localhost:8000/docs
```

---

## Run Locally

Clone the repository:

```bash
git clone <repository-url>
cd <repository-name>
```

Create and activate a virtual environment:

```bash
python -m venv .venv
source .venv/bin/activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Start the application locally:

```bash
python -m uvicorn app.main:app --reload
```

API documentation:

```text
http://127.0.0.1:8000/docs
```

Local development can use Uvicorn directly. Docker startup uses Gunicorn with Uvicorn workers.

---

## Run Tests in Docker

Run the test environment:

```bash
docker compose -f docker-compose.test.yml -p my_first_project_test run --rm test-runner
```

The test environment uses an isolated PostgreSQL container named `test_db`.

The test database is not exposed to the host machine and uses `tmpfs` for temporary storage.

Expected result:

```text
25 passed
```

---

## API Endpoints

### System

- `GET /system/ping`
- `GET /system/info`
- `GET /system/db-info`

### Users

- `POST /users/register`
- `POST /users/login`
- `GET /users/me`

### Tasks

- `GET /tasks`
- `POST /tasks`
- `GET /tasks/count`
- `GET /tasks/last`
- `GET /tasks/{task_id}`
- `PUT /tasks/{task_id}`
- `PUT /tasks/{task_id}/complete`
- `DELETE /tasks/{task_id}`
- `DELETE /tasks`

---

## Production Notes

- The application uses fail-fast configuration through Pydantic Settings.
- Alembic migrations run before the web server starts.
- The production container runs Gunicorn with Uvicorn workers.
- Redis is used for caching task list responses.
- Cache is invalidated after task create, update, complete, and delete operations.
- The application runs as a non-root user inside Docker.
- Tests run in an isolated Docker environment with a separate PostgreSQL database.

---

## Author

Vladislav