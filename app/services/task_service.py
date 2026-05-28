from datetime import datetime, timezone
from typing import Optional

from fastapi import HTTPException
from sqlalchemy.orm import Query, Session

from app.database.models import Task, User
from app.schemas import TaskCreate


def _active_user_tasks_query(db: Session, current_user: User) -> Query:
    return (
        db.query(Task)
        .filter(
            Task.user_id == current_user.id,
            Task.is_deleted.is_(False),
        )
    )


def find_task(task_id: int, db: Session, current_user: User):
    db_task = (
        _active_user_tasks_query(db, current_user)
        .filter(Task.id == task_id)
        .first()
    )

    if db_task is None:
        raise HTTPException(status_code=404, detail="Task not found")

    return db_task


def get_tasks(
    db: Session,
    current_user: User,
    completed: Optional[bool],
    priority: Optional[int],
    limit: int,
    offset: int,
    sort_by: str,
    order: str,
    is_deleted: Optional[bool] = False,
):
    if is_deleted is False:
        query = _active_user_tasks_query(db, current_user)
    else:
        query = db.query(Task).filter(Task.user_id == current_user.id)

        if is_deleted is not None:
            query = query.filter(Task.is_deleted == is_deleted)

    if completed is not None:
        query = query.filter(Task.completed == completed)

    if priority is not None:
        query = query.filter(Task.priority == priority)

    order_column = getattr(Task, sort_by)

    if order == "desc":
        query = query.order_by(order_column.desc())
    else:
        query = query.order_by(order_column.asc())

    return query.offset(offset).limit(limit).all()


def create_task(item: TaskCreate, db: Session, current_user: User):
    db_task = Task(
        title=item.title,
        description=item.description,
        user_id=current_user.id,
        completed=False,
        priority=item.priority,
        is_deleted=False,
        deleted_at=None,
    )

    db.add(db_task)
    db.commit()
    db.refresh(db_task)

    return db_task


def update_task(task_id: int, item: TaskCreate, db: Session, current_user: User):
    db_task = find_task(task_id, db, current_user)

    db_task.title = item.title
    db_task.description = item.description
    db_task.priority = item.priority

    db.commit()
    db.refresh(db_task)

    return db_task


def complete_task(task_id: int, db: Session, current_user: User):
    db_task = find_task(task_id, db, current_user)

    db_task.completed = True

    db.commit()
    db.refresh(db_task)

    return db_task


def delete_task(task_id: int, db: Session, current_user: User):
    db_task = find_task(task_id, db, current_user)

    db_task.is_deleted = True
    db_task.deleted_at = datetime.now(timezone.utc)

    db.commit()
    db.refresh(db_task)

    return db_task


def task_count(db: Session, current_user: User):
    return _active_user_tasks_query(db, current_user).count()


def task_last(db: Session, current_user: User):
    db_task = (
        _active_user_tasks_query(db, current_user)
        .order_by(Task.id.desc())
        .first()
    )

    if db_task is None:
        raise HTTPException(status_code=404, detail="Task not found")

    return db_task


def delete_tasks(db: Session, current_user: User):
    deleted_at = datetime.now(timezone.utc)

    updated_count = (
        _active_user_tasks_query(db, current_user)
        .update(
            {
                Task.is_deleted: True,
                Task.deleted_at: deleted_at,
            },
            synchronize_session=False,
        )
    )

    db.commit()

    return {"deleted_count": updated_count}