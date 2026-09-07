import asyncio

from app.db.base import Base
from app.db.session import engine

# IMPORTANT:
# Models ko import karna zaroori hai taaki SQLAlchemy
# unhe Base.metadata mein register kare.
from app.models.patient import Patient
from app.models.doctor import Doctor
from app.models.appointment import Appointment
from app.models.user import User


async def create_tables():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    print("Tables created successfully!")


if __name__ == "__main__":
    asyncio.run(create_tables())