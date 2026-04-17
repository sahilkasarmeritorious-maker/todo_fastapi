from fastapi import APIRouter, Depends, HTTPException, Request, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from todo_app.database import get_db
from todo_app.auth import get_current_user
from todo_app import crud, schemas, models
from todo_app.limiter import limiter
from todo_app.background_task import (
    send_task_assigned_email,
    send_task_completed_email,
    send_deadline_reminder_email
)

router = APIRouter(prefix="/tasks", tags=["Tasks"])


@router.get("/", response_model=schemas.TaskListResponse)
@limiter.limit("30/minute")
async def get_all_tasks(
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    tasks = await crud.get_all_tasks(db, user_id=current_user.id)
    return {
        "success": True,
        "message": "Tasks fetched successfully",
        "data": tasks,
        "total": len(tasks)
    }


@router.get("/employee/{employee_id}", response_model=schemas.TaskListResponse)
@limiter.limit("30/minute")
async def get_tasks_by_employee(
    request: Request,
    employee_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    tasks = await crud.get_tasks_by_employee(db, employee_id, user_id=current_user.id)
    return {
        "success": True,
        "message": f"Tasks for employee {employee_id} fetched",
        "data": tasks,
        "total": len(tasks)
    }


@router.get("/{task_id}", response_model=schemas.TaskAPIResponse)
@limiter.limit("30/minute")
async def get_task(
    request: Request,
    task_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    task = await crud.get_task_by_id(db, task_id, user_id=current_user.id)
    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    return {
        "success": True,
        "message": "Task fetched successfully",
        "data": task
    }


@router.post("/", response_model=schemas.TaskAPIResponse, status_code=201)
@limiter.limit("20/minute")
async def create_task(
    request: Request,
    task: schemas.TaskCreate,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    # check employee exists
    employee = await crud.get_employee_by_id(db, task.employee_id, user_id=current_user.id)
    if employee is None:
        raise HTTPException(
            status_code=404,
            detail="Employee not found. Create the employee first."
        )

    new_task = await crud.create_task(db, task, user_id=current_user.id)

    # ✅ Extract plain Python values NOW, while the session is still open
    # SQLAlchemy ORM objects cannot be accessed inside background tasks
    # because the DB session will be closed by then
    employee_name  = employee.name
    employee_email = employee.email
    task_title     = new_task.title
    task_description = new_task.description
    task_priority  = new_task.priority.value if hasattr(new_task.priority, "value") else str(new_task.priority)
    deadline_str   = (
        task.deadline.strftime("%Y-%m-%d %H:%M UTC")
        if task.deadline else "No deadline set"
    )

    # send email in background — API responds instantly
    background_tasks.add_task(
        send_task_assigned_email,
        employee_name,
        employee_email,
        task_title,
        task_description or "No description provided",
        task_priority,
        deadline_str
    )

    return {
        "success": True,
        "message": "Task created successfully",
        "data": new_task
    }


@router.put("/{task_id}", response_model=schemas.TaskAPIResponse)
@limiter.limit("20/minute")
async def update_task(
    request: Request,
    task_id: int,
    task: schemas.TaskUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    updated = await crud.update_task(db, task_id, task, user_id=current_user.id)
    if updated is None:
        raise HTTPException(status_code=404, detail="Task not found")
    return {
        "success": True,
        "message": "Task updated successfully",
        "data": updated
    }


@router.patch("/{task_id}", response_model=schemas.TaskAPIResponse)
@limiter.limit("20/minute")
async def patch_task(
    request: Request,
    task_id: int,
    task: schemas.TaskPatch,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    existing_task = await crud.get_task_by_id(db, task_id, user_id=current_user.id)
    if existing_task is None:
        raise HTTPException(status_code=404, detail="Task not found")

    employee = await crud.get_employee_by_id(
        db, existing_task.employee_id, user_id=current_user.id
    )

    patched = await crud.patch_task(db, task_id, task, user_id=current_user.id)

    # ✅ Extract plain values before the session closes
    if employee:
        employee_name  = employee.name
        employee_email = employee.email
        task_title     = patched.title

        if task.status == "completed":
            background_tasks.add_task(
                send_task_completed_email,
                employee_name,
                employee_email,
                task_title
            )

        if task.deadline:
            deadline_str = task.deadline.strftime("%Y-%m-%d %H:%M UTC")
            background_tasks.add_task(
                send_deadline_reminder_email,
                employee_name,
                employee_email,
                task_title,
                deadline_str
            )

    return {
        "success": True,
        "message": "Task patched successfully",
        "data": patched
    }


@router.delete("/{task_id}")
@limiter.limit("20/minute")
async def delete_task(
    request: Request,
    task_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    deleted = await crud.soft_delete_task(db, task_id, user_id=current_user.id)
    if deleted is None:
        raise HTTPException(status_code=404, detail="Task not found")
    return {
        "success": True,
        "message": "Task deleted successfully",
        "data": None
    }