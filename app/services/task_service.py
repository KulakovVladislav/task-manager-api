from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.database.models import Task, User
from app.schemas import TaskCreate


def find_task(task_id: int, db: Session, current_user: User):
    db_task = db.query(Task).filter(Task.id == task_id, Task.user_id == current_user.id).first()
    if not db_task:
        raise HTTPException(status_code=404, detail="Task not found")
    return db_task


def get_tasks(db: Session, current_user: User):
    db_tasks = db.query(Task).filter(Task.user_id == current_user.id).all()
    return db_tasks


def create_task(item: TaskCreate, db: Session, current_user: User):
    db_task = Task(
        title=item.title,
        description=item.description,
        user_id=current_user.id,
        completed=False,
        priority=item.priority,
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
    db.delete(db_task)
    db.commit()
    return db_task


def task_count(db: Session, current_user: User):
    count = db.query(Task).filter(Task.user_id == current_user.id).count()
    return count


def task_last(db: Session, current_user: User):
    db_tasks = db.query(Task).filter(Task.user_id == current_user.id).order_by(Task.id.desc()).first()
    if not db_tasks:
        raise HTTPException(status_code=404, detail="Task not found")
    return db_tasks


def delete_tasks(db: Session, current_user: User):
    db_tasks = db.query(Task).filter(Task.user_id == current_user.id).all()
    if not db_tasks:
        raise HTTPException(status_code=404, detail="Task not found")
    db.query(Task).filter(Task.user_id == current_user.id).delete()
    db.commit()
    return db_tasks
