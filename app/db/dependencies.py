"""
Database dependencies.

Is file ka kaam:
- FastAPI endpoints ko database session provide karna.
- Request complete hone ke baad session automatically close karna.
"""

from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import SessionLocal


# ---------------------------------------------------------
# Database Session Dependency
# ---------------------------------------------------------

async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    FastAPI ke endpoints ko ek AsyncSession provide karta hai.

    Endpoint mein:
        db: AsyncSession = Depends(get_db)

    use karne par ye function session create karega.
    Request complete hone ke baad session automatically close ho jayega.
    """

    async with SessionLocal() as session:
        yield session