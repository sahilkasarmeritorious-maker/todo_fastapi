from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from todo_app.database import get_db
from todo_app.auth import get_current_user
from todo_app import crud, schemas, models

router = APIRouter(prefix="/todos", tags=["Todos"])


@router.get("/", response_model=schemas.APIListResponse)
async def get_all_todos(
    db: AsyncSession = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    todos = await crud.get_all_todos(db, user_id=current_user.id)
    return {
        "success": True,
        "message": "Todos fetched successfully",
        "data": todos,
        "total": len(todos)
    }


@router.get("/{todo_id}", response_model=schemas.APIResponse)
async def get_todo(
    todo_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    todo = await crud.get_todo_by_id(db, todo_id, user_id=current_user.id)
    if todo is None:
        raise HTTPException(status_code=404, detail="Todo not found")
    return {"success": True, "message": "Todo fetched", "data": todo}


@router.post("/", response_model=schemas.APIResponse, status_code=201)
async def create_todo(
    todo: schemas.TodoCreate,
    db: AsyncSession = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    new_todo = await crud.create_todo(db, todo, user_id=current_user.id)
    return {"success": True, "message": "Todo created successfully", "data": new_todo}


@router.put("/{todo_id}", response_model=schemas.APIResponse)
async def update_todo(
    todo_id: int,
    todo: schemas.TodoUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    updated = await crud.update_todo(db, todo_id, todo, user_id=current_user.id)
    if updated is None:
        raise HTTPException(status_code=404, detail="Todo not found")
    return {"success": True, "message": "Todo updated successfully", "data": updated}


@router.patch("/{todo_id}", response_model=schemas.APIResponse)
async def patch_todo(
    todo_id: int,
    todo: schemas.TodoPatch,
    db: AsyncSession = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    patched = await crud.patch_todo(db, todo_id, todo, user_id=current_user.id)
    if patched is None:
        raise HTTPException(status_code=404, detail="Todo not found")
    return {"success": True, "message": "Todo patched successfully", "data": patched}


@router.delete("/{todo_id}")
async def delete_todo(
    todo_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    deleted = await crud.soft_delete_todo(db, todo_id, user_id=current_user.id)
    if deleted is None:
        raise HTTPException(status_code=404, detail="Todo not found")
    return {"success": True, "message": "Todo deleted", "data": None}