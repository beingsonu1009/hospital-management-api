"""
Authentication router.

Is file mein:
- User registration
- Password hashing
- User login
- JWT token generation

handle kiya gaya hai.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.dependencies import get_db
from app.models.user import User
from app.schema import UserCreate, UserLogin, UserResponse
from app.security import (
    create_access_token,
    hash_password,
    verify_password,
)


router = APIRouter(
    prefix="/auth",
    tags=["Authentication"],
)


# =========================================================
# REGISTER
# =========================================================

@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
)
async def register_user(
    user: UserCreate,
    db: AsyncSession = Depends(get_db),
):
    """
    New user create karta hai.

    Password ko plain text mein database mein store nahi karte.
    Pehle password hash hota hai, phir hashed_password column
    mein save hota hai.
    """

    # Check karo username already exist karta hai ya nahi
    statement = select(User).where(
        User.username == user.username
    )

    result = await db.execute(statement)

    existing_user = result.scalar_one_or_none()

    if existing_user is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Username already exists",
        )

    # Plain password ko hash karo
    hashed_password = hash_password(user.password)

    # Database model ke exact column names use karo
    new_user = User(
        username=user.username,
        hashed_password=hashed_password,
        status="active",
    )

    db.add(new_user)

    await db.commit()

    await db.refresh(new_user)

    return new_user


# =========================================================
# LOGIN
# =========================================================

@router.post("/login")
async def login_user(
    user: UserLogin,
    db: AsyncSession = Depends(get_db),
):
    """
    Username + password verify karke JWT token return karta hai.
    """

    # Username se user find karo
    statement = select(User).where(
        User.username == user.username
    )

    result = await db.execute(statement)

    existing_user = result.scalar_one_or_none()

    # User exist nahi karta
    if existing_user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password",
        )

    # Database se hashed_password lekar
    # entered plain password ko verify karo
    password_is_valid = verify_password(
        user.password,
        existing_user.hashed_password,
    )

    if not password_is_valid:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password",
        )

    # JWT token create karo
    access_token = create_access_token(
        data={
            "sub": str(existing_user.id),
        }
    )

    return {
        "access_token": access_token,
        "token_type": "bearer",
    }