# Task Manager API

## Description

Task Manager API is a backend application built with FastAPI.

The project allows users to register, log in, receive a JWT access token, and manage their own tasks. Each user can only
access, update, complete, and delete tasks that belong to them.

## Tech Stack

- Python
- FastAPI
- PostgreSQL
- SQLAlchemy
- Pydantic
- JWT authentication
- Passlib
- python-jose
- Uvicorn

## Features

- User registration
- User login
- Password hashing
- JWT access token authentication
- Get current user
- Create tasks
- Get only current user's tasks
- Get task by ID
- Update task
- Mark task as completed
- Delete one task
- Delete all current user's tasks
- User-specific task isolation

## Installation

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

## Environment Variables

Create a `.env` file based on `.env.example`:

```env
DB_HOST=localhost
DB_PORT=5432
APP_TITLE=Task Manager API
DATABASE_URL=postgresql://username:password@localhost:5432/database_name
SECRET_KEY=your-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

## Run

Start the application:

```bash
python -m uvicorn app.main:app --reload
```

Open API docs:

```text
http://127.0.0.1:8000/docs
```

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

## Author

Vladislav