from typing import Optional

from fastapi import APIRouter, Depends
from fastapi import Query
from sqlalchemy.orm import Session

from app.database.db import get_db
from app.database.models import User
from app.dependencies import get_current_user_dependency
from app.schemas import TaskCreate, TaskResponse, SortByFields, OrderOptions
from app.services.task_service import complete_task as complete_task_service
from app.services.task_service import create_task as create_task_service
from app.services.task_service import delete_task as delete_task_service
from app.services.task_service import delete_tasks as delete_tasks_service
from app.services.task_service import find_task
from app.services.task_service import get_tasks as get_tasks_service
from app.services.task_service import task_count as task_count_service
from app.services.task_service import task_last as task_last_service
from app.services.task_service import update_task as update_task_service

router = APIRouter()


@router.get("/tasks", response_model=list[TaskResponse])
def get_tasks(
        completed: Optional[bool] = None,
        priority: Optional[int] = None,
        limit: int = Query(default=10, le=100),
        offset: int = Query(default=0, ge=0),
        sort_by: SortByFields = SortByFields.id,
        order: OrderOptions = OrderOptions.asc,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user_dependency)
):
    db_tasks = get_tasks_service(
        db=db,
        current_user=current_user,
        completed=completed,
        priority=priority,
        limit=limit,
        offset=offset,
        sort_by=sort_by,
        order=order
    )
    return db_tasks


@router.post("/tasks", status_code=201, response_model=TaskResponse)
def add_task(item: TaskCreate, db: Session = Depends(get_db),
             current_user: User = Depends(get_current_user_dependency)):
    db_task = create_task_service(item, db, current_user)
    return db_task


@router.get("/tasks/count", response_model=int)
def task_count(db: Session = Depends(get_db), current_user: User = Depends(get_current_user_dependency)):
    db_tasks = task_count_service(db, current_user)
    return db_tasks


@router.get("/tasks/last", response_model=TaskResponse)
def task_last(db: Session = Depends(get_db), current_user: User = Depends(get_current_user_dependency)):
    db_task = task_last_service(db, current_user)
    return db_task


@router.get("/tasks/{task_id}", response_model=TaskResponse)
def get_task(task_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user_dependency)):
    db_task = find_task(task_id, db, current_user)
    return db_task


@router.delete("/tasks/{task_id}", response_model=TaskResponse)
def delete_task(task_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user_dependency)):
    db_task = delete_task_service(task_id, db, current_user)
    return db_task


@router.delete("/tasks", response_model=list[TaskResponse])
def delete_tasks(db: Session = Depends(get_db), current_user: User = Depends(get_current_user_dependency)):
    db_tasks = delete_tasks_service(db, current_user)
    return db_tasks


@router.put("/tasks/{task_id}/complete", response_model=TaskResponse)
def complete_task(task_id: int, db: Session = Depends(get_db),
                  current_user: User = Depends(get_current_user_dependency)):
    db_task = complete_task_service(task_id, db, current_user)
    return db_task


@router.put("/tasks/{task_id}", response_model=TaskResponse)
def update_task(task_id: int, item: TaskCreate, db: Session = Depends(get_db),
                current_user: User = Depends(get_current_user_dependency)):
    db_task = update_task_service(task_id, item, db, current_user)
    return db_task
