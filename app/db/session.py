"""
Database session configuration.

Is file ka main kaam:
1. .env se DATABASE_URL read karna.
2. PostgreSQL ke liye Async SQLAlchemy engine banana.
3. Async database sessions create karne ke liye SessionLocal banana.
"""


# ---------------------------------------------------------
# Imports
# ---------------------------------------------------------

import os

from dotenv import load_dotenv
from sqlalchemy import text
from sqlalchemy.ext.asyncio import (
    create_async_engine,
    async_sessionmaker,
)


# ---------------------------------------------------------
# Environment Variables
# ---------------------------------------------------------

# .env file ke variables ko environment mein load karta hai.
load_dotenv()


# PostgreSQL connection URL .env se read kar rahe hain.
#
# Example:
# DATABASE_URL=postgresql+asyncpg://username:password@127.0.0.1:5432/hospital_db
#
# Is URL ke through SQLAlchemy ko pata chalega:
# - kaunsa database use karna hai
# - database kis host par hai
# - kaunsa driver use karna hai
DATABASE_URL = os.getenv("DATABASE_URL")


# Agar DATABASE_URL missing hai to application startup par
# clear error milega instead of confusing database error.
if not DATABASE_URL:
    raise RuntimeError(
        "DATABASE_URL is not configured in the .env file."
    )


# ---------------------------------------------------------
# Async Database Engine
# ---------------------------------------------------------

# Engine database ke saath actual connections manage karta hai.
#
# create_async_engine() use kar rahe hain kyunki hamara
# FastAPI + SQLAlchemy setup asynchronous hai.
engine = create_async_engine(
    DATABASE_URL,
)


# ---------------------------------------------------------
# Async Session Factory
# ---------------------------------------------------------

# SessionLocal ek factory hai.
#
# Jab bhi kisi API endpoint ko database ke saath kaam karna hoga,
# get_db() isi factory se ek AsyncSession create karega.
SessionLocal = async_sessionmaker(
    bind=engine,

    # Commit ke baad SQLAlchemy objects ko automatically expire
    # nahi karega.
    #
    # Isse commit ke baad object ke attributes ko safely access
    # karna easier hota hai.
    expire_on_commit=False,
)


# ---------------------------------------------------------
# Database Connection Test
# ---------------------------------------------------------

async def test_session():
    """
    Database connection test karne ke liye helper function.

    SELECT 1 ek simple SQL query hai.
    Agar database connection successful hai,
    to result 1 return karega.
    """

    async with SessionLocal() as session:

        # Database ko simple test query bhej rahe hain.
        result = await session.execute(
            text("SELECT 1")
        )

        # Query ka result terminal mein print hoga.
        print("Database connection test:", result.scalar())