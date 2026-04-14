from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession
from todo_app.database import get_db
from todo_app.auth import get_current_user
from todo_app import crud, schemas, models
from todo_app.limiter import limiter

router = APIRouter(prefix="/employees", tags=["Employees"])


@router.get("/", response_model=schemas.EmployeeListResponse)
@limiter.limit("30/minute")
async def get_all_employees(
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    employees = await crud.get_all_employees(db, user_id=current_user.id)
    return {
        "success": True,
        "message": "Employees fetched successfully",
        "data": employees,
        "total": len(employees)
    }


@router.get("/{employee_id}", response_model=schemas.EmployeeAPIResponse)
@limiter.limit("30/minute")
async def get_employee(
    request: Request,
    employee_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    employee = await crud.get_employee_by_id(db, employee_id, user_id=current_user.id)
    if employee is None:
        raise HTTPException(status_code=404, detail="Employee not found")
    return {
        "success": True,
        "message": "Employee fetched successfully",
        "data": employee
    }


@router.post("/", response_model=schemas.EmployeeAPIResponse, status_code=201)
@limiter.limit("20/minute")
async def create_employee(
    request: Request,
    employee: schemas.EmployeeCreate,
    db: AsyncSession = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    new_employee = await crud.create_employee(db, employee, user_id=current_user.id)
    return {
        "success": True,
        "message": "Employee created successfully",
        "data": new_employee
    }


@router.put("/{employee_id}", response_model=schemas.EmployeeAPIResponse)
@limiter.limit("20/minute")
async def update_employee(
    request: Request,
    employee_id: int,
    employee: schemas.EmployeeUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    updated = await crud.update_employee(db, employee_id, employee, user_id=current_user.id)
    if updated is None:
        raise HTTPException(status_code=404, detail="Employee not found")
    return {
        "success": True,
        "message": "Employee updated successfully",
        "data": updated
    }


@router.patch("/{employee_id}", response_model=schemas.EmployeeAPIResponse)
@limiter.limit("20/minute")
async def patch_employee(
    request: Request,
    employee_id: int,
    employee: schemas.EmployeePatch,
    db: AsyncSession = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    patched = await crud.patch_employee(db, employee_id, employee, user_id=current_user.id)
    if patched is None:
        raise HTTPException(status_code=404, detail="Employee not found")
    return {
        "success": True,
        "message": "Employee patched successfully",
        "data": patched
    }


@router.delete("/{employee_id}")
@limiter.limit("20/minute")
async def delete_employee(
    request: Request,
    employee_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    deleted = await crud.soft_delete_employee(db, employee_id, user_id=current_user.id)
    if deleted is None:
        raise HTTPException(status_code=404, detail="Employee not found")
    return {
        "success": True,
        "message": "Employee deleted successfully",
        "data": None
    }