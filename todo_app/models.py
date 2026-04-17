from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, Enum
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from todo_app.database import Base
import enum


# --- Enums ---
# fixed choice fields — only these values allowed in DB
class TaskStatus(str, enum.Enum):
    pending     = "pending"
    in_progress = "in_progress"
    completed   = "completed"
    cancelled   = "cancelled"

class TaskPriority(str, enum.Enum):
    low    = "low"
    medium = "medium"
    high   = "high"

# --- User ---
class User(Base):
    __tablename__ = "users"

    id         = Column(Integer, primary_key=True, index=True)
    username   = Column(String, unique=True, nullable=False, index=True)
    email      = Column(String, unique=True, nullable=False, index=True)
    password   = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # relationships
    employees = relationship("Employee", back_populates="created_by_user")
    tasks     = relationship("Task", back_populates="created_by_user")


# --- Employee ---
class Employee(Base):
    __tablename__ = "employees"

    id         = Column(Integer, primary_key=True, index=True)
    name       = Column(String, nullable=False)
    email      = Column(String, unique=True, nullable=False, index=True)
    department = Column(String, nullable=True)
    position   = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    deleted_at = Column(DateTime(timezone=True), nullable=True, default=None)

    created_by = Column(Integer, ForeignKey("users.id"), nullable=False)

    # relationships
    created_by_user = relationship("User", back_populates="employees")
    tasks           = relationship("Task", back_populates="assigned_employee")


# --- Task ---
class Task(Base):
    __tablename__ = "tasks"

    id          = Column(Integer, primary_key=True, index=True)
    title       = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    status      = Column(Enum(TaskStatus),   default=TaskStatus.pending,  nullable=False)
    priority    = Column(Enum(TaskPriority), default=TaskPriority.medium, nullable=False)
    deadline    = Column(DateTime(timezone=True), nullable=True)
    created_at  = Column(DateTime(timezone=True), server_default=func.now())
    updated_at  = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    deleted_at  = Column(DateTime(timezone=True), nullable=True, default=None)

    # which employee is assigned
    employee_id = Column(Integer, ForeignKey("employees.id"), nullable=False)
    # who created the task
    created_by  = Column(Integer, ForeignKey("users.id"), nullable=False)

    # relationships
    assigned_employee = relationship("Employee", back_populates="tasks")
    created_by_user   = relationship("User", back_populates="tasks")