from sqlalchemy import Column, Integer, String, DateTime, Boolean
from sqlalchemy.sql import func
from todo_app.database import Base

class Todo(Base):
    __tablename__ = "todos_new"

    id          = Column(Integer, primary_key=True, index=True)
    title       = Column(String, nullable=False)
    description = Column(String, nullable=True)
    status      = Column(String, default="pending")   # pending | in_progress | done
    created_at  = Column(DateTime(timezone=True), server_default=func.now())
    updated_at  = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    deleted_at  = Column(DateTime(timezone=True), nullable=True, default=None)  # NULL = active