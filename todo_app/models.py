from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from todo_app.database import Base

class User(Base):
    __tablename__ = "users"

    id         = Column(Integer, primary_key=True, index=True)
    username   = Column(String, unique=True, nullable=False, index=True)
    password   = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    todos = relationship("Todo", back_populates="owner")


class Todo(Base):
    __tablename__ = "todos"

    id          = Column(Integer, primary_key=True, index=True)
    title       = Column(String, nullable=False)
    description = Column(String, nullable=True)
    status      = Column(String, default="pending")
    created_at  = Column(DateTime(timezone=True), server_default=func.now())
    updated_at  = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    deleted_at  = Column(DateTime(timezone=True), nullable=True, default=None)

    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    owner   = relationship("User", back_populates="todos")