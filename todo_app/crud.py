from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import func
from todo_app import models, schemas


# ─── Employee CRUD ────────────────────────────────────────

async def get_all_employees(db: AsyncSession, user_id: int):
    result = await db.execute(
        select(models.Employee).where(
            models.Employee.deleted_at == None,
            models.Employee.created_by == user_id
        )
    )
    return result.scalars().all()


async def get_employee_by_id(db: AsyncSession, employee_id: int, user_id: int):
    result = await db.execute(
        select(models.Employee).where(
            models.Employee.id         == employee_id,
            models.Employee.deleted_at == None,
            models.Employee.created_by == user_id
        )
    )
    return result.scalars().first()


async def create_employee(db: AsyncSession, employee: schemas.EmployeeCreate, user_id: int):
    new_employee = models.Employee(
        name=employee.name,
        email=employee.email,
        department=employee.department,
        position=employee.position,
        created_by=user_id
    )
    db.add(new_employee)
    await db.commit()
    await db.refresh(new_employee)
    return new_employee


async def update_employee(db: AsyncSession, employee_id: int, employee: schemas.EmployeeUpdate, user_id: int):
    db_employee = await get_employee_by_id(db, employee_id, user_id)
    if db_employee is None:
        return None
    update_data = employee.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_employee, key, value)
    await db.commit()
    await db.refresh(db_employee)
    return db_employee


async def patch_employee(db: AsyncSession, employee_id: int, employee: schemas.EmployeePatch, user_id: int):
    db_employee = await get_employee_by_id(db, employee_id, user_id)
    if db_employee is None:
        return None
    update_data = employee.model_dump(exclude_unset=True)
    if not update_data:
        return db_employee
    for key, value in update_data.items():
        setattr(db_employee, key, value)
    await db.commit()
    await db.refresh(db_employee)
    return db_employee


async def soft_delete_employee(db: AsyncSession, employee_id: int, user_id: int):
    db_employee = await get_employee_by_id(db, employee_id, user_id)
    if db_employee is None:
        return None
    db_employee.deleted_at = func.now()
    await db.commit()
    return db_employee


# ─── Task CRUD ────────────────────────────────────────────

async def get_all_tasks(db: AsyncSession, user_id: int):
    result = await db.execute(
        select(models.Task).where(
            models.Task.deleted_at == None,
            models.Task.created_by == user_id
        )
    )
    return result.scalars().all()


async def get_task_by_id(db: AsyncSession, task_id: int, user_id: int):
    result = await db.execute(
        select(models.Task).where(
            models.Task.id         == task_id,
            models.Task.deleted_at == None,
            models.Task.created_by == user_id
        )
    )
    return result.scalars().first()


async def get_tasks_by_employee(db: AsyncSession, employee_id: int, user_id: int):
    result = await db.execute(
        select(models.Task).where(
            models.Task.employee_id == employee_id,
            models.Task.deleted_at  == None,
            models.Task.created_by  == user_id
        )
    )
    return result.scalars().all()


async def create_task(db: AsyncSession, task: schemas.TaskCreate, user_id: int):
    new_task = models.Task(
        title=task.title,
        description=task.description,
        priority=task.priority,
        deadline=task.deadline,
        employee_id=task.employee_id,
        created_by=user_id
    )
    db.add(new_task)
    await db.commit()
    await db.refresh(new_task)
    return new_task


async def update_task(db: AsyncSession, task_id: int, task: schemas.TaskUpdate, user_id: int):
    db_task = await get_task_by_id(db, task_id, user_id)
    if db_task is None:
        return None
    update_data = task.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_task, key, value)
    await db.commit()
    await db.refresh(db_task)
    return db_task


async def patch_task(db: AsyncSession, task_id: int, task: schemas.TaskPatch, user_id: int):
    db_task = await get_task_by_id(db, task_id, user_id)
    if db_task is None:
        return None
    update_data = task.model_dump(exclude_unset=True)
    if not update_data:
        return db_task
    for key, value in update_data.items():
        setattr(db_task, key, value)
    await db.commit()
    await db.refresh(db_task)
    return db_task


async def soft_delete_task(db: AsyncSession, task_id: int, user_id: int):
    db_task = await get_task_by_id(db, task_id, user_id)
    if db_task is None:
        return None
    db_task.deleted_at = func.now()
    await db.commit()
    return db_task