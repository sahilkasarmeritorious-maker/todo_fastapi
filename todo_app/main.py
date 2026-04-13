from fastapi import FastAPI
from todo_app.database import Base, engine
from todo_app import models  # ← this is critical — registers both User and Todo with Base
from todo_app.routers import auth as auth_router
from todo_app.routers import todo as todos_router

app = FastAPI(title="Todo App")


async def create_tables():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


@app.on_event("startup")
async def startup():
    await create_tables()


app.include_router(auth_router.router)
app.include_router(todos_router.router)


@app.get("/")
def root():
    return {"message": "Todo API is running"}