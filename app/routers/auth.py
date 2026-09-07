from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.dependencies import get_db
from app.models.user import User
from app.schema import UserCreate, UserResponse, UserLogin

from app.security import (
    hash_password,
    verify_password,
    create_access_token,
)

router = APIRouter(
    prefix="/auth",
    tags=["Authentication"]
)


@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED
)
async def register_user(
    user: UserCreate,
    db: AsyncSession = Depends(get_db)
):
    # 1. Check whether the username already exists.
    statement = select(User).where(User.username == user.username)

    result = await db.execute(statement)

    existing_user = result.scalar_one_or_none()

    # 2. Duplicate username should not be allowed.
    if existing_user is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Username already exists"
        ) 

    # 3. Convert the plain password into a secure hash.
    hashed_password = hash_password(user.password)

    # 4. Create the SQLAlchemy User object.
    new_user = User(
        username=user.username,
        hashed_password=hashed_password,
        status="Active"
    )

    # 5. Add the new user to the current database session.
    db.add(new_user)

    # 6. Save the transaction in PostgreSQL.
    await db.commit()

    # 7. Get database-generated values such as id.
    await db.refresh(new_user)

    # 8. UserResponse prevents hashed_password from being returned.
    return new_user

@router.post("/login")
async def login_user(
    user: UserLogin,
    db: AsyncSession = Depends(get_db)
):
    # Database mein username se user find karo
    statement = select(User).where(User.username == user.username)

    result = await db.execute(statement)

    existing_user = result.scalar_one_or_none()

    # User nahi mila
    if existing_user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password"
        )

    # Entered password ko stored Argon2 hash ke against verify karo
    password_is_valid = verify_password(
        user.password,
        existing_user.hashed_password
    )

    # Password incorrect
    if not password_is_valid:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password"
        )

    # Authentication successful → JWT create karo
    access_token = create_access_token(
        data={
            "sub": str(existing_user.id)
        }
    )

    # Client ko JWT return karo
    return {
        "access_token": access_token,
        "token_type": "bearer"
    }