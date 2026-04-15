from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


# ─── Auth ─────────────────────────────────────────────────

class RegisterRequest(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    password: str = Field(..., min_length=6)

class LoginRequest(BaseModel):
    username: str
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str   = "bearer"
    expires_in: str   = "15 minutes"

class RefreshTokenRequest(BaseModel):
    refresh_token: str

class TokenResponseWithRefresh(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: str = "15 minutes"

# ─── Employee ─────────────────────────────────────────────

class EmployeeCreate(BaseModel):
    name:       str           = Field(..., min_length=2, max_length=100)
    email:      str           = Field(...)
    department: Optional[str] = None
    position:   Optional[str] = None

class EmployeeUpdate(BaseModel):
    name:       Optional[str] = None
    email:      Optional[str] = None
    department: Optional[str] = None
    position:   Optional[str] = None

class EmployeePatch(BaseModel):
    name:       Optional[str] = None
    email:      Optional[str] = None
    department: Optional[str] = None
    position:   Optional[str] = None

class EmployeeOut(BaseModel):
    id:         int
    name:       str
    email:      str
    department: Optional[str]
    position:   Optional[str]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class EmployeeAPIResponse(BaseModel):
    success: bool
    message: str
    data:    Optional[EmployeeOut] = None

class EmployeeListResponse(BaseModel):
    success: bool
    message: str
    data:    list[EmployeeOut] = []
    total:   int = 0


# ─── Task ─────────────────────────────────────────────────

class TaskCreate(BaseModel):
    title:       str                = Field(..., min_length=1, max_length=200)
    description: Optional[str]      = None
    priority:    Optional[str]      = "medium"
    deadline:    Optional[datetime] = None
    employee_id: int

class TaskUpdate(BaseModel):
    title:       Optional[str]      = None
    description: Optional[str]      = None
    status:      Optional[str]      = None
    priority:    Optional[str]      = None
    deadline:    Optional[datetime] = None
    employee_id: Optional[int]      = None

class TaskPatch(BaseModel):
    title:       Optional[str]      = None
    description: Optional[str]      = None
    status:      Optional[str]      = None
    priority:    Optional[str]      = None
    deadline:    Optional[datetime] = None
    employee_id: Optional[int]      = None

class TaskOut(BaseModel):
    id:          int
    title:       str
    description: Optional[str]
    status:      str
    priority:    str
    deadline:    Optional[datetime]
    employee_id: int
    created_at:  datetime
    updated_at:  datetime

    class Config:
        from_attributes = True

class TaskAPIResponse(BaseModel):
    success: bool
    message: str
    data:    Optional[TaskOut] = None

class TaskListResponse(BaseModel):
    success: bool
    message: str
    data:    list[TaskOut] = []
    total:   int = 0