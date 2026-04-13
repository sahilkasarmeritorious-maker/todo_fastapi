from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm  # ← add this
from sqlalchemy.ext.asyncio import AsyncSession
from todo_app.database import get_db
from todo_app import schemas, models, auth

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/register")
async def register(request: schemas.RegisterRequest, db: AsyncSession = Depends(get_db)):
    existing_user = await auth.get_user_by_username(db, request.username)
    if existing_user:
        raise HTTPException(
            status_code=400,
            detail="Username already taken"
        )
    hashed = auth.hash_password(request.password)
    new_user = models.User(
        username=request.username,
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


@router.post("/login", response_model=schemas.TokenResponse)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),  # ← changed this
    db: AsyncSession = Depends(get_db)
):
    user = await auth.get_user_by_username(db, form_data.username)  # ← form_data not request

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