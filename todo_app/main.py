from fastapi import FastAPI
from todo_app.database import Base, engine
from todo_app.routers import todo
from sqlalchemy.ext.asyncio import AsyncEngine

app = FastAPI(title="Todo App")

async def create_tables():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

@app.on_event("startup")
async def startup():
    await create_tables()

app.include_router(todo.router)

@app.get("/")
def root():
    return {"message": "Todo API is running"}