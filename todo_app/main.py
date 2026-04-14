from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from todo_app.database import Base, engine
from todo_app import models
from todo_app.routers import auth as auth_router
from todo_app.routers import todo as todos_router
from todo_app.middleware import LoggingMiddleware, ErrorHandlingMiddleware
from todo_app.limiter import limiter

app = FastAPI(title="Todo App")

# --- attach limiter to app ---
# slowapi needs this to work
app.state.limiter = limiter

# --- add rate limit exceeded handler ---
# when someone hits the limit this returns a clean 429 response
# instead of an ugly crash
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
app.include_router(todos_router.router)


@app.get("/")
def root():
    return {"message": "Todo API is running"}