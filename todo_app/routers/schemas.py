from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class TodoCreate(BaseModel):
    title: str
    description: Optional[str] = None

class TodoUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = None

class TodoPatch(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = None

class TodoOut(BaseModel):
    id: int
    title: str
    description: Optional[str]
    status: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class APIResponse(BaseModel):
    success: bool
    message: str
    data: Optional[TodoOut] = None

class APIListResponse(BaseModel):
    success: bool
    message: str
    data: list[TodoOut] = []
    total: int = 0