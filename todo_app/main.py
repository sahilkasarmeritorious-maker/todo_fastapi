from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from todo_app.database import Base, engine
from todo_app import models
from todo_app.routers import auth as auth_router
from todo_app.routers import employees as employees_router
from todo_app.routers import task as tasks_router
from todo_app.middleware import LoggingMiddleware, ErrorHandlingMiddleware
from todo_app.limiter import limiter

app = FastAPI(title="Task Management System")

# --- Rate limiter ---
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# --- Middlewares ---
app.add_middleware(ErrorHandlingMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(LoggingMiddleware)


async def create_tables():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

@app.on_event("startup")
async def startup():
    await create_tables()


app.include_router(auth_router.router)
app.include_router(employees_router.router)
app.include_router(tasks_router.router)


@app.get("/")
def root():
    return {"message": "Task Management System is running successfully!"}