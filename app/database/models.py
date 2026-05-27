from sqlalchemy import Boolean, Column, ForeignKey, Integer, String,Index
from sqlalchemy.orm import relationship

from app.database.base import Base


class Task(Base):
    __tablename__ = "tasks"
    id = Column(Integer, primary_key=True)
    title = Column(String)
    description = Column(String)
    completed = Column(Boolean, default=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    user = relationship("User", back_populates="tasks")
    priority = Column(Integer, default=1)

    __table_args__ = (
        Index(
            "ix_tasks_user_id_completed_priority",
            "user_id",
            "completed",
            "priority",
        ),
    )


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    username = Column(String, unique=True, nullable=False)
    email = Column(String, unique=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    tasks = relationship("Task", back_populates="user")
