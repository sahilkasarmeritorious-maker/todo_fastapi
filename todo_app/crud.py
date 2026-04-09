from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import func
from todo_app import models, schemas


async def get_all_todos(db: AsyncSession):
    result = await db.execute(
        select(models.Todo).where(models.Todo.deleted_at == None)
    )
    return result.scalars().all()


async def get_todo_by_id(db: AsyncSession, todo_id: int):
    result = await db.execute(
        select(models.Todo).where(
            models.Todo.id == todo_id,
            models.Todo.deleted_at == None
        )
    )
    return result.scalars().first()


async def create_todo(db: AsyncSession, todo: schemas.TodoCreate):
    new_todo = models.Todo(
        title=todo.title,
        description=todo.description
    )
    db.add(new_todo)
    await db.commit()
    await db.refresh(new_todo)
    return new_todo


async def update_todo(db: AsyncSession, todo_id: int, todo: schemas.TodoUpdate):
    db_todo = await get_todo_by_id(db, todo_id)
    if db_todo is None:
        return None
    update_data = todo.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_todo, key, value)
    await db.commit()
    await db.refresh(db_todo)
    return db_todo


async def patch_todo(db: AsyncSession, todo_id: int, todo: schemas.TodoPatch):
    db_todo = await get_todo_by_id(db, todo_id)
    if db_todo is None:
        return None

    update_data = todo.model_dump(exclude_unset=True)


    if not update_data:
        return db_todo

    for key, value in update_data.items():
        setattr(db_todo, key, value)

    await db.commit()
    await db.refresh(db_todo)
    return db_todo


async def soft_delete_todo(db: AsyncSession, todo_id: int):
    db_todo = await get_todo_by_id(db, todo_id)
    if db_todo is None:
        return None
    db_todo.deleted_at = func.now()
    await db.commit()
    return db_todo