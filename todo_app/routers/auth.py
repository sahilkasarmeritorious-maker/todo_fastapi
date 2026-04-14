from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from todo_app.database import get_db
from todo_app import schemas, models, auth
from todo_app.limiter import limiter

router = APIRouter(prefix="/auth", tags=["Auth"])


# 5 requests per minute on register
# stops bots creating thousands of fake accounts
@router.post("/register")
@limiter.limit("5/minute")
async def register(
    request: Request,   # Request must be first param for slowapi to work
    body: schemas.RegisterRequest,
    db: AsyncSession = Depends(get_db)
):
    existing_user = await auth.get_user_by_username(db, body.username)
    if existing_user:
        raise HTTPException(
            status_code=400,
            detail="Username already taken"
        )

    hashed = auth.hash_password(body.password)
    new_user = models.User(
        username=body.username,
        password=hashed
    )
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)

    return {
        "success": True,
        "message": "User registered successfully",
        "data": {"username": new_user.username}
    }


# 10 requests per minute on login
# stops brute force password attacks
@router.post("/login", response_model=schemas.TokenResponse)
@limiter.limit("10/minute")
async def login(
    request: Request,   # ← Request must be first param
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_db)
):
    user = await auth.get_user_by_username(db, form_data.username)

    if not user or not auth.verify_password(form_data.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Wrong username or password"
        )

    token = auth.create_access_token(data={"sub": user.username})

    return {
        "access_token": token,
        "token_type": "bearer",
        "expires_in": "15 minutes"
    }