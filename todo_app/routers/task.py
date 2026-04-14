from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession
from todo_app.database import get_db
from todo_app.auth import get_current_user
from todo_app import crud, schemas, models
from todo_app.limiter import limiter

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
    db: AsyncSession = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    employee = await crud.get_employee_by_id(db, task.employee_id, user_id=current_user.id)
    if employee is None:
        raise HTTPException(
            status_code=404,
            detail="Employee not found. Create the employee first."
        )

    new_task = await crud.create_task(db, task, user_id=current_user.id)

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
    db: AsyncSession = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    patched = await crud.patch_task(db, task_id, task, user_id=current_user.id)
    if patched is None:
        raise HTTPException(status_code=404, detail="Task not found")

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