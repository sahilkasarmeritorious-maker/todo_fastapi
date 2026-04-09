from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from todo_app import crud, schemas
from todo_app.database import get_db

router = APIRouter(prefix="/todos", tags=["Todos"])


@router.get("/", response_model=schemas.APIListResponse)
async def get_all_todos(db: AsyncSession = Depends(get_db)):
    todos = await crud.get_all_todos(db)
    return {
        "success": True,
        "message": "Todos fetched successfully",
        "data": todos,
        "total": len(todos)
    }


@router.get("/{todo_id}", response_model=schemas.APIResponse)
async def get_todo(todo_id: int, db: AsyncSession = Depends(get_db)):
    todo = await crud.get_todo_by_id(db, todo_id)
    if todo is None:
        raise HTTPException(status_code=404, detail="Todo not found")
    return {
        "success": True,
        "message": "Todo fetched successfully",
        "data": todo
    }


@router.post("/", response_model=schemas.APIResponse, status_code=201)
async def create_todo(todo: schemas.TodoCreate, db: AsyncSession = Depends(get_db)):
    new_todo = await crud.create_todo(db, todo)
    return {
        "success": True,
        "message": "Todo created successfully",
        "data": new_todo
    }


@router.put("/{todo_id}", response_model=schemas.APIResponse)
async def update_todo(todo_id: int, todo: schemas.TodoUpdate, db: AsyncSession = Depends(get_db)):
    updated = await crud.update_todo(db, todo_id, todo)
    if updated is None:
        raise HTTPException(status_code=404, detail="Todo not found")
    return {
        "success": True,
        "message": "Todo updated successfully",
        "data": updated
    }


@router.patch("/{todo_id}", response_model=schemas.APIResponse)
async def patch_update_todo(todo_id: int, todo: schemas.TodoPatch, db: AsyncSession = Depends(get_db)):
    patched = await crud.patch_todo(db, todo_id, todo)
    if patched is None:
        raise HTTPException(status_code=404, detail="Todo not found")
    return {
        "success": True,
        "message": "Todo patched successfully",
        "data": patched
    }


@router.delete("/{todo_id}")
async def delete_todo(todo_id: int, db: AsyncSession = Depends(get_db)):
    deleted = await crud.soft_delete_todo(db, todo_id)
    if deleted is None:
        raise HTTPException(status_code=404, detail="Todo not found")
    return {
        "success": True,
        "message": "Todo deleted successfully",
        "data": None
    }